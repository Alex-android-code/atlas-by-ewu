"""Managed ATLAS user onboarding page."""

AGENT_ONBOARDING_HTML = r"""
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS | Створення AI-агента</title>
  <style>
    :root {
      --bg: #020714;
      --panel: rgba(255,255,255,0.07);
      --panel-strong: rgba(255,255,255,0.1);
      --line: rgba(238,241,246,0.16);
      --gold: #d4af37;
      --gold-soft: rgba(212,175,55,0.18);
      --text: #eef1f6;
      --muted: rgba(238,241,246,0.7);
      --platinum: #cfd6e6;
      --danger: #ffd0d0;
    }
    * { box-sizing: border-box; min-width: 0; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 16% 0%, rgba(212,175,55,0.18), transparent 30%),
        radial-gradient(circle at 84% 8%, rgba(79,140,255,0.15), transparent 32%),
        linear-gradient(180deg, #020714, #071224 58%, #020714);
    }
    main {
      width: min(1100px, 100%);
      margin: 0 auto;
      padding: calc(24px + env(safe-area-inset-top)) clamp(16px, 4vw, 40px) 40px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: clamp(22px, 5vw, 52px);
    }
    .brand { color: var(--platinum); font-weight: 850; letter-spacing: 0.18em; }
    .top-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .badge {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      background: rgba(255,255,255,0.04);
      font-size: 13px;
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: clamp(22px, 5vw, 44px);
      background: linear-gradient(180deg, var(--panel-strong), rgba(255,255,255,0.035));
      box-shadow: 0 32px 90px rgba(0,0,0,0.34);
    }
    .eyebrow {
      margin: 0 0 12px;
      color: var(--gold);
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      font-size: clamp(32px, 7vw, 70px);
      line-height: 1;
      letter-spacing: 0;
    }
    h2 { margin: 0 0 12px; font-size: clamp(26px, 4vw, 38px); }
    h3 { margin: 0 0 10px; }
    p, li { color: var(--muted); line-height: 1.58; }
    .lead { max-width: 760px; font-size: clamp(16px, 2.2vw, 20px); }
    .progress { height: 9px; margin: 28px 0; overflow: hidden; border-radius: 999px; background: rgba(255,255,255,0.09); }
    .progress span { display: block; width: 0%; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #9f7e22, #f5d56a, #b88720); transition: width 240ms ease; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
    .grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .card {
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      background: rgba(255,255,255,0.045);
    }
    label { display: grid; gap: 8px; color: var(--platinum); font-weight: 720; }
    input, textarea, select {
      width: 100%;
      min-height: 50px;
      border: 1px solid rgba(238,241,246,0.18);
      border-radius: 14px;
      padding: 14px;
      color: var(--text);
      background: rgba(2,7,20,0.72);
      outline: none;
      font: inherit;
    }
    textarea { min-height: 110px; resize: vertical; }
    input:focus, textarea:focus, select:focus { border-color: rgba(212,175,55,0.7); box-shadow: 0 0 0 4px var(--gold-soft); }
    .actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 22px; }
    button, .button {
      min-height: 50px;
      border: 0;
      border-radius: 15px;
      padding: 0 18px;
      cursor: pointer;
      font-weight: 780;
      text-decoration: none;
      display: inline-grid;
      place-items: center;
      text-align: center;
    }
    button:disabled { cursor: not-allowed; opacity: 0.5; }
    .primary { color: #130f05; background: linear-gradient(135deg, #ffe27a, #d4af37 52%, #a97818); box-shadow: 0 18px 45px rgba(212,175,55,0.24); }
    .secondary { color: var(--text); background: rgba(255,255,255,0.06); border: 1px solid var(--line); }
    .danger { color: var(--danger); background: rgba(255,80,80,0.08); border: 1px solid rgba(255,120,120,0.25); }
    .upload {
      border: 1px dashed rgba(212,175,55,0.5);
      border-radius: 22px;
      padding: 22px;
      background: radial-gradient(circle at 15% 0%, rgba(212,175,55,0.18), transparent 32%), rgba(255,255,255,0.04);
    }
    .upload.drag { border-color: #f5d56a; background-color: rgba(212,175,55,0.08); }
    .upload-progress {
      height: 8px;
      margin: 12px 0;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255,255,255,0.09);
    }
    .upload-progress span {
      display: block;
      width: 1%;
      height: 100%;
      background: linear-gradient(90deg, #8db7ff, #f5d56a);
      transition: width 160ms ease;
    }
    .file-row { display: grid; grid-template-columns: 112px 1fr; gap: 16px; align-items: center; }
    .preview {
      width: 112px;
      aspect-ratio: 1;
      border-radius: 18px;
      border: 1px solid var(--line);
      display: grid;
      place-items: center;
      overflow: hidden;
      color: var(--gold);
      background: rgba(2,7,20,0.65);
      font-weight: 900;
    }
    .preview img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .small { font-size: 13px; color: var(--muted); }
    .error { color: var(--danger); margin-top: 12px; }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    .chip { border: 1px solid var(--line); border-radius: 999px; padding: 7px 10px; color: var(--muted); background: rgba(255,255,255,0.04); }
    .consent-row { display: grid; grid-template-columns: auto 1fr; gap: 10px; align-items: start; padding: 12px 0; border-bottom: 1px solid rgba(238,241,246,0.08); }
    .consent-row input { width: 18px; min-height: 18px; margin-top: 3px; }
    .dna-score { font-size: clamp(48px, 10vw, 92px); line-height: 1; color: var(--gold); font-weight: 900; }
    .hidden { display: none !important; }
    @media (max-width: 760px) {
      header { align-items: flex-start; flex-direction: column; }
      .top-actions, .actions, .actions > *, .button { width: 100%; }
      .grid, .grid.three, .file-row { grid-template-columns: 1fr; }
      .preview { width: 96px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">ATLAS by EWU</div>
      <div class="top-actions">
        <a class="secondary button" href="/gdpr">GDPR / RODO</a>
        <a class="secondary button" href="/agent/dashboard">Dashboard</a>
        <div class="badge" id="step-badge">Завантаження</div>
      </div>
    </header>
    <section class="panel">
      <p class="eyebrow">Personal AI Agent</p>
      <div id="view"></div>
      <div class="progress"><span id="progress-bar"></span></div>
      <div id="error" class="error"></div>
      <div class="actions">
        <button class="secondary" id="back" type="button">Назад</button>
        <button class="primary" id="next" type="button">Продовжити</button>
      </div>
    </section>
  </main>
  <script>
    let userId = localStorage.getItem("atlas_user_id") || "";
    let headers = {"Content-Type": "application/json"};
    const steps = ["welcome","agent","profile_photo","cv","cv_review","personal_data","profession","experience","education","languages","preferences","consents","professional_dna","completed"];
    let session = null;
    let current = "welcome";
    let local = {};
    let selectedParsed = {};
    const uploadRuntime = {};
    const uploadConfigs = {
      profile_photo: {
        mode: "image",
        serverKind: "profile-photo",
        acceptedTypes: "image/png,image/jpeg,image/webp,image/heic,image/heif,.png,.jpg,.jpeg,.webp,.heic,.heif",
        extensions: /\.(png|jpg|jpeg|webp|heic|heif)$/i,
        maxSize: 10 * 1024 * 1024,
        maxFiles: 1,
        uploadEndpoint: "/api/files/upload",
        preview: true,
        allowReplace: true,
        allowDelete: true,
        allowDownload: true
      },
      cv: {
        mode: "document",
        serverKind: "cv",
        acceptedTypes: ".pdf,.doc,.docx,.odt,.rtf,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.oasis.opendocument.text,application/rtf,text/rtf",
        extensions: /\.(pdf|doc|docx|odt|rtf)$/i,
        maxSize: 15 * 1024 * 1024,
        maxFiles: 1,
        uploadEndpoint: "/api/files/upload",
        preview: true,
        allowReplace: true,
        allowDelete: true,
        allowDownload: true
      }
    };

    const view = document.getElementById("view");
    const badge = document.getElementById("step-badge");
    const bar = document.getElementById("progress-bar");
    const errorBox = document.getElementById("error");
    const backButton = document.getElementById("back");
    const nextButton = document.getElementById("next");

    async function api(path, options = {}) {
      const response = await fetch(path, {headers, ...options});
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Запит не виконано.");
      return data;
    }

    async function ensureUser() {
      const registrationHeaders = {"Content-Type": "application/json"};
      if (userId) registrationHeaders["X-ATLAS-User-Id"] = userId;
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: registrationHeaders,
        body: JSON.stringify({preferred_language: localStorage.getItem("atlas_language") || "uk"})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "User registration failed.");
      userId = data.user_id;
      localStorage.setItem("atlas_user_id", userId);
      headers = {"Content-Type": "application/json", "X-ATLAS-User-Id": userId};
    }

    async function load() {
      await ensureUser();
      session = await api("/api/onboarding", {headers: {"X-ATLAS-User-Id": userId}});
      local = structuredClone(session.data || {});
      current = session.status === "completed" ? "completed" : (session.current_step || "welcome");
      render();
    }

    function render() {
      errorBox.textContent = "";
      const stepIndex = Math.max(0, steps.indexOf(current));
      badge.textContent = `${stepIndex + 1} / ${steps.length}`;
      bar.style.width = `${session?.progress?.percent || 0}%`;
      backButton.disabled = stepIndex === 0;
      nextButton.textContent = current === "completed" ? "Відкрити dashboard" : current === "professional_dna" ? "Завершити" : "Продовжити";
      view.innerHTML = templates[current]();
      bindStep();
    }

    const templates = {
      welcome: () => `
        <h1>Створення професійного профілю ATLAS</h1>
        <p class="lead">ATLAS проведе вас від першого екрану до готової професійної карти: агент, фото, CV, досвід, мови, побажання, GDPR/RODO та Professional DNA.</p>
        <div class="grid three">
          <div class="card"><h3>AI-агент</h3><p>Персональний помічник запам'ятає вашу ціль і стиль комунікації.</p></div>
          <div class="card"><h3>Документи</h3><p>Фото та CV зберігаються приватно, з валідацією типу і розміру файлу.</p></div>
          <div class="card"><h3>Professional DNA</h3><p>Після підтвердження даних система створить першу rule-based оцінку готовності.</p></div>
        </div>`,
      agent: () => formGrid("Налаштуйте AI-агента", [
        input("agent.name", "Ім'я агента", val("agent.name") || "ATLAS Agent"),
        select("agent.language", "Мова спілкування", ["uk","ru","pl","en","de"], val("agent.language") || "uk"),
        select("agent.style", "Стиль допомоги", ["спокійний професійний","детальний наставник","коротко і по суті"], val("agent.style") || "спокійний професійний"),
        textarea("agent.goal", "Ваша головна ціль", val("agent.goal"))
      ]),
      profile_photo: () => fileTemplate("profile_photo", "Фото профілю", "JPG, JPEG, PNG, WEBP, HEIC до 10 MB", "image/*,.heic,.heif"),
      cv: () => `
        ${fileTemplate("cv", "CV / резюме", "PDF, DOC, DOCX, ODT, RTF до 15 MB", ".pdf,.doc,.docx,.odt,.rtf")}
        <div class="card" style="margin-top:14px">
          <h3>Статус обробки</h3>
          <p>${local.cv?.file ? "CV завантажено. На наступному кроці ATLAS проаналізує файл і попросить підтвердити дані." : "Очікуємо файл CV."}</p>
        </div>`,
      cv_review: () => `
        <div class="card" style="margin-top:14px">
          <h3>Підтвердження даних з CV</h3>
          <p>AI не записує дані в профіль автоматично. Спочатку перегляньте витягнуті поля, відредагуйте або відхиліть.</p>
          <div class="actions">
            <button class="secondary" data-action="parse-cv" type="button">Проаналізувати CV</button>
            <button class="secondary" data-action="accept-all-cv" type="button">Прийняти всі поля</button>
            <button class="secondary" data-action="accept-cv" type="button">Прийняти вибрані</button>
            <button class="danger" data-action="reject-cv" type="button">Відхилити витягнуті дані</button>
          </div>
          <div id="cv-review">${cvReviewTemplate()}</div>
        </div>`,
      personal_data: () => formGrid("Особисті дані", [
        input("personal_data.fullName", "Повне ім'я", val("personal_data.fullName") || parsed("fullName")),
        input("personal_data.email", "Email", val("personal_data.email") || parsed("email")),
        input("personal_data.phone", "Телефон", val("personal_data.phone") || parsed("phone")),
        input("personal_data.location", "Місто / країна", val("personal_data.location") || parsed("location")),
        textarea("personal_data.summary", "Коротке професійне резюме", val("personal_data.summary"))
      ]),
      profession: () => formGrid("Професія та навички", [
        input("profession.profession", "Професія", val("profession.profession")),
        input("profession.headline", "Професійний заголовок", val("profession.headline") || parsed("headline")),
        textarea("profession.skillsText", "Навички через кому", val("profession.skillsText") || listText("skills")),
        input("profession.customSkill", "Додати власну навичку", "")
      ]),
      experience: () => recordsTemplate("experience", "Досвід роботи", ["Посада","Компанія","Період","Опис"]),
      education: () => recordsTemplate("education", "Освіта, курси, сертифікати", ["Назва","Організація","Рік","Документ / примітка"]),
      languages: () => recordsTemplate("languages", "Мови", ["Мова","CEFR рівень","Практика","Примітка"]),
      preferences: () => formGrid("Кар'єрні побажання", [
        textarea("preferences.careerGoal", "Бажана роль і ціль", val("preferences.careerGoal")),
        input("preferences.countriesText", "Країни через кому", val("preferences.countriesText")),
        select("preferences.format", "Формат роботи", ["будь-який","офіс","гібрид","віддалено","вахтовий"], val("preferences.format") || "будь-який"),
        input("preferences.salary", "Очікувана зарплата / валюта", val("preferences.salary"))
      ]),
      consents: () => `
        <h2>GDPR / RODO центр</h2>
        <p>Обов'язкові згоди потрібні для створення профілю та AI-агента. Опціональні згоди не встановлені за замовчуванням.</p>
        ${consent("terms", "Погоджуюся з умовами використання ATLAS", true)}
        ${consent("privacy", "Погоджуюся з політикою приватності та обробкою персональних даних", true)}
        ${consent("aiProcessing", "Дозволяю AI-обробку даних для створення Professional DNA", true)}
        ${consent("marketing", "Дозволяю маркетингові повідомлення", false)}
        ${consent("analytics", "Дозволяю покращення продукту через аналітику", false)}`,
      professional_dna: () => dnaTemplate(),
      completed: () => `
        <h1>Профіль створено</h1>
        <p class="lead">Онбординг завершено, Professional DNA збережено, а ваш AI-агент готовий працювати в особистому кабінеті.</p>
        <div class="actions"><a class="primary button" href="/agent/dashboard">Відкрити dashboard</a></div>`
    };

    function bindStep() {
      document.querySelectorAll("[data-path]").forEach((el) => {
        el.addEventListener("input", () => setPath(el.dataset.path, el.type === "checkbox" ? el.checked : el.value));
        if (el.type === "checkbox") el.addEventListener("change", () => setPath(el.dataset.path, el.checked));
      });
      document.querySelectorAll("[data-universal-upload]").forEach(bindUniversalUpload);
      document.querySelector("[data-action='parse-cv']")?.addEventListener("click", parseCv);
      document.querySelector("[data-action='accept-all-cv']")?.addEventListener("click", acceptAllCv);
      document.querySelector("[data-action='accept-cv']")?.addEventListener("click", acceptCv);
      document.querySelector("[data-action='reject-cv']")?.addEventListener("click", rejectCv);
      document.querySelector("[data-action='generate-dna']")?.addEventListener("click", generateDna);
      document.querySelector("[data-action='add-record']")?.addEventListener("click", addRecordFromForm);
      document.querySelectorAll("[data-action='remove-record']").forEach((button) => button.addEventListener("click", removeRecord));
      document.querySelector("[data-action='view-file']")?.addEventListener("click", viewFile);
      document.querySelector("[data-action='delete-file']")?.addEventListener("click", deleteFile);
    }

    async function next() {
      if (current === "completed") {
        location.href = "/agent/dashboard";
        return;
      }
      const data = collectStepData(current);
      if (!validate(current, data)) return;
      if (current === "professional_dna") {
        await api("/api/onboarding/complete", {method: "POST", headers: {"X-ATLAS-User-Id": userId}});
        session = await api("/api/onboarding", {headers: {"X-ATLAS-User-Id": userId}});
        current = "completed";
        render();
        return;
      }
      session = await api("/api/onboarding", {method: "PATCH", body: JSON.stringify({step: current, data}), headers});
      local = structuredClone(session.data || {});
      current = session.current_step;
      render();
    }

    function previous() {
      const index = steps.indexOf(current);
      if (index > 0) {
        current = steps[index - 1];
        render();
      }
    }

    function collectStepData(step) {
      if (step === "profession") {
        const data = local.profession || {};
        const skills = splitList(data.skillsText);
        if (data.customSkill) skills.push(data.customSkill);
        return {...data, skills: [...new Set(skills.map((item) => item.trim()).filter(Boolean))]};
      }
      if (step === "preferences") {
        const data = local.preferences || {};
        return {...data, countries: splitList(data.countriesText)};
      }
      if (step === "cv_review") {
        return {
          accepted_parsed_data: local.cv?.accepted_parsed_data || {},
          rejected: Boolean(local.cv?.parse_rejected),
          job_id: session?.parsed_cv?.job_id || ""
        };
      }
      if (step === "consents") return {...(local.consents || {}), version: "atlas-rodo-v1", language: local.agent?.language || "uk"};
      return local[step] || {};
    }

    function validate(step, data) {
      if (step === "profile_photo" && !data.file?.id) return fail("Додайте фото профілю.");
      if (step === "cv" && !data.file?.id) return fail("Додайте CV або резюме.");
      if (step === "cv_review" && !hasAcceptedCvData() && !local.cv?.parse_rejected) return fail("Прийміть поля з CV або відхиліть витягнуті дані.");
      if (step === "personal_data" && (!data.fullName || !data.email)) return fail("Вкажіть ім'я та email.");
      if (step === "consents" && (!data.terms || !data.privacy || !data.aiProcessing)) return fail("Потрібні всі обов'язкові згоди.");
      return true;
    }

    function fail(message) {
      errorBox.textContent = message;
      return false;
    }

    function bindUniversalUpload(root) {
      const kind = root.dataset.universalUpload;
      const input = root.querySelector("input[type=file]");
      root.addEventListener("dragover", (event) => { event.preventDefault(); root.classList.add("drag"); });
      root.addEventListener("dragleave", () => root.classList.remove("drag"));
      root.addEventListener("drop", (event) => {
        event.preventDefault();
        root.classList.remove("drag");
        if (event.dataTransfer.files[0]) upload(kind, event.dataTransfer.files[0]);
      });
      root.querySelector("[data-action='choose-file']")?.addEventListener("click", () => input.click());
      root.querySelector("[data-action='retry-file']")?.addEventListener("click", () => uploadRuntime[kind]?.lastFile && upload(kind, uploadRuntime[kind].lastFile));
      input.addEventListener("change", () => input.files[0] && upload(kind, input.files[0]));
    }

    async function upload(kind, file) {
      return universalUpload(kind, file);
    }

    async function legacyUploadUnused(kind, file) {
      const isPhoto = kind === "profile_photo";
      const max = isPhoto ? 10 * 1024 * 1024 : 15 * 1024 * 1024;
      const allowed = isPhoto ? /\.(png|jpg|jpeg|webp|heic|heif)$/i : /\.(pdf|doc|docx|odt|rtf)$/i;
      if (!allowed.test(file.name) || file.size > max) return fail(isPhoto ? "Фото має бути JPG/JPEG/PNG/WEBP/HEIC до 10 MB." : "CV має бути PDF/DOC/DOCX/ODT/RTF до 15 MB.");
      const body = new FormData();
      body.append("file", file);
      const endpoint = "/api/files/upload";
      const response = await fetch(endpoint, {method: "POST", headers: {"X-ATLAS-User-Id": userId}, body});
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.success) return fail(data.detail || "Файл не завантажено.");
      setPath(`${kind}.file`, data.file);
      await api("/api/onboarding", {method: "PATCH", body: JSON.stringify({step: kind === "profile_photo" ? "profile_photo" : "cv", data: local[kind]}), headers});
      if (kind === current) render();
    }

    async function universalUpload(kind, file) {
      const config = uploadConfigs[kind];
      if (!config) return fail("Unsupported upload type.");
      if (!config.extensions.test(file.name) || file.size > config.maxSize) return fail(config.mode === "image" ? "Фото має бути JPG/JPEG/PNG/WEBP/HEIC до 10 MB." : "Документ має бути PDF/DOC/DOCX/ODT/RTF до 15 MB.");
      const body = new FormData();
      body.append("kind", config.serverKind);
      body.append("file", file);
      uploadRuntime[kind] = {status: "uploading", progress: 1, lastFile: file, error: ""};
      render();
      try {
        const data = await uploadWithProgress(config.uploadEndpoint, body, kind);
        if (!data.success) throw new Error(data.detail || "File upload failed.");
        setPath(`${kind}.file`, data.file);
        uploadRuntime[kind] = {status: "success", progress: 100, lastFile: file, error: ""};
        await api("/api/onboarding", {method: "PATCH", body: JSON.stringify({step: kind === "profile_photo" ? "profile_photo" : "cv", data: local[kind]}), headers});
      } catch (error) {
        uploadRuntime[kind] = {status: "error", progress: 0, lastFile: file, error: error.message || "File upload failed."};
        fail(uploadRuntime[kind].error);
      }
      render();
    }

    function uploadWithProgress(endpoint, body, kind) {
      return new Promise((resolve, reject) => {
        const request = new XMLHttpRequest();
        request.open("POST", endpoint);
        request.setRequestHeader("X-ATLAS-User-Id", userId);
        request.upload.addEventListener("progress", (event) => {
          if (!event.lengthComputable) return;
          uploadRuntime[kind].progress = Math.max(1, Math.round((event.loaded / event.total) * 100));
          const bar = document.querySelector(`[data-upload-progress="${kind}"] span`);
          if (bar) bar.style.width = `${uploadRuntime[kind].progress}%`;
        });
        request.onload = () => {
          const data = JSON.parse(request.responseText || "{}");
          if (request.status >= 200 && request.status < 300) resolve(data);
          else reject(new Error(data.detail || "File upload failed."));
        };
        request.onerror = () => reject(new Error("Network error while uploading file."));
        request.send(body);
      });
    }

    async function viewFile() {
      const kind = current === "profile_photo" ? "profile_photo" : "cv";
      const file = local[kind]?.file;
      if (!file?.url) return;
      const response = await fetch(file.url, {headers: {"X-ATLAS-User-Id": userId}});
      if (!response.ok) return fail("Не вдалося відкрити файл.");
      const blobUrl = URL.createObjectURL(await response.blob());
      window.open(blobUrl, "_blank", "noopener");
      setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
    }

    async function deleteFile() {
      const kind = current === "profile_photo" ? "profile_photo" : "cv";
      const file = local[kind]?.file;
      if (!file?.id) return;
      const config = uploadConfigs[kind];
      await fetch(`/api/files/${encodeURIComponent(file.id)}?kind=${encodeURIComponent(config.serverKind)}`, {method: "DELETE", headers: {"X-ATLAS-User-Id": userId}});
      setPath(`${kind}.file`, null);
      render();
    }

    async function parseCv() {
      const file = local.cv?.file;
      if (!file?.id) return fail("Спочатку завантажте CV.");
      await api("/api/onboarding", {method: "PATCH", body: JSON.stringify({step: "cv", data: local.cv}), headers});
      const job = await api(`/api/cv/${encodeURIComponent(file.id)}/parse`, {method: "POST", headers: {"X-ATLAS-User-Id": userId}});
      session.parsed_cv = {job_id: job.id, status: job.status, result: job.result};
      selectedParsed = job.result;
      render();
    }

    async function acceptCv() {
      selectedParsed = collectSelectedCvFields();
      if (!Object.keys(selectedParsed).length) return fail("Виберіть хоча б одне поле з CV.");
      await api("/api/cv/parse-jobs/accept", {method: "POST", body: JSON.stringify({accepted: selectedParsed}), headers});
      setPath("cv.accepted_parsed_data", selectedParsed);
      setPath("cv.parse_rejected", false);
      fail("Дані з CV прийнято. Можете продовжити.");
    }

    async function acceptAllCv() {
      selectedParsed = collectAllCvFields();
      if (!Object.keys(selectedParsed).length) return fail("Спочатку проаналізуйте CV.");
      await api("/api/cv/parse-jobs/accept", {method: "POST", body: JSON.stringify({accepted: selectedParsed}), headers});
      setPath("cv.accepted_parsed_data", selectedParsed);
      setPath("cv.parse_rejected", false);
      fail("Усі доступні дані з CV прийнято. Можете продовжити.");
    }

    function rejectCv() {
      setPath("cv.accepted_parsed_data", {});
      setPath("cv.parse_rejected", true);
      selectedParsed = {};
      fail("Витягнуті дані відхилено. У профіль нічого не записано.");
    }

    async function generateDna() {
      const dna = await api("/api/professional-dna/generate", {method: "POST", headers: {"X-ATLAS-User-Id": userId}});
      setPath("professional_dna", dna);
      session.professional_dna = dna;
      render();
    }

    function addRecordFromForm(event) {
      const step = event.target.dataset.step;
      const values = [...document.querySelectorAll(`[data-record='${step}']`)].map((input) => input.value.trim());
      if (!values.some(Boolean)) return;
      const record = {title: values[0], organization: values[1], period: values[2], note: values[3]};
      const records = local[step]?.records || [];
      setPath(`${step}.records`, [...records, record]);
      render();
    }

    function removeRecord(event) {
      const step = event.target.dataset.step;
      const index = Number(event.target.dataset.index);
      const records = [...(local[step]?.records || [])];
      records.splice(index, 1);
      setPath(`${step}.records`, records);
      render();
    }

    function UniversalFileUpload({key, title, hint, value, runtime, config}) {
      const file = value;
      const progress = runtime.status === "uploading"
        ? `<div class="upload-progress" data-upload-progress="${key}"><span style="width:${runtime.progress || 1}%"></span></div>`
        : "";
      const error = runtime.status === "error" ? `<p class="error">${escapeHtml(runtime.error || "Upload failed.")}</p>` : "";
      const preview = config.mode === "image" && file?.thumbnail_url ? `<img src="${file.thumbnail_url}" alt="${escapeHtml(title)}">` : `<span>${config.mode === "image" ? "A" : "DOC"}</span>`;
      return `
        <h2>${title}</h2>
        <div class="upload" data-universal-upload="${key}" data-mode="${config.mode}">
          <input class="hidden" type="file" accept="${config.acceptedTypes}">
          ${file ? `
            <div class="file-row">
              <div class="preview">${preview}</div>
              <div>
                <h3>${escapeHtml(file.original_name || "File")}</h3>
                <p>${formatBytes(file.size || 0)} · ${escapeHtml(file.mimeType || "")}</p>
                <p class="small">${escapeHtml(file.analysis?.message || "File uploaded.")}</p>
                ${progress}
                ${error}
                <div class="actions">
                  ${config.allowDownload ? `<button class="secondary" data-action="view-file" type="button">Переглянути</button>` : ""}
                  ${config.allowReplace ? `<button class="secondary" data-action="choose-file" type="button">Замінити</button>` : ""}
                  ${config.allowDelete ? `<button class="danger" data-action="delete-file" type="button">Видалити</button>` : ""}
                  ${runtime.status === "error" ? `<button class="secondary" data-action="retry-file" type="button">Повторити</button>` : ""}
                </div>
              </div>
            </div>` : `
            <h3>Прикріпити файл</h3>
            <p>Перетягніть файл сюди або виберіть його на комп'ютері. ${hint}</p>
            ${progress}
            ${error}
            <button class="primary" data-action="choose-file" type="button">Прикріпити файл</button>
            ${runtime.status === "error" ? `<button class="secondary" data-action="retry-file" type="button">Повторити</button>` : ""}`}
        </div>`;
    }

    function fileTemplate(kind, title, hint, accept) {
      return UniversalFileUpload({
        key: kind,
        title,
        hint,
        value: local[kind]?.file,
        runtime: uploadRuntime[kind] || {},
        config: uploadConfigs[kind]
      });
    }

    function legacyFileTemplateUnused(kind, title, hint, accept) {
      const file = local[kind]?.file;
      const preview = kind === "profile_photo" && file?.thumbnail_url ? `<img src="${file.thumbnail_url}" alt="Фото профілю">` : `<span>${kind === "profile_photo" ? "A" : "CV"}</span>`;
      return `
        <h2>${title}</h2>
        <div class="upload" data-universal-upload="${kind}">
          <input class="hidden" type="file" accept="${accept}">
          ${file ? `
            <div class="file-row">
              <div class="preview">${preview}</div>
              <div>
                <h3>${escapeHtml(file.original_name || "Файл")}</h3>
                <p>${formatBytes(file.size || 0)} · ${escapeHtml(file.mimeType || "")}</p>
                <p class="small">${escapeHtml(file.analysis?.message || "Файл завантажено.")}</p>
                <div class="actions">
                  <button class="secondary" data-action="view-file" type="button">Переглянути</button>
                  <button class="secondary" data-action="choose-file" type="button">Замінити</button>
                  <button class="danger" data-action="delete-file" type="button">Видалити</button>
                </div>
              </div>
            </div>` : `
            <h3>Прикріпити файл</h3>
            <p>Перетягніть файл сюди або виберіть його на комп'ютері. ${hint}</p>
            <button class="primary" data-action="choose-file" type="button">Вибрати файл</button>`}
        </div>`;
    }

    function cvReviewTemplate() {
      const parsedData = session?.parsed_cv?.result;
      if (!parsedData) return `<p class="small">Після аналізу тут з'являться поля з confidence і source.</p>`;
      return `<div class="grid">${Object.entries(parsedData).filter(([key]) => !["source","warnings","confidence"].includes(key)).map(([key, value]) => {
        const shown = typeof value === "object" && value !== null && "value" in value ? value.value : value;
        const confidence = typeof value === "object" && value !== null ? value.confidence || parsedData.confidence : parsedData.confidence;
        const textValue = Array.isArray(shown) ? shown.join(", ") : (typeof shown === "object" ? JSON.stringify(shown ?? "") : String(shown ?? ""));
        const hasValue = textValue.trim().length > 0 && textValue !== "[]";
        return `<div class="card">
          <label class="consent-row"><input type="checkbox" data-cv-select="${escapeHtml(key)}" ${hasValue ? "checked" : ""}><span><strong>${escapeHtml(key)}</strong></span></label>
          <textarea data-cv-field="${escapeHtml(key)}">${escapeHtml(textValue)}</textarea>
          <div class="chips"><span class="chip">${escapeHtml(confidence || "low")}</span><span class="chip">${escapeHtml(value?.source || parsedData.source?.fileName || "cv")}</span></div>
        </div>`;
      }).join("")}</div><p class="small">${escapeHtml((parsedData.warnings || []).join(" "))}</p>`;
    }

    function collectSelectedCvFields() {
      const result = {};
      document.querySelectorAll("[data-cv-select]:checked").forEach((checkbox) => {
        const key = checkbox.dataset.cvSelect;
        const value = document.querySelector(`[data-cv-field="${CSS.escape(key)}"]`)?.value.trim();
        if (value) result[key] = cvFieldValue(key, value);
      });
      return result;
    }

    function collectAllCvFields() {
      const result = {};
      document.querySelectorAll("[data-cv-field]").forEach((field) => {
        const key = field.dataset.cvField;
        const value = field.value.trim();
        if (value) result[key] = cvFieldValue(key, value);
      });
      return result;
    }

    function cvFieldValue(key, value) {
      const parsedData = session?.parsed_cv?.result || {};
      const original = parsedData[key];
      if (["skills", "professions"].includes(key)) {
        return {value: splitList(value), source: "user_confirmed_cv_review", confidence: original?.confidence || "medium"};
      }
      return {value, source: "user_confirmed_cv_review", confidence: original?.confidence || "medium"};
    }

    function dnaTemplate() {
      const dna = local.professional_dna || session?.professional_dna;
      if (!dna) {
        return `<h2>Professional DNA v1</h2><p>Система створить першу детерміновану оцінку без зовнішніх AI-ключів: готовність профілю, документи, навички, мови, мобільність і рекомендації.</p><button class="primary" data-action="generate-dna" type="button">Згенерувати Professional DNA</button>`;
      }
      return `<h2>Professional DNA v1</h2><div class="dna-score">${dna.overallScore}%</div><div class="grid"><div class="card"><h3>Сильні сторони</h3><ul>${dna.strengths.map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div><div class="card"><h3>Прогалини</h3><ul>${(dna.gaps.length ? dna.gaps : ["Критичних прогалин не знайдено."]).map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div></div><div class="chips">${dna.recommendedActions.map((x) => `<span class="chip">${escapeHtml(x)}</span>`).join("")}</div>`;
    }

    function formGrid(title, fields) {
      return `<h2>${title}</h2><div class="grid">${fields.map((field) => `<div class="card">${field}</div>`).join("")}</div>`;
    }

    function recordsTemplate(step, title, labels) {
      const records = local[step]?.records || [];
      return `<h2>${title}</h2><div class="grid">${labels.map((label) => `<label>${label}<input data-record="${step}"></label>`).join("")}</div><div class="actions"><button class="secondary" data-action="add-record" data-step="${step}" type="button">Додати запис</button></div><div class="grid" style="margin-top:14px">${records.map((record, index) => `<div class="card"><h3>${escapeHtml(record.title || "Запис")}</h3><p>${escapeHtml([record.organization, record.period, record.note].filter(Boolean).join(" · "))}</p><button class="danger" data-action="remove-record" data-step="${step}" data-index="${index}" type="button">Видалити</button></div>`).join("")}</div>`;
    }

    function input(path, label, value = "") { return `<label>${label}<input data-path="${path}" value="${escapeHtml(value)}"></label>`; }
    function textarea(path, label, value = "") { return `<label>${label}<textarea data-path="${path}">${escapeHtml(value)}</textarea></label>`; }
    function select(path, label, options, value = "") { return `<label>${label}<select data-path="${path}">${options.map((option) => `<option ${option === value ? "selected" : ""}>${escapeHtml(option)}</option>`).join("")}</select></label>`; }
    function consent(path, label, required) {
      const checked = Boolean(val(`consents.${path}`));
      return `<label class="consent-row"><input type="checkbox" data-path="consents.${path}" ${checked ? "checked" : ""}><span>${label} ${required ? "<strong>(обов'язково)</strong>" : "(опціонально)"}</span></label>`;
    }
    function val(path) { return path.split(".").reduce((acc, key) => acc?.[key], local) || ""; }
    function parsed(key) {
      const accepted = local.cv?.accepted_parsed_data || {};
      const value = accepted[key];
      return value && typeof value === "object" && "value" in value ? value.value : value || "";
    }
    function listText(key) {
      const value = parsed(key);
      return Array.isArray(value) ? value.join(", ") : "";
    }
    function setPath(path, value) {
      const parts = path.split(".");
      let target = local;
      while (parts.length > 1) {
        const key = parts.shift();
        target[key] = target[key] || {};
        target = target[key];
      }
      target[parts[0]] = value;
    }
    function splitList(value) { return String(value || "").split(",").map((item) => item.trim()).filter(Boolean); }
    function hasAcceptedCvData() { return Object.keys(local.cv?.accepted_parsed_data || {}).length > 0; }
    function formatBytes(bytes) { return bytes ? `${(bytes / 1024 / 1024).toFixed(bytes > 1048576 ? 1 : 2)} MB` : "0 MB"; }
    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[char]));
    }

    backButton.addEventListener("click", previous);
    nextButton.addEventListener("click", () => next().catch((error) => fail(error.message)));
    load().catch((error) => fail(error.message));
  </script>
</body>
</html>
"""
