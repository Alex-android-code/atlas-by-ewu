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
      --muted: rgba(238,241,246,0.7);
      --platinum: #cfd6e6;
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
    .button {
      min-height: 46px;
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
    .grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 16px; }
    .panel, .card {
      border: 1px solid var(--line);
      border-radius: 22px;
      background: linear-gradient(180deg, rgba(255,255,255,0.09), rgba(255,255,255,0.035));
      box-shadow: 0 26px 80px rgba(0,0,0,0.26);
      padding: clamp(18px, 3vw, 30px);
    }
    .eyebrow { color: var(--gold); margin: 0 0 10px; letter-spacing: 0.16em; text-transform: uppercase; font-size: 12px; }
    h1 { margin: 0; font-size: clamp(34px, 7vw, 72px); line-height: 1; letter-spacing: 0; }
    h2, h3 { margin: 0 0 10px; }
    p, li { color: var(--muted); line-height: 1.55; }
    .score { font-size: clamp(48px, 9vw, 88px); color: var(--gold); font-weight: 900; line-height: 1; }
    .meter { height: 10px; overflow: hidden; border-radius: 999px; background: rgba(255,255,255,0.09); }
    .meter span { display: block; height: 100%; background: linear-gradient(90deg, #9f7e22, #f5d56a, #b88720); }
    .chip { display: inline-flex; margin: 5px 5px 0 0; border: 1px solid var(--line); border-radius: 999px; padding: 7px 10px; color: var(--muted); background: rgba(255,255,255,0.04); }
    .empty { border-style: dashed; opacity: 0.78; }
    @media (max-width: 820px) {
      header { align-items: flex-start; flex-direction: column; }
      .hero, .grid, .grid.three { grid-template-columns: 1fr; }
      .button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">ATLAS by EWU</div>
      <a class="button" href="/agent/onboarding">Продовжити профіль</a>
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
      const data = await response.json();
      render(data);
    }

    function render(data) {
      const dna = data.professional_dna || {};
      const profile = data.profile || {};
      const cv = data.cv?.file;
      const photo = data.photo?.file;
      const completeness = profile.profile_completeness || data.onboarding?.progress?.percent || 0;
      document.getElementById("dashboard").innerHTML = `
        <section class="hero">
          <div class="panel">
            <p class="eyebrow">AI Agent</p>
            <h1>${escapeHtml(data.agent?.name || "ATLAS Agent")}</h1>
            <p>${escapeHtml(data.agent?.goal || "AI-agent profile is being formed.")}</p>
            <div class="meter"><span style="width:${Number(completeness)}%"></span></div>
            <p>${Number(completeness)}% profile completeness · ${escapeHtml(data.onboarding?.status || "not_started")}</p>
          </div>
          <div class="panel">
            <p class="eyebrow">Professional DNA</p>
            <div class="score">${dna.overallScore ?? 0}%</div>
            <p>${escapeHtml(dna.version || "DNA has not been generated yet.")}</p>
          </div>
        </section>
        <section class="grid three">
          <article class="card"><h3>Profile photo</h3>${photo ? `<p>${escapeHtml(photo.original_name)}</p><span class="chip">attached</span>` : `<p>No profile photo attached.</p><span class="chip">missing</span>`}</article>
          <article class="card"><h3>CV</h3>${cv ? `<p>${escapeHtml(cv.original_name)} · ${formatBytes(cv.size)}</p><span class="chip">attached</span>` : `<p>No CV attached.</p><span class="chip">missing</span>`}</article>
          <article class="card"><h3>Documents</h3><p>${data.documents.length} onboarding document(s) stored.</p></article>
        </section>
        <section class="grid">
          <article class="card"><h3>Recommendations</h3>${list(data.recommendations.map((item) => item.title), "No rule-based recommendations yet.")}</article>
          <article class="card"><h3>DNA formula</h3>${dna.formula ? `<p>${escapeHtml(dna.formula.overallScore)}</p>` : "<p>Generate Professional DNA to see formula.</p>"}</article>
        </section>
        <section class="grid three">
          ${(data.unavailable_modules || []).map((item) => `<article class="card empty"><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.reason)}</p><span class="chip">unavailable</span></article>`).join("")}
        </section>`;
    }

    function list(items, empty) {
      return items.length ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : `<p>${empty}</p>`;
    }
    function formatBytes(bytes) { return bytes ? `${(bytes / 1024 / 1024).toFixed(bytes > 1048576 ? 1 : 2)} MB` : "0 MB"; }
    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[char]));
    }
    loadDashboard().catch((error) => { document.getElementById("dashboard").textContent = error.message; });
  </script>
</body>
</html>
"""
