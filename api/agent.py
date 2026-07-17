"""Personal AI agent onboarding and dashboard screens."""

AGENT_ONBOARDING_HTML = r"""
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS AI Agent Onboarding</title>
  <style>
    :root {
      --bg: #020714;
      --panel: rgba(255,255,255,0.055);
      --line: rgba(238,241,246,0.14);
      --gold: #d4af37;
      --text: #eef1f6;
      --muted: rgba(238,241,246,0.68);
      --platinum: #cfd6e6;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 20% 0%, rgba(212,175,55,0.16), transparent 28%),
        radial-gradient(circle at 80% 12%, rgba(76,154,255,0.18), transparent 30%),
        linear-gradient(180deg, #020714, #071224 58%, #020714);
    }
    main {
      width: min(960px, 100%);
      margin: 0 auto;
      padding: calc(28px + env(safe-area-inset-top)) clamp(16px, 4vw, 40px) 40px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: clamp(28px, 7vw, 72px);
    }
    .brand {
      color: var(--platinum);
      font-weight: 800;
      letter-spacing: 0.18em;
      font-size: 18px;
    }
    .badge {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      font-size: 13px;
      background: rgba(255,255,255,0.04);
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: clamp(22px, 5vw, 44px);
      background: linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.035));
      box-shadow: 0 32px 90px rgba(0,0,0,0.34);
    }
    .eyebrow {
      color: var(--gold);
      font-size: 13px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      margin: 0 0 14px;
    }
    h1 {
      max-width: 780px;
      margin: 0;
      font-size: clamp(34px, 8vw, 76px);
      line-height: 0.98;
      letter-spacing: 0;
    }
    .lead {
      max-width: 680px;
      margin: 20px 0 0;
      color: var(--muted);
      font-size: clamp(16px, 2.4vw, 20px);
      line-height: 1.6;
    }
    .progress {
      height: 8px;
      margin: 28px 0;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255,255,255,0.09);
    }
    .progress span {
      display: block;
      width: 0%;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #9f7e22, #f5d56a, #b88720);
      transition: width 260ms ease;
    }
    label {
      display: block;
      margin: 0 0 10px;
      color: var(--text);
      font-size: clamp(22px, 5vw, 34px);
      font-weight: 760;
      line-height: 1.15;
    }
    .why {
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.55;
    }
    textarea, input {
      width: 100%;
      min-height: 64px;
      border: 1px solid rgba(238,241,246,0.18);
      border-radius: 18px;
      padding: 18px;
      color: var(--text);
      background: rgba(2,7,20,0.72);
      outline: none;
      font: inherit;
      resize: vertical;
    }
    textarea:focus, input:focus {
      border-color: rgba(212,175,55,0.68);
      box-shadow: 0 0 0 4px rgba(212,175,55,0.12);
    }
    .actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 20px;
    }
    button, .button {
      min-height: 54px;
      border: 0;
      border-radius: 16px;
      padding: 0 20px;
      cursor: pointer;
      font-weight: 760;
      text-decoration: none;
      display: inline-grid;
      place-items: center;
    }
    .primary {
      color: #130f05;
      background: linear-gradient(135deg, #ffe27a, #d4af37 52%, #a97818);
      box-shadow: 0 18px 45px rgba(212,175,55,0.24);
    }
    .secondary {
      color: var(--text);
      background: rgba(255,255,255,0.06);
      border: 1px solid var(--line);
    }
    .complete {
      display: none;
      margin-top: 18px;
      color: var(--platinum);
      line-height: 1.55;
    }
    @media (max-width: 520px) {
      header { align-items: flex-start; flex-direction: column; }
      .actions > * { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">ATLAS by EWU</div>
      <div class="badge" id="step-badge">1 / 15</div>
    </header>
    <section class="panel">
      <p class="eyebrow">Personal AI Agent</p>
      <h1>Створити свого AI-агента</h1>
      <p class="lead">ATLAS починає не з анкети, а з першого інтерв'ю. Ваш агент поступово формує Professional DNA і запам'ятовує важливі відповіді.</p>
      <div class="progress"><span id="progress-bar"></span></div>
      <form id="onboarding-form">
        <label id="question" for="answer"></label>
        <p class="why" id="why"></p>
        <textarea id="answer" autocomplete="off"></textarea>
        <div class="actions">
          <button class="secondary" id="back" type="button">Назад</button>
          <button class="primary" type="submit">Зберегти відповідь</button>
          <a class="secondary button" href="/agent/dashboard">У мене вже є агент</a>
        </div>
      </form>
      <div class="complete" id="complete">
        Ваш AI-агент створений. Тепер він починає формувати вашу професійну карту.
        <div class="actions"><a class="primary button" href="/agent/dashboard">Відкрити dashboard агента</a></div>
      </div>
    </section>
  </main>
  <script>
    const params = new URLSearchParams(location.search);
    const language = params.get("lang") || localStorage.getItem("atlas_language") || "uk";
    const userId = localStorage.getItem("atlas_user_id") || `user-${crypto.randomUUID()}`;
    localStorage.setItem("atlas_user_id", userId);
    let fields = [];
    let index = Number(localStorage.getItem("atlas_agent_onboarding_index") || 0);
    const answers = JSON.parse(localStorage.getItem("atlas_agent_onboarding_answers") || "{}");
    const question = document.getElementById("question");
    const why = document.getElementById("why");
    const answer = document.getElementById("answer");
    const badge = document.getElementById("step-badge");
    const bar = document.getElementById("progress-bar");
    const back = document.getElementById("back");
    const complete = document.getElementById("complete");
    const form = document.getElementById("onboarding-form");

    async function loadSchema() {
      const response = await fetch(`/api/agent/onboarding/schema?language=${encodeURIComponent(language)}`);
      const data = await response.json();
      fields = data.fields;
      render();
    }

    function render() {
      const field = fields[index];
      if (!field) return;
      question.textContent = field.question;
      why.textContent = field.why;
      answer.value = answers[field.key] || "";
      badge.textContent = `${field.step} / ${field.total}`;
      bar.style.width = `${Math.round((index / fields.length) * 100)}%`;
      back.disabled = index === 0;
    }

    back.addEventListener("click", () => {
      if (index > 0) {
        index -= 1;
        localStorage.setItem("atlas_agent_onboarding_index", String(index));
        render();
      }
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const field = fields[index];
      answers[field.key] = answer.value.trim();
      localStorage.setItem("atlas_agent_onboarding_answers", JSON.stringify(answers));
      await fetch("/api/agent/onboarding/answer", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id: userId, field: field.key, value: answers[field.key], language})
      });
      if (index < fields.length - 1) {
        index += 1;
        localStorage.setItem("atlas_agent_onboarding_index", String(index));
        render();
      } else {
        await fetch("/api/agent/onboarding/complete", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({user_id: userId})
        });
        bar.style.width = "100%";
        form.style.display = "none";
        complete.style.display = "block";
      }
    });

    loadSchema();
  </script>
</body>
</html>
"""


