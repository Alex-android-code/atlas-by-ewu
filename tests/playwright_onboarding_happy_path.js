const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

const baseUrl = process.env.ATLAS_BASE_URL || "http://127.0.0.1:8018";
const photoPath = process.env.ATLAS_E2E_PHOTO || path.resolve(".tmp-onboarding-check/happy-avatar.png");
const cvPath = process.env.ATLAS_E2E_CV || path.resolve(".tmp-onboarding-check/happy-cv.rtf");

async function next(page) {
  await page.click("#next");
  await page.waitForTimeout(350);
}

async function dropFile(page, selector, filePath, mimeType) {
  const payload = {
    selector,
    name: path.basename(filePath),
    mimeType,
    base64: fs.readFileSync(filePath).toString("base64"),
  };
  await page.evaluate(({ selector, name, mimeType, base64 }) => {
    const bytes = Uint8Array.from(atob(base64), (char) => char.charCodeAt(0));
    const file = new File([bytes], name, { type: mimeType });
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    const element = document.querySelector(selector);
    element.dispatchEvent(new DragEvent("dragover", { bubbles: true, cancelable: true, dataTransfer }));
    element.dispatchEvent(new DragEvent("drop", { bubbles: true, cancelable: true, dataTransfer }));
  }, payload);
}

async function dropVirtualFile(page, selector, name, mimeType, content) {
  await page.evaluate(({ selector, name, mimeType, content }) => {
    const file = new File([content], name, { type: mimeType });
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    const element = document.querySelector(selector);
    element.dispatchEvent(new DragEvent("drop", { bubbles: true, cancelable: true, dataTransfer }));
  }, { selector, name, mimeType, content });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  page.setDefaultTimeout(15000);

  await page.goto(`${baseUrl}/agent/onboarding`, { waitUntil: "networkidle" });
  await next(page);
  await page.fill('[data-path="agent.name"]', "Ava Atlas");
  await page.fill('[data-path="agent.goal"]', "Find logistics work in Poland");
  await next(page);

  await dropVirtualFile(page, '[data-universal-upload="profile_photo"]', "broken.png", "image/png", "not an image");
  await page.waitForSelector('[data-action="retry-file"]');
  await dropFile(page, '[data-universal-upload="profile_photo"]', photoPath, "image/png");
  await page.waitForSelector("text=happy-avatar.png");
  await next(page);

  await page.setInputFiles('input[type="file"]', cvPath);
  await page.waitForSelector("text=happy-cv.rtf");
  await next(page);

  await page.click('[data-action="parse-cv"]');
  await page.waitForSelector('[data-cv-field="email"]');
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/confirm") && response.ok()),
    page.click('[data-action="accept-all-cv"]'),
  ]);
  await next(page);

  await page.fill('[data-path="personal_data.fullName"]', "Olena Atlas");
  await page.fill('[data-path="personal_data.email"]', "olena@example.com");
  await page.fill('[data-path="personal_data.phone"]', "+48123456789");
  await page.fill('[data-path="personal_data.location"]', "Warsaw");
  await next(page);

  await page.fill('[data-path="profession.profession"]', "Logistics coordinator");
  await page.fill('[data-path="profession.headline"]', "Logistics coordinator");
  await page.fill('[data-path="profession.skillsText"]', "Python, Logistics, CRM");
  await next(page);

  await page.locator('[data-record="experience"]').nth(0).fill("Coordinator");
  await page.locator('[data-record="experience"]').nth(1).fill("EWU");
  await page.locator('[data-record="experience"]').nth(2).fill("2022-2026");
  await page.locator('[data-record="experience"]').nth(3).fill("Operations and candidate logistics");
  await page.click('[data-action="add-record"]');
  await next(page);

  await page.locator('[data-record="education"]').nth(0).fill("Logistics course");
  await page.locator('[data-record="education"]').nth(1).fill("ATLAS Academy");
  await page.locator('[data-record="education"]').nth(2).fill("2025");
  await page.locator('[data-record="education"]').nth(3).fill("Certificate available");
  await page.click('[data-action="add-record"]');
  await next(page);

  await page.locator('[data-record="languages"]').nth(0).fill("Polish");
  await page.locator('[data-record="languages"]').nth(1).fill("B1");
  await page.locator('[data-record="languages"]').nth(2).fill("Work communication");
  await page.locator('[data-record="languages"]').nth(3).fill("Confirmed by user");
  await page.click('[data-action="add-record"]');
  await next(page);

  await page.fill('[data-path="preferences.careerGoal"]', "Logistics coordinator role");
  await page.fill('[data-path="preferences.countriesText"]', "Poland, Germany");
  await page.fill('[data-path="preferences.minimumSalary"]', "5000");
  await page.selectOption('[data-path="preferences.currency"]', "PLN");
  await page.selectOption('[data-path="preferences.salaryPeriod"]', "month");
  await next(page);

  await page.click('[data-action="accept-required-consents"]');
  await page.check('[data-path="consents.aiCvAnalysis"]');
  await next(page);

  await page.click('[data-action="generate-dna"]');
  await page.waitForSelector(".dna-score");
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/api/onboarding/complete") && response.ok()),
    page.click("#next"),
  ]);
  await page.waitForSelector("text=Профіль створено");

  await page.goto(`${baseUrl}/agent/dashboard`, { waitUntil: "networkidle" });
  await page.waitForSelector(".score");
  const summary = await page.evaluate(() => ({
    title: document.title,
    score: document.querySelector(".score")?.textContent,
    overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    text: document.body.innerText,
  }));
  if (summary.overflow) throw new Error("Dashboard has horizontal overflow");
  if (!summary.text.includes("happy-cv.rtf")) throw new Error("Dashboard does not show uploaded CV");
  if (!summary.text.includes("2 onboarding document")) throw new Error("Dashboard does not show uploaded documents");
  console.log(JSON.stringify({ title: summary.title, score: summary.score, ok: true }, null, 2));
  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
