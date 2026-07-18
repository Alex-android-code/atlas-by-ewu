"""ATLAS Control Center shell."""

from api.components.brand_logo import BRAND_LOGO_CSS, BRAND_MARK_HTML
from api.components.design_system import ATLAS_DESIGN_SYSTEM_CSS
from api.observability import observability_body_html, observability_head_html


CONTROL_CENTER_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS Control Center</title>
  <link rel="icon" href="/static/assets/atlas_brand_icon.png" type="image/png" />
  {{OBSERVABILITY_HEAD}}
  <style>
    :root {
      --cc-bg: #05070d;
      --cc-panel: rgba(255,255,255,0.058);
      --cc-line: rgba(238,241,246,0.12);
      --cc-muted: rgba(238,241,246,0.66);
      --cc-gold: #d6b25e;
      --cc-platinum: #eef1f6;
    }
    body { margin: 0; min-height: 100vh; }
    {{BRAND_LOGO_CSS}}
    {{ATLAS_DESIGN_SYSTEM_CSS}}
    .shell {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 260px 1fr;
    }
    aside {
      position: sticky;
      top: 0;
      height: 100vh;
      padding: 18px;
      border-right: 1px solid var(--cc-line);
      background: rgba(5,7,13,0.82);
    }
    .nav {
      display: grid;
      gap: 6px;
      margin-top: 24px;
    }
    .nav button {
      width: 100%;
      justify-content: start;
      min-height: 38px;
      border-radius: 10px;
      color: var(--cc-muted);
      background: transparent;
    }
    .nav button.active, .nav button:hover {
      color: var(--cc-platinum);
      background: rgba(255,255,255,0.07);
    }
    main {
      padding: 24px clamp(16px, 3vw, 34px) 34px;
      display: grid;
      gap: 18px;
      align-content: start;
    }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: end;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--cc-line);
    }
    h1 {
      margin: 0;
      font-size: clamp(31px, 5vw, 56px);
      line-height: 1;
      letter-spacing: 0;
    }
    .lead { margin: 10px 0 0; color: var(--cc-muted); max-width: 760px; line-height: 1.55; }
    .role-switch {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: end;
    }
    .grid {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 16px;
      align-items: start;
    }
    .panel {
      border: 1px solid var(--cc-line);
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(255,255,255,0.075), rgba(255,255,255,0.038));
      overflow: hidden;
    }
    .panel-head {
      min-height: 58px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 14px 16px;
      border-bottom: 1px solid var(--cc-line);
    }
    h2 { margin: 0; font-size: 16px; }
    .hint { color: var(--cc-muted); font-size: 13px; }
    .brief, .records, .kanban, .actions { display: grid; gap: 10px; padding: 14px; }
    .brief-card, .record, .stage {
      padding: 12px;
      border: 1px solid rgba(238,241,246,0.10);
      border-radius: 12px;
      background: rgba(255,255,255,0.04);
    }
    .brief-card strong, .record strong, .stage strong { display: block; font-size: 14px; }
    .brief-card span, .record span, .stage span { display: block; margin-top: 4px; color: var(--cc-muted); font-size: 12px; }
    .actions { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .action-button { min-height: 46px; }
    .kanban { grid-template-columns: repeat(4, minmax(120px, 1fr)); overflow-x: auto; }
    .stage { min-height: 86px; }
    .stage b { color: var(--cc-gold); font-size: 24px; }
    .status {
      min-height: 36px;
      color: var(--cc-muted);
      font-size: 13px;
    }
    @media (max-width: 980px) {
      .shell { grid-template-columns: 1fr; }
      aside { position: static; height: auto; }
      .grid, .hero, .actions { grid-template-columns: 1fr; }
      .role-switch { justify-content: start; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      {{BRAND_MARK_HTML}}
      <nav class="nav" id="nav"></nav>
    </aside>
    <main>
      <section class="hero">
        <div>
          <h1>ATLAS Control Center</h1>
          <p class="lead" id="brief-lead">Loading operational intelligence...</p>
        </div>
        <div class="role-switch">
          <button type="button" data-role="admin" class="active">Admin</button>
          <button type="button" data-role="coordinator">Coordinator</button>
          <button type="button" data-role="employer_owner">Employer</button>
          <button type="button" data-role="candidate">Candidate</button>
        </div>
      </section>
      <section class="panel">
        <div class="panel-head"><h2>Quick Actions</h2><span class="hint">Role-aware commands</span></div>
        <div class="actions" id="quick-actions"></div>
      </section>
      <section class="grid">
        <div class="panel">
          <div class="panel-head"><h2>AI Daily Brief</h2><span class="hint" id="events-count"></span></div>
          <div class="brief" id="daily-brief"></div>
        </div>
        <div class="panel">
          <div class="panel-head"><h2>Intelligence View</h2><span class="hint">Grouped signals</span></div>
          <div class="brief" id="intelligence"></div>
        </div>
      </section>
      <section class="panel">
        <div class="panel-head"><h2>Candidate Pipeline</h2><span class="hint">Centralized status config</span></div>
        <div class="kanban" id="candidate-kanban"></div>
      </section>
      <section class="panel">
        <div class="panel-head"><h2>CRM Workspace</h2><span class="hint">Latest candidate records</span></div>
        <div class="records" id="records"></div>
      </section>
      <div class="status" id="status">Ready.</div>
    </main>
  </div>
  {{OBSERVABILITY_BODY}}
  <script>
    let role = "admin";
    const $ = (id) => document.getElementById(id);
    const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    }[char]));

    async function loadWorkspace() {
      $("status").textContent = "Loading workspace...";
      const response = await fetch(`/api/product/crm-workspace?role=${encodeURIComponent(role)}`);
      if (!response.ok) {
        $("status").textContent = "Access denied or server error.";
        return;
      }
      const data = await response.json();
      render(data);
      $("status").textContent = "Workspace updated.";
    }

    function render(data) {
      $("brief-lead").textContent = data.daily_brief.summary;
      $("events-count").textContent = `${data.daily_brief.events_analyzed} events analyzed`;
      $("nav").innerHTML = data.navigation.map((item, index) =>
        `<button type="button" class="${index === 0 ? "active" : ""}">${escapeHtml(item.label)}</button>`
      ).join("");
      $("quick-actions").innerHTML = data.quick_actions.map((item, index) =>
        `<button type="button" class="action-button ${index === 0 ? "primary" : ""}">${escapeHtml(item.label)}</button>`
      ).join("");
      const recommendations = data.daily_brief.recommendations || [];
      $("daily-brief").innerHTML = recommendations.length
        ? recommendations.map(item => `<div class="brief-card"><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.reason)} Source: ${escapeHtml(item.source)}. Expected: ${escapeHtml(item.expected_result)}</span></div>`).join("")
        : `<div class="brief-card"><strong>No urgent decisions</strong><span>ATLAS found no high-priority operational blockers.</span></div>`;
      $("intelligence").innerHTML = data.intelligence_view.groups.map(item =>
        `<div class="brief-card"><strong>${escapeHtml(item.label)}</strong><span>${item.count} records · priority ${escapeHtml(item.priority)} · ${escapeHtml(item.source)}</span></div>`
      ).join("");
      $("candidate-kanban").innerHTML = data.kanban_view.candidate.map(stage =>
        `<div class="stage"><strong>${escapeHtml(stage.status.replaceAll("_", " "))}</strong><span><b>${stage.count}</b> records</span></div>`
      ).join("");
      const candidates = data.table_view.candidates || [];
      $("records").innerHTML = candidates.slice(-12).reverse().map(candidate =>
        `<div class="record"><strong>${escapeHtml(candidate.first_name)} ${escapeHtml(candidate.last_name)}</strong><span>${escapeHtml(candidate.profession_code)} · ${escapeHtml(candidate.status)} · ${escapeHtml(candidate.phone)}</span></div>`
      ).join("") || `<div class="record"><strong>No candidates yet</strong><span>New applications will appear here automatically.</span></div>`;
    }

    document.querySelectorAll("[data-role]").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll("[data-role]").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        role = button.dataset.role;
        loadWorkspace();
      });
    });
    loadWorkspace();
  </script>
</body>
</html>
""".replace("{{BRAND_LOGO_CSS}}", BRAND_LOGO_CSS).replace("{{ATLAS_DESIGN_SYSTEM_CSS}}", ATLAS_DESIGN_SYSTEM_CSS).replace("{{BRAND_MARK_HTML}}", BRAND_MARK_HTML).replace("{{OBSERVABILITY_HEAD}}", observability_head_html()).replace("{{OBSERVABILITY_BODY}}", observability_body_html("control-center"))