AGENT_DASHBOARD_HTML = r"""
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS AI Agent Dashboard</title>
  <style>
    :root {
      --bg: #020714;
      --panel: rgba(255,255,255,0.06);
      --line: rgba(238,241,246,0.14);
      --gold: #d4af37;
      --text: #eef1f6;
      --muted: rgba(238,241,246,0.68);
      --platinum: #cfd6e6;
    }
    * { box-sizing: border-box; min-width: 0; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 20% -10%, rgba(212,175,55,0.15), transparent 26%),
        radial-gradient(circle at 80% 0%, rgba(76,154,255,0.13), transparent 28%),
        #020714;
    }
    main {
      width: min(1180px, 100%);
      margin: 0 auto;
      padding: calc(24px + env(safe-area-inset-top)) clamp(16px, 4vw, 40px) 40px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 26px;
    }
    .brand { color: var(--platinum); font-weight: 800; letter-spacing: 0.18em; }
    .button {
      min-height: 44px;
      border-radius: 14px;
      padding: 0 16px;
      display: inline-grid;
      place-items: center;
      color: #130f05;
      background: linear-gradient(135deg, #ffe27a, #d4af37 52%, #a97818);
      text-decoration: none;
      font-weight: 760;
    }
    .hero {
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 18px;
      align-items: stretch;
    }
    .panel, .card {
      border: 1px solid var(--line);
      border-radius: 24px;
      background: linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.035));
      box-shadow: 0 26px 80px rgba(0,0,0,0.28);
    }
    .panel { padding: clamp(22px, 4vw, 38px); }
    .eyebrow { color: var(--gold); text-transform: uppercase; letter-spacing: 0.16em; font-size: 12px; margin: 0 0 12px; }
    h1 { margin: 0; font-size: clamp(34px, 7vw, 72px); line-height: 1; letter-spacing: 0; }
    .lead { color: var(--muted); max-width: 680px; line-height: 1.6; font-size: clamp(16px, 2vw, 19px); }
    .meter { height: 10px; overflow: hidden; border-radius: 999px; background: rgba(255,255,255,0.09); }
    .meter span { display: block; width: 0%; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #9f7e22, #f5d56a, #b88720); }
    .status { color: var(--platinum); font-size: 18px; font-weight: 760; }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 16px;
    }
    .card { padding: 18px; }
    .card h2, .card h3 { margin: 0 0 10px; }
    .card p, li { color: var(--muted); line-height: 1.55; }
    ul { padding-left: 18px; margin: 0; }
    .tag {
      display: inline-flex;
      margin-top: 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      color: var(--muted);
      font-size: 12px;
    }
    @media (max-width: 860px) {
      .hero, .grid { grid-template-columns: 1fr; }
      header { align-items: flex-start; flex-direction: column; }
      .button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">ATLAS by EWU</div>
      <a class="button" href="/agent/onboarding">Продовжити інтерв'ю</a>
    </header>
    <section class="hero">
      <div class="panel">
        <p class="eyebrow">Personal AI Agent</p>
        <h1>Ваш AI-агент</h1>
        <p class="lead" id="agent-activity">Завантажую стан агента...</p>
        <p class="status" id="agent-status"></p>
        <div class="meter"><span id="dna-meter"></span></div>
        <p class="lead" id="next-action"></p>
      </div>
      <div class="panel">
        <p class="eyebrow">Professional DNA</p>
        <h2 id="dna-percent">0%</h2>
        <p class="lead">Це не CV, а цифровий професійний профіль, який агент поступово наповнює фактами, цілями, документами та рекомендаціями.</p>
        <span class="tag">Тестовий режим</span>
      </div>
    </section>
    <section class="grid" id="modules"></section>
  </main>
  <script>
    const userId = localStorage.getItem("atlas_user_id") || `user-${crypto.randomUUID()}`;
    localStorage.setItem("atlas_user_id", userId);

    async function loadDashboard() {
      const response = await fetch(`/api/agent/dashboard/${encodeURIComponent(userId)}`);
      const data = await response.json();
      document.getElementById("agent-activity").textContent = data.agent.activity;
      document.getElementById("agent-status").textContent = data.agent.status;
      document.getElementById("next-action").textContent = data.agent.next_recommended_action;
      document.getElementById("dna-percent").textContent = `${data.agent.profile_completeness}%`;
      document.getElementById("dna-meter").style.width = `${data.agent.profile_completeness}%`;
      const modules = document.getElementById("modules");
      modules.innerHTML = "";
      data.modules.forEach((module) => {
        const card = document.createElement("article");
        card.className = "card";
        card.innerHTML = `<h3>${module.title}</h3><p>${descriptionFor(module.key)}</p><span class="tag">${statusLabel(module.status)}</span>`;
        modules.appendChild(card);
      });
    }

    function statusLabel(status) {
      if (status === "active") return "Працює";
      if (status === "test_mode") return "Тестовий режим";
      return "У розробці";
    }

    function descriptionFor(key) {
      const descriptions = {
        my_ai_agent: "Статус агента, остання активність, журнал дій і можливість почати діалог.",
        professional_dna: "Професійний профіль, відсоток заповнення, відсутні дані та статус перевірки.",
        opportunities: "Рекомендовані вакансії, навчання, сертифікації та варіанти релокації.",
        documents: "CV, сертифікати, дозволи, строки дії документів і попередження.",
        career_strategy: "Поточна мета, рекомендовані кроки, прогрес і наступна дія.",
        agent_settings: "Мова, тон спілкування, країни пошуку, тип роботи і автономність агента."
      };
      return descriptions[key] || "";
    }

    loadDashboard();
  </script>
</body>
</html>
"""
