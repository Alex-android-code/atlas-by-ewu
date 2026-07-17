"""Employer experience page."""

from api.components.brand_logo import BRAND_LOGO_CSS, BRAND_MARK_HTML
from api.components.design_system import ATLAS_DESIGN_SYSTEM_CSS
from api.observability import observability_body_html, observability_head_html


EMPLOYER_HTML = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="atlas-title-key" content="employer.hero_title" />
  <title>ATLAS Employer Coordinator</title>
  <link rel="icon" href="/static/assets/atlas_brand_icon.png" type="image/png" />
  {observability_head_html()}
  <style>
    :root {{
      --atlas-navy: #0B132B;
      --atlas-dark: #1A2338;
      --atlas-slate: #2E3A4F;
      --atlas-gold: #D4AF37;
      --atlas-gold-light: #F5D98A;
      --atlas-light: #E6E8EB;
      --atlas-white: #FFFFFF;
      --atlas-green: #20c787;
      --atlas-red: #ef4444;
      --atlas-warning: #F5D98A;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, Poppins, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 50% 0%, rgba(212,175,55,0.08), transparent 28%),
        var(--atlas-navy);
      color: var(--atlas-white);
    }}
    {BRAND_LOGO_CSS}
    {ATLAS_DESIGN_SYSTEM_CSS}
    header {{
      min-height: 76px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px clamp(16px, 3vw, 34px);
      background: rgba(11, 19, 43, 0.92);
      border-bottom: 1px solid rgba(230,232,235,0.10);
      backdrop-filter: blur(18px);
      position: sticky;
      top: 0;
      z-index: 5;
    }}
    nav {{ display: flex; align-items: center; gap: 18px; color: var(--atlas-light); font-size: 14px; font-weight: 500; }}
    nav a {{ color: inherit; text-decoration: none; }}
    nav a:hover, nav a.active {{ color: var(--atlas-gold); }}
    .login-link {{ border: 1px solid var(--atlas-gold); border-radius: 999px; padding: 9px 14px; color: var(--atlas-gold); }}
    .language-selector {{ position: relative; }}
    .language-button {{ display: inline-flex; align-items: center; gap: 8px; border: 0; background: transparent; color: inherit; font: inherit; cursor: pointer; padding: 0; }}
    .language-current {{ color: var(--atlas-gold); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    .language-menu {{ position: absolute; top: 28px; right: 0; z-index: 10; min-width: 220px; display: none; padding: 8px; border: 1px solid rgba(212,175,55,0.28); border-radius: 16px; background: rgba(11,19,43,0.98); }}
    .language-menu.open {{ display: grid; gap: 4px; }}
    .language-option {{ min-height: 42px; border: 0; border-radius: 10px; background: transparent; color: var(--atlas-light); font: inherit; text-align: left; cursor: pointer; padding: 0 10px; }}
    .language-option:hover, .language-option.active {{ background: rgba(212,175,55,0.12); color: var(--atlas-white); }}
    main {{
      min-height: calc(100vh - 76px);
      display: grid;
      grid-template-columns: minmax(0, 1fr) 390px;
    }}
    .conversation {{
      min-height: calc(100vh - 76px);
      display: grid;
      grid-template-rows: auto 1fr auto;
    }}
    .intro {{ padding: clamp(20px, 4vw, 34px) clamp(18px, 5vw, 56px) 10px; }}
    .intro h1 {{ margin: 0 0 10px; font-size: clamp(30px, 5vw, 56px); line-height: 1.02; letter-spacing: 0; }}
    .intro p {{ margin: 0; max-width: 720px; color: rgba(230,232,235,0.74); font-size: 17px; line-height: 1.5; }}
    .messages {{ padding: 22px clamp(18px, 5vw, 56px); display: flex; flex-direction: column; gap: 14px; overflow: auto; }}
    .message {{ max-width: min(760px, 92%); padding: 15px 17px; border-radius: 18px; line-height: 1.55; white-space: pre-wrap; }}
    .assistant {{ align-self: flex-start; background: rgba(26,35,56,0.94); border: 1px solid rgba(212,175,55,0.28); border-left: 3px solid var(--atlas-gold); color: var(--atlas-light); }}
    .user {{ align-self: flex-end; background: var(--atlas-slate); border: 1px solid rgba(230,232,235,0.12); color: var(--atlas-white); }}
    .composer {{ padding: 16px clamp(18px, 5vw, 56px); background: rgba(11,19,43,0.94); border-top: 1px solid rgba(230,232,235,0.10); }}
    .inputbar {{ display: grid; grid-template-columns: 1fr auto; gap: 10px; background: rgba(26,35,56,0.96); border: 1px solid rgba(230,232,235,0.14); border-radius: 18px; padding: 8px; }}
    .inputbar:focus-within {{ border-color: var(--atlas-gold); }}
    textarea {{ border: 0; resize: none; min-height: 52px; max-height: 160px; padding: 13px 12px; background: transparent; color: var(--atlas-white); font: inherit; outline: 0; }}
    .send {{ border: 0; min-width: 54px; border-radius: 14px; background: var(--atlas-gold); color: var(--atlas-navy); font-weight: 850; cursor: pointer; }}
    .panel {{
      min-height: calc(100vh - 76px);
      padding: 18px;
      display: grid;
      align-content: start;
      gap: 14px;
      background: rgba(26,35,56,0.74);
      border-left: 1px solid rgba(230,232,235,0.10);
    }}
    .card {{ border: 1px solid rgba(230,232,235,0.10); border-radius: 16px; background: rgba(255,255,255,0.055); padding: 15px; display: grid; gap: 12px; }}
    .card h2 {{ margin: 0; font-size: 15px; }}
    .score {{ display: flex; align-items: end; justify-content: space-between; gap: 16px; }}
    .score strong {{ color: var(--atlas-gold); font-size: 38px; line-height: 1; }}
    .score span {{ color: rgba(230,232,235,0.72); font-size: 13px; }}
    .field {{ display: flex; justify-content: space-between; gap: 12px; color: var(--atlas-light); font-size: 13px; }}
    .field span:first-child {{ color: rgba(230,232,235,0.66); }}
    .field strong {{ text-align: right; color: var(--atlas-white); }}
    .advice {{ display: grid; gap: 9px; }}
    .advice-item {{ border-radius: 12px; padding: 11px 12px; background: rgba(212,175,55,0.10); border: 1px solid rgba(212,175,55,0.22); color: var(--atlas-light); font-size: 13px; }}
    .advice-item.ok {{ background: rgba(32,199,135,0.10); border-color: rgba(32,199,135,0.22); }}
    .advice-item.warning {{ background: rgba(245,217,138,0.10); }}
    .pipeline {{ display: grid; gap: 9px; }}
    .step {{ display: flex; align-items: center; gap: 10px; color: rgba(230,232,235,0.62); font-size: 13px; }}
    .dot {{ width: 20px; height: 20px; border-radius: 999px; display: grid; place-items: center; border: 1px solid rgba(230,232,235,0.22); color: rgba(230,232,235,0.68); font-size: 11px; }}
    .step.complete {{ color: var(--atlas-white); }}
    .step.complete .dot {{ background: var(--atlas-green); border-color: var(--atlas-green); color: var(--atlas-navy); }}
    .step.active .dot {{ background: var(--atlas-gold); border-color: var(--atlas-gold); color: var(--atlas-navy); }}
    .metrics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }}
    .metric {{ border: 1px solid rgba(230,232,235,0.10); border-radius: 12px; padding: 10px; background: rgba(11,19,43,0.32); }}
    .metric span {{ display: block; color: rgba(230,232,235,0.64); font-size: 11px; }}
    .metric strong {{ color: var(--atlas-white); font-size: 22px; }}
    @media (max-width: 1080px) {{
      main {{ grid-template-columns: 1fr; }}
      .panel {{ min-height: auto; border-left: 0; border-top: 1px solid rgba(230,232,235,0.10); }}
    }}
    @media (max-width: 760px) {{
      header {{ align-items: flex-start; flex-direction: column; }}
      nav {{ width: 100%; flex-wrap: nowrap; gap: 6px; }}
      main {{ padding: 10px; gap: 12px; }}
      .intro {{ padding: 22px 16px 8px; }}
      .intro h1 {{ font-size: 30px; }}
      .intro p {{ font-size: 15px; }}
      .messages {{ padding: 14px 16px; }}
      .composer {{ padding: 12px; }}
      .panel {{ padding: 10px; gap: 10px; }}
      .metrics {{ grid-template-columns: 1fr; }}
    }}
    header {{
      min-height: 72px;
    }}
    main {{
      max-width: 1440px;
      margin: 0 auto;
      grid-template-columns: minmax(0, 1.35fr) minmax(340px, 0.65fr);
      gap: 16px;
      padding: 16px;
    }}
    .conversation, .panel {{
      min-height: calc(100vh - 104px);
      border: 1px solid var(--atlas-line);
      border-radius: 18px;
      background: rgba(255,255,255,0.035);
      overflow: hidden;
    }}
    .panel {{
      border-left: 1px solid var(--atlas-line);
      padding: 14px;
      background: rgba(255,255,255,0.028);
    }}
    .intro {{
      padding: 28px clamp(18px, 4vw, 44px) 12px;
    }}
    .intro h1 {{
      font-weight: 760;
      letter-spacing: -0.014em;
    }}
    .intro p {{
      color: var(--atlas-muted);
    }}
    .messages {{
      padding: 18px clamp(18px, 4vw, 44px);
    }}
    .message {{
      border-radius: 16px;
      box-shadow: none;
    }}
    .assistant {{
      background: rgba(255,255,255,0.055);
      border: 1px solid var(--atlas-line);
      border-left: 1px solid var(--atlas-line);
    }}
    .user {{
      background: rgba(214,178,94,0.13);
      border: 1px solid rgba(214,178,94,0.26);
    }}
    .composer {{
      background: rgba(5,7,13,0.58);
    }}
    .inputbar {{
      border-radius: 16px;
      background: rgba(255,255,255,0.045);
    }}
    .card {{
      border-radius: 16px;
    }}
    .advice-item, .metric {{
      border-radius: 12px;
      background: rgba(255,255,255,0.045);
      border-color: var(--atlas-line);
    }}
    .score strong {{
      color: var(--atlas-platinum);
      font-weight: 760;
    }}
    @media (max-width: 1080px) {{
      main {{
        grid-template-columns: 1fr;
      }}
      .conversation, .panel {{
        min-height: auto;
      }}
    }}
  </style>
