"""Coordinator dashboard HTML."""

from api.components.brand_logo import BRAND_LOGO_CSS, BRAND_LOGO_HTML
from api.observability import observability_body_html, observability_head_html


DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="atlas-title-key" content="dashboard.title" />
  <title>ATLAS by EWU Coordinator Dashboard</title>
  <link rel="icon" href="/static/assets/atlas_brand_icon.png" type="image/png" />
  {{OBSERVABILITY_HEAD}}
  <style>
    :root {
      color-scheme: dark;
      --atlas-navy: #0B132B;
      --atlas-dark: #1A2338;
      --atlas-slate: #2E3A4F;
      --atlas-gold: #D4AF37;
      --atlas-gold-light: #F5D98A;
      --atlas-light: #E6E8EB;
      --atlas-white: #FFFFFF;
      --risk: #ef4444;
      --ok: #20c787;
      --warning: #facc15;
      --line: rgba(230,232,235,0.12);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Poppins, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 20% 0%, rgba(212,175,55,0.10), transparent 28%),
        var(--atlas-navy);
      color: var(--atlas-white);
    }
    {{BRAND_LOGO_CSS}}
    header {
      padding: 18px 28px;
      background: rgba(11,19,43,0.92);
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 5;
      backdrop-filter: blur(18px);
    }
    h1 { margin: 0; font-size: 22px; }
    .brand-title {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .top-nav {
      display: flex;
      align-items: center;
      gap: 18px;
      color: var(--atlas-light);
      font-size: 14px;
      font-weight: 500;
    }
    .top-nav a {
      color: inherit;
      text-decoration: none;
    }
    .top-nav a:hover, .top-nav a.active {
      color: var(--atlas-gold);
    }
    .top-nav .login-link {
      border: 1px solid var(--atlas-gold);
      border-radius: 999px;
      padding: 9px 14px;
      color: var(--atlas-gold);
    }
    .language-selector { position: relative; }
    .language-button {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 0;
      background: transparent;
      color: inherit;
      font: inherit;
      cursor: pointer;
      padding: 0;
    }
    .language-current { color: var(--atlas-gold); font-size: 12px; font-weight: 800; text-transform: uppercase; }
    .language-menu {
      position: absolute;
      top: 28px;
      right: 0;
      z-index: 10;
      min-width: 220px;
      display: none;
      padding: 8px;
      border: 1px solid rgba(212,175,55,0.28);
      border-radius: 16px;
      background: rgba(11,19,43,0.98);
    }
    .language-menu.open { display: grid; gap: 4px; }
    .language-option {
      min-height: 42px;
      border: 0;
      border-radius: 10px;
      background: transparent;
      color: var(--atlas-light);
      font: inherit;
      text-align: left;
      cursor: pointer;
      padding: 0 10px;
    }
    .language-option:hover, .language-option.active { background: rgba(212,175,55,0.12); color: var(--atlas-white); }
    h2 {
      margin: 0;
      padding: 14px 16px;
      font-size: 16px;
      border-bottom: 1px solid var(--line);
      color: var(--atlas-white);
    }
    main {
      padding: 24px 28px;
      display: grid;
      gap: 20px;
    }
    .dashboard-intro {
      padding: 18px;
    }
    .dashboard-intro h1 {
      font-size: 30px;
      margin-bottom: 8px;
    }
    .toolbar, .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }
    button {
      border: 1px solid rgba(212,175,55,0.35);
      background: rgba(255,255,255,0.06);
      color: var(--atlas-white);
      padding: 9px 12px;
      border-radius: 10px;
      cursor: pointer;
      font-weight: 700;
    }
    button.primary {
      background: linear-gradient(135deg, var(--atlas-gold), var(--atlas-gold-light));
      border-color: transparent;
      color: var(--atlas-navy);
    }
    button.mini {
      padding: 5px 7px;
      font-size: 12px;
      margin: 2px;
    }
    input, select {
      width: 100%;
      border: 1px solid rgba(230,232,235,0.14);
      border-radius: 10px;
      padding: 9px 10px;
      color: var(--atlas-white);
      background: rgba(255,255,255,0.06);
      font: inherit;
      min-width: 0;
      outline: 0;
    }
    input:focus, select:focus { border-color: var(--atlas-gold); }
    label {
      display: grid;
      gap: 5px;
      color: rgba(230,232,235,0.72);
      font-size: 12px;
      font-weight: 700;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(6, minmax(130px, 1fr));
      gap: 12px;
    }
    .metric, section {
      background: rgba(26,35,56,0.84);
      border: 1px solid var(--line);
      border-radius: 16px;
    }
    .metric { padding: 14px; }
    .metric span { color: rgba(230,232,235,0.70); font-size: 12px; font-weight: 600; }
    .metric strong { display: block; color: var(--atlas-gold); font-size: 30px; margin-top: 6px; }
    .forms {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }
    form {
      padding: 14px 16px 16px;
      display: grid;
      gap: 10px;
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .full { grid-column: 1 / -1; }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }
    section { overflow: hidden; }
    table { width: 100%; border-collapse: collapse; }
    th, td {
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 13px;
    }
    th { color: rgba(230,232,235,0.68); font-weight: 700; background: rgba(255,255,255,0.04); }
    .tag {
      display: inline-block;
      padding: 3px 7px;
      border-radius: 999px;
      background: rgba(212,175,55,0.12);
      color: var(--atlas-gold-light);
      font-size: 12px;
      margin: 1px;
    }
    .risk { color: var(--risk); font-weight: 700; }
    .ok { color: var(--ok); font-weight: 700; }
    .muted { color: rgba(230,232,235,0.70); }
    .status {
      min-height: 20px;
      color: rgba(230,232,235,0.70);
      font-size: 12px;
    }
    .notice {
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.06);
      border-radius: 14px;
      padding: 12px 14px;
      color: var(--atlas-light);
      font-size: 13px;
    }
    .nowrap { white-space: nowrap; }
    @media (max-width: 1180px) {
      .forms { grid-template-columns: 1fr; }
    }
    @media (max-width: 920px) {
      .metrics, .grid, .form-grid { grid-template-columns: 1fr; }
      header { align-items: flex-start; flex-direction: column; }
      .top-nav {
        width: 100%;
        justify-content: space-between;
        gap: 10px;
        overflow-x: auto;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand-title">
      {{BRAND_LOGO_HTML}}
    </div>
    <nav class="top-nav" aria-label="Main navigation">
      <a href="/ai?intent=job" data-i18n="nav.jobs">Jobs</a>
      <a href="/employer" data-i18n="nav.employers">Employers</a>
      <a class="active" href="/dashboard" data-i18n="nav.coordinator">Coordinator</a>
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
    <div class="toolbar">
      <button onclick="loadAll()" data-i18n="dashboard.refresh">Refresh</button>
      <button class="primary" onclick="seedDemo()" data-i18n="dashboard.seed_demo">Seed Demo</button>
    </div>
  </header>
  <main>
    <section class="dashboard-intro">
      <h1 data-i18n="dashboard.title">Coordinator Dashboard</h1>
      <div class="muted" data-i18n="dashboard.subtitle">Premium operations workspace for candidates, employers, vacancies, matching, document risks, and manual-contact queue.</div>
    </section>
    <div class="metrics">
      <div class="metric"><span data-i18n="dashboard.new_users">New users</span><strong id="m-users">0</strong></div>
      <div class="metric"><span data-i18n="dashboard.new_candidates">New candidates</span><strong id="m-candidates">0</strong></div>
      <div class="metric"><span data-i18n="dashboard.new_employers">New employers</span><strong id="m-employers">0</strong></div>
      <div class="metric"><span data-i18n="dashboard.open_vacancies">Open vacancies</span><strong id="m-vacancies">0</strong></div>
      <div class="metric"><span data-i18n="dashboard.strong_matches">Strong matches</span><strong id="m-matches">0</strong></div>
      <div class="metric"><span data-i18n="dashboard.risk_cases">Risk cases</span><strong id="m-risks">0</strong></div>
    </div>

    <section>
      <h2>Analytics</h2>
      <table id="analytics"></table>
    </section>

    <section>
      <h2 data-i18n="dashboard.quick_actions">Quick Actions</h2>
      <form id="match-form">
        <div class="form-grid">
          <label><span data-i18n="form.vacancy">Vacancy</span>
            <select id="match-vacancy"></select>
          </label>
          <label><span data-i18n="form.minimum_score">Minimum score</span>
            <input id="match-score" type="number" value="60" min="0" max="100" />
          </label>
        </div>
        <div class="actions">
          <button class="primary" type="submit" data-i18n="dashboard.run_matching">Run Matching</button>
          <span class="status" id="match-status"></span>
        </div>
      </form>
    </section>

    <div class="forms">
      <section>
        <h2 data-i18n="dashboard.candidates">Candidates</h2>
        <form id="candidate-form">
          <div class="form-grid">
            <label><span data-i18n="form.first_name">First name</span><input name="first_name" value="Andrii" required /></label>
            <label><span data-i18n="form.last_name">Last name</span><input name="last_name" value="Melnyk" required /></label>
            <label><span data-i18n="form.email">Email</span><input name="email" value="andrii.melnyk@example.com" required /></label>
            <label><span data-i18n="form.phone">Phone</span><input name="phone" value="+380661234567" required /></label>
            <label><span data-i18n="form.current_country">Current country</span><input name="country_code" value="UA" required /></label>
            <label><span data-i18n="form.profession">Profession</span><input name="profession_code" value="welder" required /></label>
            <label><span data-i18n="form.experience_years">Experience years</span><input name="years_of_experience" type="number" value="4" min="0" /></label>
            <label><span data-i18n="form.desired_country">Desired country</span><input name="desired_country_code" value="PL" /></label>
            <label><span data-i18n="form.desired_salary">Desired salary</span><input name="desired_salary" type="number" value="6200" min="0" /></label>
            <label><span data-i18n="form.currency">Currency</span><input name="salary_currency" value="PLN" /></label>
            <label><span data-i18n="form.ready_from">Ready from</span><input name="ready_from" value="2026-08-01" /></label>
            <label><span data-i18n="form.languages">Languages</span><input name="languages" value="uk,pl" /></label>
            <label class="full"><span data-i18n="form.document_types">Document types</span><input name="document_types" value="passport_or_id,cv" /></label>
          </div>
          <div class="actions">
            <button class="primary" type="submit" data-i18n="dashboard.create_candidate">Create Candidate</button>
            <span class="status" id="candidate-status"></span>
          </div>
        </form>
      </section>

      <section>
        <h2 data-i18n="dashboard.employers">Employers</h2>
        <form id="employer-form">
          <div class="form-grid">
            <label><span data-i18n="form.company">Company</span><input name="company_name" value="Atlas Demo Works" required /></label>
            <label><span data-i18n="form.country">Country</span><input name="country_code" value="PL" required /></label>
            <label><span data-i18n="form.email">Email</span><input name="contact_email" value="hr@atlas-demo.example" required /></label>
            <label><span data-i18n="form.phone">Phone</span><input name="contact_phone" value="+48111222333" required /></label>
            <label><span data-i18n="form.industry">Industry</span><input name="industry" value="manufacturing" required /></label>
            <label><span data-i18n="form.verified">Verified</span>
              <select name="verified">
                <option value="false" data-i18n="common.no">No</option>
                <option value="true" data-i18n="common.yes">Yes</option>
              </select>
            </label>
          </div>
          <div class="actions">
            <button class="primary" type="submit" data-i18n="dashboard.create_employer">Create Employer</button>
            <span class="status" id="employer-status"></span>
          </div>
        </form>
      </section>

      <section>
        <h2 data-i18n="dashboard.open_vacancies">Open vacancies</h2>
        <form id="vacancy-form">
          <div class="form-grid">
            <label><span data-i18n="form.employer">Employer</span>
              <select name="employer_id" id="vacancy-employer"></select>
            </label>
            <label><span data-i18n="form.title">Title</span><input name="title" value="Welder" required /></label>
            <label><span data-i18n="form.country">Country</span><input name="country_code" value="PL" required /></label>
            <label><span data-i18n="form.profession">Profession</span><input name="profession_code" value="welder" required /></label>
            <label><span data-i18n="form.salary_min">Salary min</span><input name="salary_min" type="number" value="5600" min="0" /></label>
            <label><span data-i18n="form.salary_max">Salary max</span><input name="salary_max" type="number" value="7200" min="0" /></label>
            <label><span data-i18n="form.currency">Currency</span><input name="currency" value="PLN" /></label>
            <label><span data-i18n="form.location">Location</span><input name="location" value="Poznan" /></label>
            <label><span data-i18n="form.languages">Languages</span><input name="required_languages" value="pl" /></label>
            <label><span data-i18n="form.documents">Documents</span><input name="required_documents" value="passport_or_id,cv" /></label>
            <label><span data-i18n="form.contract_type">Contract type</span><input name="contract_type" value="umowa_o_prace" /></label>
            <label><span data-i18n="form.people_needed">People needed</span><input name="people_needed" type="number" value="2" min="1" /></label>
            <label><span data-i18n="form.housing">Housing</span>
              <select name="housing">
                <option value="true" data-i18n="common.yes">Yes</option>
                <option value="false" data-i18n="common.no">No</option>
              </select>
            </label>
            <label><span data-i18n="form.salary_confirmed">Salary confirmed</span>
              <select name="salary_confirmed">
                <option value="true" data-i18n="common.yes">Yes</option>
                <option value="false" data-i18n="common.no">No</option>
              </select>
            </label>
            <label class="full"><span data-i18n="form.housing_terms">Housing terms</span><input name="housing_terms" value="Employer provides written housing terms." /></label>
            <label class="full"><span data-i18n="form.requirements">Requirements</span><input name="requirements" value="mig_mag,technical_drawing" /></label>
          </div>
          <div class="actions">
            <button class="primary" type="submit" data-i18n="dashboard.create_vacancy">Create Vacancy</button>
            <span class="status" id="vacancy-status"></span>
          </div>
        </form>
      </section>
    </div>

    <div class="notice" id="last-result" data-i18n="dashboard.ready">Ready.</div>

    <div class="grid">
      <section><h2 data-i18n="dashboard.manual_contact">Manual Contact</h2><table id="manual"></table></section>
      <section><h2 data-i18n="events.title">Event Feed</h2><table id="event-feed"></table></section>
      <section><h2>Vacancies Pending Review</h2><table id="pending-vacancies"></table></section>
      <section><h2>Latest Vacancies</h2><table id="recent-vacancies"></table></section>
      <section><h2>First 5 Vacancies Report</h2><table id="first-vacancies"></table></section>
      <section><h2>Demo/Test Records</h2><table id="demo-records"></table></section>
      <section><h2 data-i18n="dashboard.new_employers">New Employers</h2><table id="employers"></table></section>
      <section><h2 data-i18n="dashboard.risk_cases">Risk Cases</h2><table id="risks"></table></section>
      <section><h2 data-i18n="dashboard.open_vacancies">Open Vacancies</h2><table id="vacancies"></table></section>
      <section><h2 data-i18n="dashboard.strong_matches">Strong Matches</h2><table id="matches"></table></section>
      <section><h2 data-i18n="dashboard.activity_log">Activity Log</h2><table id="activity"></table></section>
    </div>
  </main>
  {{OBSERVABILITY_BODY}}
  <script src="/static/i18n.js?v=20260711-langfix"></script>
  <script>
    let currentEmployers = [];
    let currentVacancies = [];
    function tr(key) {
      return window.AtlasI18n ? window.AtlasI18n.t(key) : key;
    }

    function splitList(value) {
      return String(value || "").split(/[,\\n]+/).map(item => item.trim()).filter(Boolean);
    }
    function tags(items) {
      if (!items) return "";
      const normalized = Array.isArray(items) ? items : String(items).split(/[ ,]+/).filter(Boolean);
      return normalized.map(item => `<span class="tag">${escapeHtml(item)}</span>`).join("");
    }
    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", "\\\"": "&quot;", "'": "&#039;"
      }[char]));
    }
    function formData(form) {
      return Object.fromEntries(new FormData(form).entries());
    }
    function renderTable(id, headers, rows) {
      const table = document.getElementById(id);
      const head = `<tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>`;
      const body = rows.length
        ? rows.join("")
        : `<tr><td colspan="${headers.length}" class="muted">${tr("errors.translation_missing")}</td></tr>`;
      table.innerHTML = head + body;
    }
    function eventLabel(item) {
      const labels = {
        user: `[NEW] ${tr("events.new_user")}`,
        candidate: `[CAN] ${tr("events.new_candidate")}`,
        employer: `[EMP] ${tr("events.new_employer")}`,
        risk: `[RISK] ${tr("events.document_risk")}`,
        match: `[MATCH] ${tr("events.strong_match")}`,
        contact: `[CALL] ${tr("events.manual_contact")}`,
        coordinator: `[REC] ${tr("events.coordinator_recommendation")}`
      };
      return labels[item.type] || item.label;
    }
    function setStatus(id, message) {
      document.getElementById(id).textContent = message;
      document.getElementById("last-result").textContent = message;
    }
    async function postJson(url, payload) {
      return sendJson("POST", url, payload);
    }
    async function patchJson(url, payload) {
      return sendJson("PATCH", url, payload);
    }
    async function sendJson(method, url, payload) {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      return data;
    }
    function actionButtons(actions) {
      return `<span class="nowrap">${actions.map(action =>
        `<button class="mini" type="button" onclick="${action.onclick}">${action.label}</button>`
      ).join("")}</span>`;
    }
    async function loadAll() {
      const [dashboardRes, employersRes, vacanciesRes] = await Promise.all([
        fetch("/api/dashboard"),
        fetch("/api/employers"),
        fetch("/api/vacancies")
      ]);
      const data = await dashboardRes.json();
      currentEmployers = await employersRes.json();
      currentVacancies = await vacanciesRes.json();
      renderDashboard(data);
      renderSelects();
    }
    function renderSelects() {
      const employerSelect = document.getElementById("vacancy-employer");
      employerSelect.innerHTML = currentEmployers.length
        ? currentEmployers.map(e => `<option value="${e.id}">${escapeHtml(e.company_name)} (${e.country_code})</option>`).join("")
        : `<option value="">${tr("dashboard.create_employer")}</option>`;

      const vacancySelect = document.getElementById("match-vacancy");
      vacancySelect.innerHTML = currentVacancies.length
        ? currentVacancies.map(v => `<option value="${v.id}">${escapeHtml(v.title)} (${v.country_code})</option>`).join("")
        : `<option value="">${tr("dashboard.create_vacancy")}</option>`;
    }
    function renderDashboard(data) {
      document.getElementById("m-users").textContent = data.new_candidates.length + data.new_employers.length;
      document.getElementById("m-candidates").textContent = data.new_candidates.length;
      document.getElementById("m-employers").textContent = data.new_employers.length;
      document.getElementById("m-vacancies").textContent = data.open_vacancies.length;
      document.getElementById("m-matches").textContent = data.strong_matches.length;
      document.getElementById("m-risks").textContent = data.risky_cases.length;
      const analytics = data.analytics || {};
      renderTable("analytics", ["Metric", "Value"], [
        ["Visits today", analytics.visits_today],
        ["Unique users", analytics.unique_users],
        ["Create profile clicks", analytics.profile_create_clicks],
        ["Created profiles", analytics.created_profiles],
        ["Completed profiles", analytics.completed_profiles],
        ["Incomplete profiles", analytics.incomplete_profiles],
        ["New vacancies", analytics.new_vacancies],
        ["Pending review", analytics.pending_review_vacancies],
        ["Published vacancies", analytics.published_vacancies],
        ["Rejected vacancies", analytics.rejected_vacancies],
        ["Vacancy views", analytics.vacancy_views],
        ["Applications", analytics.vacancy_apply_clicks],
        ["Profile creation conversion", analytics.profile_creation_conversion === null ? "No data" : `${analytics.profile_creation_conversion}%`],
        ["Profile completion conversion", analytics.profile_completion_conversion === null ? "No data" : `${analytics.profile_completion_conversion}%`]
      ].map(([label, value]) => `<tr><td>${escapeHtml(label)}</td><td>${escapeHtml(value ?? "No data")}</td></tr>`));
      renderTable("manual", [tr("table.name"), tr("profile.profession"), tr("table.status"), tr("table.missing"), tr("table.actions")], data.manual_contact.map(c =>
        `<tr><td>${escapeHtml(c.first_name)} ${escapeHtml(c.last_name)}</td><td>${escapeHtml(c.profession_code)}</td><td>${escapeHtml(c.status)}</td><td>${tags(c.metadata.missing_documents)}</td><td>${candidateActions(c)}</td></tr>`
      ));
      renderTable("event-feed", [tr("table.signal"), tr("table.details")], (data.event_feed || []).map(item =>
        `<tr><td>${escapeHtml(eventLabel(item))}</td><td>${escapeHtml(item.text)}</td></tr>`
      ));
      renderTable("employers", [tr("table.company"), tr("employer.country"), tr("table.verified"), tr("table.actions")], data.new_employers.map(e =>
        `<tr><td>${escapeHtml(e.company_name)}</td><td>${escapeHtml(e.country_code)}</td><td>${e.verified ? tr("common.yes") : tr("common.no")}</td><td>${employerActions(e)}</td></tr>`
      ));
      renderTable("pending-vacancies", ["ID", "Title", "Employer", "Source", "Status", "Warnings", "Actions"], (data.pending_vacancies || []).map(v =>
        `<tr><td>${escapeHtml(v.id)}</td><td>${escapeHtml(v.title)}</td><td>${escapeHtml(v.metadata?.employer_name || v.employer_id)}</td><td>${escapeHtml(v.metadata?.source || "unknown")}</td><td>${escapeHtml(v.status)}</td><td>${warningTags(v.metadata?.quality_warnings)}</td><td>${vacancyActions(v)}</td></tr>`
      ));
      renderTable("recent-vacancies", ["ID", "Date", "Title", "Employer", "Country", "City", "Profession", "Source", "Status", "Views", "Applies", "Actions"], (data.recent_vacancies || []).map(v =>
        `<tr><td>${escapeHtml(v.id)}</td><td>${escapeHtml(v.created_at)}</td><td>${escapeHtml(v.title)}</td><td>${escapeHtml(v.metadata?.employer_name || v.employer_id)}</td><td>${escapeHtml(v.country_code)}</td><td>${escapeHtml(v.location || "-")}</td><td>${escapeHtml(v.profession_code)}</td><td>${escapeHtml(v.metadata?.source || "unknown")}</td><td>${escapeHtml(v.status)}</td><td>${escapeHtml(v.metadata?.views || 0)}</td><td>${escapeHtml(v.metadata?.applies || 0)}</td><td>${vacancyActions(v)}</td></tr>`
      ));
      renderTable("first-vacancies", ["Vacancy ID", "Title", "Employer", "Source", "Created", "Complete", "Risks", "Recommended"], (data.first_vacancies_report || []).map(item =>
        `<tr><td>${escapeHtml(item.vacancy_id)}</td><td>${escapeHtml(item.title)}</td><td>${escapeHtml(item.employer)}</td><td>${escapeHtml(item.source)}</td><td>${escapeHtml(item.created_at)}</td><td>${item.data_complete ? "Yes" : "No"}</td><td>${warningTags(item.risks)}</td><td>${escapeHtml(item.recommended_status)}</td></tr>`
      ));
      const demo = data.demo_records || { employers: [], vacancies: [] };
      renderTable("demo-records", ["Type", "ID", "Name", "Reason"], [
        ...(demo.employers || []).map(e => `<tr><td>Employer</td><td>${escapeHtml(e.id)}</td><td>${escapeHtml(e.company_name)}</td><td>${escapeHtml(e.metadata?.demo_reason || "demo")}</td></tr>`),
        ...(demo.vacancies || []).map(v => `<tr><td>Vacancy</td><td>${escapeHtml(v.id)}</td><td>${escapeHtml(v.title)}</td><td>${escapeHtml(v.metadata?.demo_reason || "demo")}</td></tr>`)
      ]);
      renderTable("risks", [tr("dashboard.candidates"), tr("table.score"), tr("table.recommendation"), tr("dashboard.risk_cases"), tr("table.actions")], data.risky_cases.map(m =>
        `<tr><td>${escapeHtml(m.candidate_id)}</td><td>${m.score}</td><td class="risk">${escapeHtml(m.metadata.recommendation)}</td><td>${tags(m.metadata.risks)}</td><td>${matchActions(m)}</td></tr>`
      ));
      renderTable("vacancies", [tr("table.title"), tr("employer.country"), tr("employer.salary"), tr("table.status"), tr("table.actions")], data.open_vacancies.map(v =>
        `<tr><td>${escapeHtml(v.title)}</td><td>${escapeHtml(v.country_code)}</td><td>${v.salary_min}-${v.salary_max} ${escapeHtml(v.currency)}</td><td>${escapeHtml(v.status)}</td><td>${vacancyActions(v)}</td></tr>`
      ));
      renderTable("matches", [tr("dashboard.candidates"), tr("employer.vacancy_card"), tr("table.score"), tr("table.reasons"), tr("table.actions")], data.strong_matches.map(m =>
        `<tr><td>${escapeHtml(m.candidate_id)}</td><td>${escapeHtml(m.vacancy_id)}</td><td class="ok">${m.score}</td><td>${tags(m.reasons)}</td><td>${matchActions(m)}</td></tr>`
      ));
      renderTable("activity", [tr("table.time"), tr("table.entity"), tr("table.action"), tr("table.change"), tr("table.note")], (data.activity || []).map(a =>
        `<tr><td>${escapeHtml(a.created_at)}</td><td>${escapeHtml(a.entity_type)}<br><span class="muted">${escapeHtml(a.entity_id)}</span></td><td>${escapeHtml(a.action)}</td><td>${escapeHtml(a.old_value)} -> ${escapeHtml(a.new_value)}</td><td>${escapeHtml(a.note)}</td></tr>`
      ));
    }
    function candidateActions(candidate) {
      return actionButtons([
        { label: tr("actions.docs_received"), onclick: `documentsReceived('${candidate.id}')` },
        { label: tr("actions.ready"), onclick: `candidateStatus('${candidate.id}','ready_for_matching')` },
        { label: tr("actions.interview"), onclick: `candidateStatus('${candidate.id}','interview')` },
        { label: tr("actions.hired"), onclick: `candidateStatus('${candidate.id}','hired')` }
      ]);
    }
    function employerActions(employer) {
      return actionButtons([
        { label: tr("actions.verify"), onclick: `verifyEmployer('${employer.id}', true)` }
      ]);
    }
    function vacancyActions(vacancy) {
      return actionButtons([
        { label: "Verify", onclick: `vacancyStatus('${vacancy.id}','verified')` },
        { label: "Publish", onclick: `publishVacancy('${vacancy.id}')` },
        { label: tr("actions.reject"), onclick: `rejectVacancy('${vacancy.id}')` },
        { label: "Archive", onclick: `vacancyStatus('${vacancy.id}','archived')` }
      ]);
    }
    function warningTags(items) {
      const normalized = Array.isArray(items) ? items : [];
      if (!normalized.length) return `<span class="ok">OK</span>`;
      return normalized.map(item => `<span class="tag">${escapeHtml(item.code || item.message || item)}</span>`).join("");
    }
    function matchActions(match) {
      return actionButtons([
        { label: tr("actions.contacted"), onclick: `matchStatus('${match.id}','contacted')` },
        { label: tr("actions.interview"), onclick: `matchStatus('${match.id}','interview')` },
        { label: tr("actions.hired"), onclick: `matchStatus('${match.id}','hired')` },
        { label: tr("actions.reject"), onclick: `matchStatus('${match.id}','rejected')` }
      ]);
    }
    async function documentsReceived(candidateId) {
      await patchJson(`/api/candidates/${candidateId}/documents-received`, {
        status: "ready_for_matching",
        actor_id: "coordinator",
        note: "Documents received from dashboard"
      });
      await loadAll();
      setStatus("candidate-status", `Documents received: ${candidateId}`);
    }
    async function candidateStatus(candidateId, status) {
      await patchJson(`/api/candidates/${candidateId}/status`, {
        status,
        actor_id: "coordinator",
        note: `Candidate marked ${status} from dashboard`
      });
      await loadAll();
      setStatus("candidate-status", `Candidate ${candidateId}: ${status}`);
    }
    async function verifyEmployer(employerId, verified) {
      await patchJson(`/api/employers/${employerId}/verify`, {
        verified,
        actor_id: "coordinator",
        note: "Employer verified from dashboard"
      });
      await loadAll();
      setStatus("employer-status", `Employer verified: ${employerId}`);
    }
    async function vacancyStatus(vacancyId, status) {
      await patchJson(`/api/vacancies/${vacancyId}/status`, {
        status,
        actor_id: "coordinator",
        note: `Vacancy marked ${status} from dashboard`
      });
      await loadAll();
      setStatus("vacancy-status", `Vacancy ${vacancyId}: ${status}`);
    }
    async function publishVacancy(vacancyId) {
      await postJson(`/api/admin/vacancies/${vacancyId}/publish`, {});
      await loadAll();
      setStatus("vacancy-status", `Vacancy published: ${vacancyId}`);
    }
    async function rejectVacancy(vacancyId) {
      await patchJson(`/api/vacancies/${vacancyId}/status`, {
        status: "rejected",
        actor_id: "coordinator",
        note: "insufficient_information"
      });
      await loadAll();
      setStatus("vacancy-status", `Vacancy rejected: ${vacancyId}`);
    }
    async function matchStatus(matchId, status) {
      await patchJson(`/api/matches/${matchId}/status`, {
        status,
        actor_id: "coordinator",
        note: `Match marked ${status} from dashboard`
      });
      await loadAll();
      setStatus("match-status", `Match ${matchId}: ${status}`);
    }
    async function seedDemo() {
      setStatus("match-status", "Seeding demo...");
      await fetch("/api/demo/seed", { method: "POST" });
      await loadAll();
      setStatus("match-status", "Demo data added.");
    }
    document.getElementById("candidate-form").addEventListener("submit", async event => {
      event.preventDefault();
      const data = formData(event.currentTarget);
      const payload = {
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone,
        country_code: data.country_code.toUpperCase(),
        profession_code: data.profession_code,
        languages: splitList(data.languages),
        years_of_experience: Number(data.years_of_experience || 0),
        metadata: {
          desired_country_code: data.desired_country_code.toUpperCase(),
          desired_salary: Number(data.desired_salary || 0),
          salary_currency: data.salary_currency.toUpperCase(),
          ready_from: data.ready_from,
          document_types: splitList(data.document_types)
        }
      };
      const result = await postJson("/api/candidates", payload);
      await loadAll();
      setStatus("candidate-status", `${tr("status.candidate_created")}: ${result.candidate.id}`);
    });
    document.getElementById("employer-form").addEventListener("submit", async event => {
      event.preventDefault();
      const data = formData(event.currentTarget);
      const result = await postJson("/api/employers", {
        company_name: data.company_name,
        contact_email: data.contact_email,
        contact_phone: data.contact_phone,
        country_code: data.country_code.toUpperCase(),
        industry: data.industry,
        verified: data.verified === "true"
      });
      await loadAll();
      setStatus("employer-status", `${tr("status.employer_created")}: ${result.employer.id}`);
    });
    document.getElementById("vacancy-form").addEventListener("submit", async event => {
      event.preventDefault();
      const data = formData(event.currentTarget);
      if (!data.employer_id) {
        setStatus("vacancy-status", tr("status.create_employer_first"));
        return;
      }
      const result = await postJson("/api/vacancies", {
        employer_id: data.employer_id,
        title: data.title,
        country_code: data.country_code.toUpperCase(),
        profession_code: data.profession_code,
        salary_min: Number(data.salary_min || 0),
        salary_max: Number(data.salary_max || 0),
        currency: data.currency.toUpperCase(),
        required_languages: splitList(data.required_languages),
        required_documents: splitList(data.required_documents),
        location: data.location,
        metadata: {
          contract_type: data.contract_type,
          work_permission_status: "to_be_verified",
          housing: data.housing === "true",
          housing_terms: data.housing_terms,
          salary_confirmed: data.salary_confirmed === "true",
          people_needed: Number(data.people_needed || 1),
          requirements: splitList(data.requirements)
        }
      });
      await loadAll();
      setStatus("vacancy-status", `${tr("status.vacancy_created")}: ${result.vacancy.id}`);
    });
    document.getElementById("match-form").addEventListener("submit", async event => {
      event.preventDefault();
      const vacancyId = document.getElementById("match-vacancy").value;
      if (!vacancyId) {
        setStatus("match-status", tr("status.create_vacancy_first"));
        return;
      }
      const result = await postJson(`/api/vacancies/${vacancyId}/match`, {
        minimum_score: Number(document.getElementById("match-score").value || 60)
      });
      await loadAll();
      setStatus("match-status", `${tr("status.matching_complete")}: ${result.matches.length}`);
    });
    document.addEventListener("atlas:i18n", loadAll);
    window.AtlasI18n.init().then(loadAll);
  </script>
</body>
</html>
""".replace("{{BRAND_LOGO_CSS}}", BRAND_LOGO_CSS).replace("{{BRAND_LOGO_HTML}}", BRAND_LOGO_HTML).replace("{{OBSERVABILITY_HEAD}}", observability_head_html()).replace("{{OBSERVABILITY_BODY}}", observability_body_html("dashboard"))
