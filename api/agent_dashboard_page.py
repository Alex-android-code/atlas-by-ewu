"""Real ATLAS agent dashboard page backed by onboarding workflow data."""

AGENT_DASHBOARD_HTML = r"""
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS | AI Agent Dashboard</title>
  <style>
    :root {
      --bg: #020714;
      --panel: rgba(255,255,255,0.07);
      --line: rgba(238,241,246,0.16);
      --gold: #d4af37;
      --text: #eef1f6;
      --muted: rgba(238,241,246,0.72);
      --platinum: #cfd6e6;
      --ok: #8fe3bd;
      --warn: #f5d56a;
    }
    * { box-sizing: border-box; min-width: 0; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 18% 0%, rgba(212,175,55,0.16), transparent 30%),
        radial-gradient(circle at 82% 0%, rgba(79,140,255,0.14), transparent 32%),
        #020714;
    }
    main { width: min(1180px, 100%); margin: 0 auto; padding: calc(24px + env(safe-area-inset-top)) clamp(16px, 4vw, 40px) 40px; }
    header { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 24px; }
    .brand { color: var(--platinum); font-weight: 850; letter-spacing: 0.18em; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; }
    .button {
      min-height: 44px;
      border-radius: 14px;
      padding: 0 16px;
      display: inline-grid;
      place-items: center;
      color: #130f05;
      background: linear-gradient(135deg, #ffe27a, #d4af37 52%, #a97818);
      text-decoration: none;
      font-weight: 780;
    }
    .secondary { color: var(--text); background: rgba(255,255,255,0.06); border: 1px solid var(--line); }
    .hero, .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .grid { margin-top: 16px; }
    .grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .panel, .card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, rgba(255,255,255,0.09), rgba(255,255,255,0.035));
      box-shadow: 0 26px 80px rgba(0,0,0,0.26);
      padding: clamp(18px, 3vw, 30px);
    }
    .eyebrow { color: var(--gold); margin: 0 0 10px; letter-spacing: 0.16em; text-transform: uppercase; font-size: 12px; }
    h1 { margin: 0; font-size: clamp(34px, 7vw, 72px); line-height: 1; letter-spacing: 0; }
    h2, h3 { margin: 0 0 10px; }
    p, li { color: var(--muted); line-height: 1.55; }
    ul { margin: 8px 0 0; padding-left: 18px; }
    .score { font-size: clamp(48px, 9vw, 88px); color: var(--gold); font-weight: 900; line-height: 1; }
    .meter { height: 10px; overflow: hidden; border-radius: 999px; background: rgba(255,255,255,0.09); }
    .meter span { display: block; height: 100%; background: linear-gradient(90deg, #9f7e22, #f5d56a, #b88720); }
    .chip { display: inline-flex; margin: 5px 5px 0 0; border: 1px solid var(--line); border-radius: 999px; padding: 7px 10px; color: var(--muted); background: rgba(255,255,255,0.04); }
    .ok { color: var(--ok); }
    .warn { color: var(--warn); }
    .empty { border-style: dashed; opacity: 0.82; }
    .kv { display: grid; gap: 8px; }
    .kv div { display: flex; justify-content: space-between; gap: 14px; border-bottom: 1px solid rgba(238,241,246,0.08); padding-bottom: 8px; }
    .kv span { color: var(--muted); }
    .kv strong { text-align: right; }
    @media (max-width: 820px) {
      header { align-items: flex-start; flex-direction: column; }
      .actions, .button { width: 100%; }
      .hero, .grid, .grid.three { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">ATLAS by EWU</div>
      <div class="actions">
        <a class="button secondary" href="/agent/onboarding">Редагувати профіль</a>
        <a class="button" href="/">На головну</a>
      </div>
    </header>
    <section id="dashboard">Завантаження...</section>
  </main>
  <script>
    async function ensureUser() {
      let userId = localStorage.getItem("atlas_user_id");
      const registrationHeaders = {"Content-Type": "application/json"};
      if (userId) registrationHeaders["X-ATLAS-User-Id"] = userId;
      const response = await fetch("/api/auth/register", {method: "POST", headers: registrationHeaders, body: JSON.stringify({preferred_language: "uk"})});
      const data = await response.json();
      localStorage.setItem("atlas_user_id", data.user_id);
      return data.user_id;
    }

    async function loadDashboard() {
      const userId = await ensureUser();
      const response = await fetch("/api/agent/dashboard", {headers: {"X-ATLAS-User-Id": userId}});
      if (!response.ok) throw new Error("Dashboard недоступний");
      const data = await response.json();
      if (data.onboarding?.redirectTo) {
        location.href = data.onboarding.redirectTo;
        return;
      }
      render(data);
    }

    function render(data) {
      const dna = data.professional_dna || {};
      const dnaSummary = data.professionalDNA || {};
      const profile = data.profile || {};
      const profileStatus = data.profile_status || {};
      const readiness = data.readiness || {};
      const contact = profile.contact_information || {};
      const personal = profile.personal_information || {};
      const cv = data.cv?.file;
      const photo = data.photo?.file;
      const completeness = Number(profileStatus.completeness || profile.profile_completeness || data.onboarding?.progress?.percent || 0);
      const components = dna.components || {};
      document.getElementById("dashboard").innerHTML = `
        <section class="hero">
          <div class="panel">
            <p class="eyebrow">AI Agent</p>
            <h1>${escapeHtml(data.agent?.name || "ATLAS Agent")}</h1>
            <p>${escapeHtml(data.agent?.goal || "Профіль агента формується на основі підтверджених даних.")}</p>
            <div class="meter"><span style="width:${clamp(completeness)}%"></span></div>
            <p>${clamp(completeness)}% заповнення профілю · ${escapeHtml(data.onboarding?.status || "not_started")}</p>
          </div>
          <div class="panel">
            <p class="eyebrow">Professional DNA</p>
            <div class="score">${dnaSummary?.overallScore ?? dna.overallScore ?? 0}%</div>
            <p>${escapeHtml(dnaSummary?.version || dna.scoringConfigVersion || dna.version || "DNA ще не згенеровано")}</p>
          </div>
        </section>
        <section class="grid">
          <article class="card"><h3>Profile Status</h3>
            <p>Completed: ${(profileStatus.completedSections || []).map(escapeHtml).join(", ") || "none"}</p>
            <p>Missing: ${(profileStatus.missingSections || []).map(escapeHtml).join(", ") || "none"}</p>
            ${(profileStatus.problems || []).length ? `<p>Problems: ${(profileStatus.problems || []).map(escapeHtml).join(", ")}</p>` : ""}
            <a class="button secondary" href="${escapeHtml((profileStatus.editRoutes || {}).personal_data || "/agent/onboarding?step=personal_data")}">Edit profile</a>
          </article>
          <article class="card"><h3>Career Readiness</h3>${readinessList(readiness)}</article>
        </section>
        <section class="grid three">
          <article class="card"><h3>Контактні дані</h3>${kv([
            ["Ім'я", personal.full_name || contact.full_name],
            ["Email", contact.email],
            ["Телефон", contact.phone],
            ["Локація", profile.current_location?.city || profile.current_location?.country || profile.current_location]
          ])}</article>
          <article class="card"><h3>CV</h3>${cv ? fileBlock(cv) : missing("CV не завантажено")}</article>
          <article class="card"><h3>Фото профілю</h3>${photo ? fileBlock(photo) : missing("Фото не завантажено")}</article>
        </section>
        <section class="grid">
          <article class="card"><h3>Документи</h3>${documents(data.documents || [])}</article>
          <article class="card"><h3>Рекомендації</h3>${recommendations(data.recommendedActions || data.recommendations || dna.recommendations || [])}</article>
        </section>
        <section class="grid">
          <article class="card"><h3>Компоненти DNA</h3>
            ${dnaSummary ? `<p>Strongest: ${(dnaSummary.strongestComponents || []).map(escapeHtml).join(", ") || "none"}</p><p>Weakest: ${(dnaSummary.weakestComponents || []).map(escapeHtml).join(", ") || "none"}</p>` : ""}
            ${componentGrid(components)}
          </article>
          <article class="card"><h3>Сильні сторони і прогалини</h3>
            <h4>Сильні сторони</h4>${insights(dna.strengths || [])}
            <h4>Прогалини</h4>${insights(dna.gaps || [], "Критичних прогалин не знайдено.")}
          </article>
        </section>
        <section class="grid">
          <article class="card"><h3>Recent Activity</h3>${activity(data.recentActivity || [])}</article>
          <article class="card"><h3>Quick Actions</h3>${quickActions(data.quickActions || [])}</article>
        </section>
        <section class="grid three">
          ${(data.unavailable_modules || []).map((item) => `<article class="card empty"><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.reason)}</p><span class="chip">недоступно</span></article>`).join("")}
        </section>`;
    }

    function kv(items) {
      const rows = items.filter(([, value]) => Boolean(value));
      if (!rows.length) return missing("Поки немає підтверджених контактних даних");
      return `<div class="kv">${rows.map(([key, value]) => `<div><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}</div>`;
    }
    function fileBlock(file) {
      return `<p>${escapeHtml(file.original_name || file.name || file.id)} · ${formatBytes(file.size)}</p><span class="chip ok">прикріплено</span>`;
    }
    function missing(text) {
      return `<p>${escapeHtml(text)}</p><span class="chip warn">потрібно додати</span>`;
    }
    function documents(items) {
      if (!items.length) return missing("Документи онбордингу ще не збережені");
      return `<ul>${items.map((item) => `<li>${escapeHtml(item.title || item.filename || item.metadata?.original_name || item.id)} · ${escapeHtml(item.status || "stored")}</li>`).join("")}</ul><span class="chip ok">${items.length} onboarding document(s) stored</span>`;
    }
    function recommendations(items) {
      if (!items.length) return `<p>Немає rule-based рекомендацій для поточного профілю.</p>`;
      return `<ul>${items.slice(0, 5).map((item) => `<li><strong>${escapeHtml(item.title || item)}</strong>${item.priority ? ` · ${escapeHtml(item.priority)}` : ""}${item.route ? ` <a href="${escapeHtml(item.route)}">Open</a>` : ""}</li>`).join("")}</ul>`;
    }
    function readinessList(readiness) {
      const entries = Object.entries(readiness);
      if (!entries.length) return `<p>Readiness data is not available yet.</p>`;
      return `<div class="kv">${entries.map(([key, value]) => `<div><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}</div>`;
    }
    function activity(items) {
      if (!items.length) return `<p>No real activity has been recorded yet.</p>`;
      return `<ul>${items.map((item) => `<li><strong>${escapeHtml(item.title)}</strong> · ${escapeHtml(item.createdAt || "")}</li>`).join("")}</ul>`;
    }
    function quickActions(items) {
      if (!items.length) return `<p>No available actions for this profile state.</p>`;
      return `<div class="actions">${items.map((item) => `<a class="button secondary" href="${escapeHtml(item.route)}">${escapeHtml(item.title)}</a>`).join("")}</div>`;
    }
    function componentGrid(components) {
      const entries = Object.entries(components);
      if (!entries.length) return `<p>Згенеруйте Professional DNA, щоб побачити формулу.</p>`;
      return entries.map(([key, item]) => `<p><strong>${escapeHtml(key)}</strong>: ${escapeHtml(item.score)} / 100 · weight ${escapeHtml(item.weight)}%</p>`).join("");
    }
    function insights(items, empty = "Дані ще накопичуються.") {
      if (!items.length) return `<p>${escapeHtml(empty)}</p>`;
      return `<ul>${items.map((item) => `<li>${escapeHtml(typeof item === "string" ? item : `${item.title}: ${item.description || ""}`)}</li>`).join("")}</ul>`;
    }
    function clamp(value) { return Math.max(0, Math.min(100, Math.round(Number(value) || 0))); }
    function formatBytes(bytes) { return bytes ? `${(bytes / 1024 / 1024).toFixed(bytes > 1048576 ? 1 : 2)} MB` : "0 MB"; }
    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[char]));
    }
    loadDashboard().catch((error) => { document.getElementById("dashboard").textContent = error.message; });
  </script>
</body>
</html>
"""