</head>
<body>
  <header>
    {BRAND_MARK_HTML}
    <nav aria-label="Main navigation">
      <a href="/ai?intent=job" data-i18n="nav.jobs">Jobs</a>
      <a class="active" href="/employer" data-i18n="nav.employers">Employers</a>
      <a href="/ai" data-i18n="nav.coordinator">Coordinator</a>
      <a href="/" data-i18n="nav.about">About</a>
      <div class="language-selector" data-language-selector>
        <button class="language-button" type="button" aria-expanded="false" data-language-button>
          <span data-i18n="nav.languages">Languages</span>
          <span class="language-current" data-language-current>EN</span>
        </button>
        <div class="language-menu" role="menu" data-language-menu></div>
      </div>
      <a class="login-link" href="/login" data-i18n="nav.login">Login</a>
    </nav>
  </header>
  <main>
    <section class="conversation">
      <div class="intro">
        <h1 data-i18n="employer.hero_title">Your recruitment coordinator</h1>
        <p data-i18n="employer.hero_subtitle">Create stronger vacancies, receive live recommendations and start hiring with confidence.</p>
      </div>
      <div class="messages" id="messages"></div>
      <form class="composer" id="form">
        <div class="inputbar">
          <textarea id="message" data-i18n-placeholder="employer.placeholder" placeholder="Describe who you need to hire..."></textarea>
          <button class="send" type="submit" data-i18n-aria-label="coordinator.send">↑</button>
        </div>
      </form>
    </section>
    <aside class="panel">
      <div class="card">
        <h2 data-i18n="employer.dashboard_title">Employer Dashboard</h2>
        <div class="metrics" id="metrics"></div>
      </div>
      <div class="card">
        <h2 data-i18n="employer.vacancy_card">Vacancy Card</h2>
        <div id="vacancy-card"></div>
      </div>
      <div class="card">
        <h2 data-i18n="employer.vacancy_quality">Vacancy Quality</h2>
        <div id="quality"></div>
      </div>
      <div class="card">
        <h2 data-i18n="employer.advice_cards">Live Advice</h2>
        <div class="advice" id="advice"></div>
      </div>
      <div class="card">
        <h2 data-i18n="employer.trust_score">Employer Trust Score</h2>
        <div id="trust"></div>
      </div>
      <div class="card">
        <h2 data-i18n="employer.match_progress">Match Progress</h2>
        <div class="pipeline" id="pipeline"></div>
      </div>
    </aside>
  </main>
  {observability_body_html("employer")}
  <script src="/static/i18n.js?v=20260711-langfix"></script>
  <script>
    const userId = localStorage.getItem("atlas_employer_user_id") || `employer-${{crypto.randomUUID()}}`;
    localStorage.setItem("atlas_employer_user_id", userId);
    const messages = document.getElementById("messages");
    const input = document.getElementById("message");
    const form = document.getElementById("form");
    const sendButton = form.querySelector("button[type='submit']");
    let isSending = false;
    const metrics = document.getElementById("metrics");
    const vacancyCard = document.getElementById("vacancy-card");
    const quality = document.getElementById("quality");
    const advice = document.getElementById("advice");
    const trust = document.getElementById("trust");
    const pipeline = document.getElementById("pipeline");

    function tr(key) {{ return window.AtlasI18n ? window.AtlasI18n.t(key) : key; }}
    function translateValue(value) {{ return typeof value === "string" && value.includes(".") ? tr(value) : value; }}
    function dash(value) {{ return value === undefined || value === null || value === "" ? "-" : value; }}
    function addMessage(role, text) {{
      const item = document.createElement("div");
      item.className = `message ${{role}}`;
      item.textContent = text;
      messages.appendChild(item);
      messages.scrollTop = messages.scrollHeight;
    }}
    function field(labelKey, value) {{
      return `<div class="field"><span>${{tr(labelKey)}}</span><strong>${{dash(Array.isArray(value) ? value.join(", ") : value)}}</strong></div>`;
    }}
    function renderExperience(exp) {{
      const vacancy = exp?.vacancy_card || {{}};
      vacancyCard.innerHTML = [
        field("employer.vacancy_id", vacancy.id),
        field("employer.profession", vacancy.profession),
        field("employer.quantity", vacancy.quantity),
        field("employer.country", vacancy.country),
        field("employer.salary", vacancy.salary),
        field("employer.housing", vacancy.housing === true ? tr("common.yes") : vacancy.housing === false ? tr("common.no") : "-"),
        field("employer.transport", vacancy.transport === true ? tr("common.yes") : vacancy.transport === false ? tr("common.no") : "-"),
        field("employer.start_date", vacancy.start_date),
        field("employer.requirements", vacancy.requirements)
      ].join("");

      const q = exp?.vacancy_quality || {{ score: 0, status: "needs_work" }};
      quality.innerHTML = `<div class="score"><strong>${{q.score || 0}} / 100</strong><span>${{tr(`quality.${{q.status || "needs_work"}}`)}}</span></div>`;

      const cards = exp?.advice_cards || [{{ key: "advisor.missing_profession", severity: "info" }}];
      advice.innerHTML = cards.map(card => `<div class="advice-item ${{card.severity}}">${{tr(card.key)}}</div>`).join("");

      const trustData = exp?.trust_score || {{ score: 0, status: "under_review" }};
      trust.innerHTML = `<div class="score"><strong>${{trustData.score || 0}} / 100</strong><span>${{tr(`trust.status.${{trustData.status || "under_review"}}`)}}</span></div>`;

      const dashData = exp?.dashboard || {{}};
      metrics.innerHTML = [
        ["employer.active_vacancies", dashData.active_vacancies || 0],
        ["employer.candidates_in_progress", dashData.candidates_in_progress || 0],
        ["employer.ready_to_start", dashData.ready_to_start || 0],
        ["employer.interviews", dashData.interviews || 0],
        ["employer.document_risks", dashData.document_risks || 0],
        ["employer.completed_projects", dashData.completed_projects || 0]
      ].map(([key, value]) => `<div class="metric"><span>${{tr(key)}}</span><strong>${{value}}</strong></div>`).join("");

      const steps = dashData.match_progress || [
        {{ key: "pipeline.need", status: "active" }},
        {{ key: "pipeline.found", status: "pending" }},
        {{ key: "pipeline.verified", status: "pending" }},
        {{ key: "pipeline.recommended", status: "pending" }},
        {{ key: "pipeline.accepted", status: "pending" }},
        {{ key: "pipeline.started", status: "pending" }}
      ];
      pipeline.innerHTML = steps.map(step => `<div class="step ${{step.status}}"><span class="dot">${{step.status === "complete" ? "✓" : step.status === "active" ? "•" : ""}}</span><span>${{tr(step.key)}}</span></div>`).join("");
    }}
    async function send(text) {{
      if (isSending) return;
      isSending = true;
      sendButton.disabled = true;
      const detectedConversationLanguage = window.AtlasI18n?.detectConversationLanguageFromText(text);
      if (detectedConversationLanguage && detectedConversationLanguage !== "unknown") {{
        window.AtlasI18n?.setConversationLanguage(detectedConversationLanguage);
      }}
      addMessage("user", text);
      input.value = "";
      addMessage("assistant", tr("coordinator.typing"));
      try {{
        const res = await fetch("/api/ai/chat", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{
            user_id: userId,
            agent_type: "employer",
            message: text,
            browser_language: navigator.language,
            saved_language: localStorage.getItem("atlas_language"),
            ui_language: window.AtlasI18n?.state?.uiLanguage || localStorage.getItem("atlas_language"),
            conversation_language: window.AtlasI18n?.state?.conversationLanguage || detectedConversationLanguage
          }})
        }});
        const data = await res.json();
        messages.lastChild.textContent = data.reply || tr("coordinator.welcome");
        renderExperience(data.employer_experience || data.profile?.employer_experience || {{}});
      }} catch (error) {{
        messages.lastChild.textContent = tr("coordinator.welcome");
      }} finally {{
        isSending = false;
        sendButton.disabled = false;
      }}
    }}
    form.addEventListener("submit", async (event) => {{
      event.preventDefault();
      const text = input.value.trim();
      if (text) await send(text);
    }});
    function boot() {{
      messages.innerHTML = "";
      addMessage("assistant", tr("employer.initial_message"));
      renderExperience({{}});
    }}
    document.addEventListener("atlas:i18n", boot);
    window.AtlasI18n.init().then(boot);
  </script>
</body>
</html>
"""
