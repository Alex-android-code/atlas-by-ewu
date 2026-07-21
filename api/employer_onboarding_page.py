"""Employer onboarding and dashboard pages."""

EMPLOYER_ONBOARDING_HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS | Employer Onboarding</title>
  <style>
    :root { --bg:#020714; --panel:rgba(255,255,255,.07); --line:rgba(238,241,246,.16); --gold:#d4af37; --text:#eef1f6; --muted:rgba(238,241,246,.72); --ok:#8fe3bd; --warn:#f5d56a; }
    * { box-sizing:border-box; min-width:0; }
    body { margin:0; min-height:100vh; background:radial-gradient(circle at 20% 0%, rgba(212,175,55,.14), transparent 30%), #020714; color:var(--text); font-family:Inter, system-ui, Segoe UI, sans-serif; }
    main { width:min(1120px,100%); margin:0 auto; padding:24px clamp(16px,4vw,40px) 40px; }
    header { display:flex; justify-content:space-between; align-items:center; gap:14px; margin-bottom:18px; }
    .brand { letter-spacing:.18em; color:#cfd6e6; font-weight:850; }
    .shell { display:grid; grid-template-columns:280px minmax(0,1fr); gap:16px; }
    .panel,.card { border:1px solid var(--line); border-radius:8px; background:linear-gradient(180deg, rgba(255,255,255,.09), rgba(255,255,255,.035)); padding:20px; box-shadow:0 24px 70px rgba(0,0,0,.24); }
    .steps { display:grid; gap:8px; }
    .step { padding:10px 12px; border-radius:8px; color:var(--muted); border:1px solid transparent; }
    .step.active { color:var(--text); border-color:rgba(212,175,55,.35); background:rgba(212,175,55,.08); }
    h1,h2,h3 { margin:0 0 12px; letter-spacing:0; }
    p,label,li { color:var(--muted); line-height:1.55; }
    label { display:grid; gap:7px; margin:10px 0; }
    input,textarea,select { width:100%; border:1px solid var(--line); border-radius:8px; background:rgba(255,255,255,.06); color:var(--text); min-height:44px; padding:10px 12px; font:inherit; }
    textarea { min-height:88px; resize:vertical; }
    .actions { display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; }
    button,.button { min-height:44px; border:0; border-radius:8px; padding:0 16px; background:linear-gradient(135deg,#ffe27a,#d4af37 52%,#a97818); color:#130f05; font-weight:800; cursor:pointer; text-decoration:none; display:inline-grid; place-items:center; }
    .secondary { background:rgba(255,255,255,.07); color:var(--text); border:1px solid var(--line); }
    .danger { background:rgba(239,68,68,.18); color:#fff; border:1px solid rgba(239,68,68,.28); }
    .grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }
    .upload { border:1px dashed rgba(212,175,55,.45); border-radius:8px; padding:20px; background:rgba(212,175,55,.05); }
    .chip { display:inline-flex; margin:4px 4px 0 0; border:1px solid var(--line); border-radius:999px; padding:6px 10px; color:var(--muted); }
    .error { color:#ffb4b4; min-height:24px; }
    @media (max-width:820px){ header,.shell{grid-template-columns:1fr; flex-direction:column; align-items:flex-start;} .grid{grid-template-columns:1fr;} button,.button{width:100%;} }
  </style>
</head>
<body>
<main>
  <header><div class="brand">ATLAS by EWU</div><a class="button secondary" href="/employer/dashboard">Dashboard</a></header>
  <section class="shell">
    <aside class="panel"><h3>Employer setup</h3><div class="steps" id="steps"></div></aside>
    <section class="panel"><div id="view"></div><div class="error" id="error"></div><div class="actions"><button class="secondary" id="back" type="button">Back</button><button id="next" type="button">Continue</button></div></section>
  </section>
</main>
<script>
  let userId = localStorage.getItem("atlas_employer_user_id") || "";
  let headers = {"Content-Type":"application/json"};
  const steps = ["welcome","employer_agent","company_identity","company_verification","company_profile","locations","team","hiring_needs","hiring_process","integrations","consents","completion"];
  let session = null;
  let current = "welcome";
  let local = {};
  const view = document.getElementById("view");
  const errorBox = document.getElementById("error");
  const backButton = document.getElementById("back");
  const nextButton = document.getElementById("next");
  async function ensureUser() {
    if (!userId) userId = `employer-${crypto.randomUUID()}`;
    localStorage.setItem("atlas_employer_user_id", userId);
    headers = {"Content-Type":"application/json","X-ATLAS-User-Id":userId};
  }
  async function api(path, options={}) {
    const res = await fetch(path, {headers, ...options});
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "Request failed");
    return data;
  }
  async function load() {
    await ensureUser();
    session = await api("/api/employer/onboarding");
    local = structuredClone(session.data || {});
    const requested = new URLSearchParams(location.search).get("step");
    current = requested && steps.includes(requested) ? requested : (session.status === "completed" ? "completion" : session.current_step || "welcome");
    render();
  }
  function render() {
    errorBox.textContent = "";
    document.getElementById("steps").innerHTML = steps.map((step) => `<div class="step ${step === current ? "active" : ""}">${escapeHtml(step.replace("_"," "))}</div>`).join("");
    backButton.disabled = steps.indexOf(current) <= 0;
    nextButton.textContent = current === "completion" ? "Open dashboard" : current === "company_verification" ? "Save verification" : current === "consents" ? "Complete" : "Continue";
    view.innerHTML = templates[current]();
    bind();
  }
  const templates = {
    welcome: () => `<h1>Employer onboarding</h1><p>Create or join a company workspace, verify business data, configure hiring and open a real employer dashboard.</p>`,
    employer_agent: () => `<h2>Employer AI agent</h2><div class="grid">${input("employer_agent.name","Agent name")}${input("employer_agent.language","Language")}${input("employer_agent.tone","Tone")}${input("employer_agent.autonomy_level","Autonomy level 0-3","number")}</div>${textarea("employer_agent.tasks","Tasks, comma separated")}`,
    company_identity: () => `<h2>Company identity</h2><div class="grid">${input("company_identity.legal_name","Legal name")}${input("company_identity.trading_name","Trading name")}${input("company_identity.country_code","Registration country")}${input("company_identity.registration_number","Registration number")}${input("company_identity.tax_number","VAT/NIP/tax number")}${input("company_identity.official_email","Official email","email")}${input("company_identity.phone","Phone")}${input("company_identity.website","Website")}</div>${textarea("company_identity.legal_address","Legal address")}`,
    company_verification: () => `<h2>Company verification</h2><p>Upload registration, tax or representation documents. Uploaded files create a pending review, not an automatic verified status.</p><div class="upload" id="drop"><input type="file" id="file" accept=".pdf,.doc,.docx,.odt,.rtf" hidden><button class="secondary" data-action="choose" type="button">Attach file</button><p id="upload-status">${(local.company_verification?.files || []).map((f) => escapeHtml(f.original_name)).join(", ") || "No documents uploaded."}</p></div>`,
    company_profile: () => `<h2>Company profile</h2><div class="grid">${input("company_profile.industry","Industry")}${input("company_profile.subindustry","Subindustry")}${input("company_profile.company_size","Company size")}${input("company_profile.employee_count","Employees","number")}${input("company_profile.founded_year","Founded year","number")}${input("company_profile.employer_type","Employer type")}</div>${textarea("company_profile.short_description","Short description")}${textarea("company_profile.benefits","Benefits, comma separated")}`,
    locations: () => `<h2>Locations</h2><p>Add headquarters or main work location. Exact address stays private unless explicitly published.</p><div class="grid">${input("locations.locations.0.type","Type")}${input("locations.locations.0.country","Country")}${input("locations.locations.0.city","City")}${input("locations.locations.0.address","Private address")}</div>`,
    team: () => `<h2>Recruiting team</h2><p>Optional. Invite trusted team members with backend-controlled roles.</p><div class="grid">${input("team.invitations.0.email","Invite email","email")}${input("team.invitations.0.role","Role")}</div>`,
    hiring_needs: () => `<h2>Hiring needs</h2><div class="grid">${input("hiring_needs.profession","Profession / role")}${input("hiring_needs.quantity","Quantity","number")}${input("hiring_needs.urgency","Urgency")}${input("hiring_needs.targetStartDate","Start date")}${input("hiring_needs.salary_min","Salary min","number")}${input("hiring_needs.salary_max","Salary max","number")}${input("hiring_needs.currency","Currency")}${input("hiring_needs.grossNet","Gross/net")}</div>${textarea("hiring_needs.skills","Skills, comma separated")}`,
    hiring_process: () => `<h2>Hiring process</h2><p>ATLAS keeps final states protected: hired, rejected and withdrawn cannot be removed.</p><div class="grid">${input("hiring_process.stages.0.label","First stage")}${input("hiring_process.stages.1.label","Second stage")}${input("hiring_process.stages.2.label","Third stage")}</div>`,
    integrations: () => `<h2>Integrations</h2><p>Optional. Keep disabled until keys and contracts are ready.</p><label><input type="checkbox" data-path="integrations.enabled" ${val("integrations.enabled") ? "checked" : ""}> Enable integrations later</label>${textarea("integrations.systems","Systems, comma separated")}`,
    consents: () => `<h2>Business consents</h2><label><input type="checkbox" data-path="consents.required.termsForBusiness" ${val("consents.required.termsForBusiness") ? "checked" : ""}> Terms for Business</label><label><input type="checkbox" data-path="consents.required.dataProcessing" ${val("consents.required.dataProcessing") ? "checked" : ""}> Privacy/Data Processing Terms</label><label><input type="checkbox" data-path="consents.required.representativeAuthority" ${val("consents.required.representativeAuthority") ? "checked" : ""}> Authority to represent company</label><label><input type="checkbox" data-path="consents.required.lawfulCandidateUse" ${val("consents.required.lawfulCandidateUse") ? "checked" : ""}> Lawful candidate data use</label><label><input type="checkbox" data-path="consents.required.nonDiscrimination" ${val("consents.required.nonDiscrimination") ? "checked" : ""}> Non-discriminatory hiring</label><label><input type="checkbox" data-path="consents.optional.aiMatching" ${val("consents.optional.aiMatching") ? "checked" : ""}> AI matching</label>`,
    completion: () => `<h1>Company workspace ready</h1><p>${escapeHtml(val("company_identity.trading_name") || val("company_identity.legal_name") || "Company")} is ready for employer dashboard review.</p><div class="grid"><div class="card"><h3>Hiring</h3><p>${escapeHtml(val("hiring_needs.profession") || "")} · ${escapeHtml(val("hiring_needs.quantity") || 1)} worker(s)</p></div><div class="card"><h3>Verification</h3><p>${(local.company_verification?.files || []).length} uploaded document(s), pending review</p></div></div><div class="actions"><a class="button" href="/employer/dashboard">Open dashboard</a><a class="button secondary" href="/employer/onboarding?step=company_identity">Review company</a></div>`
  };
  function bind() {
    document.querySelectorAll("[data-path]").forEach((el) => {
      el.addEventListener("input", () => setPath(el.dataset.path, el.type === "checkbox" ? el.checked : el.value));
      el.addEventListener("change", () => setPath(el.dataset.path, el.type === "checkbox" ? el.checked : el.value));
    });
    document.querySelector("[data-action='choose']")?.addEventListener("click", () => document.getElementById("file").click());
    document.getElementById("file")?.addEventListener("change", (event) => event.target.files[0] && upload(event.target.files[0]));
    document.getElementById("drop")?.addEventListener("dragover", (event) => event.preventDefault());
    document.getElementById("drop")?.addEventListener("drop", (event) => { event.preventDefault(); if (event.dataTransfer.files[0]) upload(event.dataTransfer.files[0]); });
  }
  async function upload(file) {
    const form = new FormData();
    form.append("kind", "employer-document");
    form.append("file", file);
    const res = await fetch("/api/files/upload", {method:"POST", headers: {"X-ATLAS-User-Id": userId}, body: form});
    const data = await res.json();
    if (!res.ok) return fail(data.detail || "Upload failed");
    local.company_verification = local.company_verification || {files:[]};
    local.company_verification.files = [...(local.company_verification.files || []), data.file];
    await api("/api/employer/onboarding", {method:"PATCH", body:JSON.stringify({step:"company_verification", data:local.company_verification, next_step:"company_verification"})});
    render();
  }
  async function next() {
    if (current === "completion") { location.href = "/employer/dashboard"; return; }
    const data = collect(current);
    if (!validate(current, data)) return;
    if (current === "consents") {
      await api("/api/employer/onboarding", {method:"PATCH", body:JSON.stringify({step:current, data})});
      const completed = await api("/api/employer/onboarding/complete", {method:"POST"});
      session = completed.session;
      local = structuredClone(session.data || {});
      current = "completed";
      render();
      return;
    }
    session = await api("/api/employer/onboarding", {method:"PATCH", body:JSON.stringify({step:current, data})});
    local = structuredClone(session.data || {});
    current = session.current_step;
    render();
  }
  function collect(step) {
    if (step === "welcome") return {};
    const data = structuredClone(local[step] || {});
    if (step === "locations" && data.locations && !Array.isArray(data.locations)) data.locations = Object.values(data.locations);
    if (step === "team" && data.invitations && !Array.isArray(data.invitations)) data.invitations = Object.values(data.invitations).filter((item) => item.email);
    if (step === "hiring_process" && data.stages && !Array.isArray(data.stages)) {
      const custom = Object.values(data.stages).filter((item) => item.label);
      data.stages = custom.length ? [...custom, {key:"hired", label:"Hired"}, {key:"rejected", label:"Rejected"}, {key:"withdrawn", label:"Withdrawn"}] : [];
    }
    return data;
  }
  function validate(step, data) {
    if (step === "company_identity" && !data.legal_name) return fail("Legal company name is required.");
    if (step === "hiring_needs" && !data.profession) return fail("Profession is required.");
    if (step === "consents" && (!data.required?.termsForBusiness || !data.required?.dataProcessing || !data.required?.representativeAuthority || !data.required?.lawfulCandidateUse || !data.required?.nonDiscrimination)) return fail("Required business consents are missing.");
    return true;
  }
  function input(path,label,type="text"){ return `<label>${label}<input data-path="${path}" type="${type}" value="${escapeHtml(val(path))}"></label>`; }
  function textarea(path,label){ return `<label>${label}<textarea data-path="${path}">${escapeHtml(val(path))}</textarea></label>`; }
  function setPath(path,value){ const parts=path.split("."); let target=local; while(parts.length>1){ const key=parts.shift(); target[key]=target[key]||{}; target=target[key]; } target[parts[0]]=value; }
  function val(path){ return path.split(".").reduce((acc,key)=>acc?.[key], local) || ""; }
  function fail(message){ errorBox.textContent=message; return false; }
  function escapeHtml(value){ return String(value ?? "").replace(/[&<>"']/g,(c)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c])); }
  backButton.addEventListener("click", () => { current = steps[Math.max(0, steps.indexOf(current)-1)]; render(); });
  nextButton.addEventListener("click", () => next().catch((error) => fail(error.message)));
  load().catch((error) => fail(error.message));
</script>
</body>
</html>
"""


EMPLOYER_DASHBOARD_HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS | Employer Dashboard</title>
  <style>
    :root { --bg:#020714; --line:rgba(238,241,246,.16); --gold:#d4af37; --text:#eef1f6; --muted:rgba(238,241,246,.72); }
    * { box-sizing:border-box; min-width:0; }
    body { margin:0; min-height:100vh; color:var(--text); background:radial-gradient(circle at 20% 0%, rgba(212,175,55,.14), transparent 30%), #020714; font-family:Inter, system-ui, Segoe UI, sans-serif; }
    main { width:min(1120px,100%); margin:0 auto; padding:24px clamp(16px,4vw,40px) 40px; }
    header { display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom:18px; }
    .brand { letter-spacing:.18em; color:#cfd6e6; font-weight:850; }
    .grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; margin-top:14px; }
    .card,.hero { border:1px solid var(--line); border-radius:8px; background:linear-gradient(180deg, rgba(255,255,255,.09), rgba(255,255,255,.035)); padding:22px; }
    .hero { display:grid; grid-template-columns:1.2fr .8fr; gap:14px; }
    h1,h2,h3 { margin:0 0 10px; } p,li { color:var(--muted); line-height:1.55; }
    .score { font-size:54px; color:var(--gold); font-weight:900; }
    .chip { display:inline-flex; margin:4px 4px 0 0; border:1px solid var(--line); border-radius:999px; padding:6px 10px; color:var(--muted); }
    .button { min-height:44px; border-radius:8px; padding:0 16px; background:linear-gradient(135deg,#ffe27a,#d4af37 52%,#a97818); color:#130f05; text-decoration:none; font-weight:800; display:inline-grid; place-items:center; }
    .secondary { background:rgba(255,255,255,.07); color:var(--text); border:1px solid var(--line); }
    .actions { display:flex; flex-wrap:wrap; gap:10px; }
    @media (max-width:820px){ header,.hero,.grid{grid-template-columns:1fr; flex-direction:column; align-items:flex-start;} .button{width:100%;} }
  </style>
</head>
<body>
<main>
  <header><div class="brand">ATLAS by EWU</div><div class="actions"><a class="button secondary" href="/employer/onboarding">Edit profile</a><a class="button" href="/employer">Employer chat</a></div></header>
  <section id="dashboard">Loading...</section>
</main>
<script>
  async function load() {
    const userId = localStorage.getItem("atlas_employer_user_id") || "";
    const res = await fetch("/api/employer/dashboard", {headers: {"X-ATLAS-User-Id": userId}});
    const data = await res.json();
    if (data.onboarding?.redirectTo) { location.href = data.onboarding.redirectTo; return; }
    render(data);
  }
  function render(data) {
    const readiness = data.readiness || {};
    document.getElementById("dashboard").innerHTML = `
      <section class="hero"><div><h1>${escapeHtml(data.employer?.company_name || "Employer")}</h1><p>${escapeHtml(data.company?.industry || data.employer?.industry || "Company profile")}</p><span class="chip">${escapeHtml(data.onboarding?.status || "")}</span></div><div><p>Verification</p><div class="score">${escapeHtml(readiness.verificationStatus || "not_started")}</div></div></section>
      <section class="grid"><article class="card"><h3>Readiness</h3>${kv(readiness)}</article><article class="card"><h3>Hiring needs</h3>${kv(data.hiringNeeds || {})}</article></section>
      <section class="grid"><article class="card"><h3>Documents</h3>${documents(data.documents || [])}</article><article class="card"><h3>Recommended actions</h3>${actions(data.recommendedActions || [])}</article></section>
      <section class="grid"><article class="card"><h3>Recent activity</h3>${activity(data.recentActivity || [])}</article><article class="card"><h3>Quick actions</h3>${quick(data.quickActions || [])}</article></section>`;
  }
  function kv(obj){ const entries=Object.entries(obj); return entries.length ? entries.map(([k,v])=>`<p><strong>${escapeHtml(k)}</strong>: ${escapeHtml(Array.isArray(v)?v.join(", "):v)}</p>`).join("") : "<p>No data yet.</p>"; }
  function documents(items){ return items.length ? `<ul>${items.map((item)=>`<li>${escapeHtml(item.metadata?.original_name || item.id)} · ${escapeHtml(item.status || "uploaded")}</li>`).join("")}</ul>` : "<p>No company documents uploaded yet.</p>"; }
  function actions(items){ return items.length ? `<ul>${items.map((item)=>`<li><strong>${escapeHtml(item.title)}</strong> · ${escapeHtml(item.priority || "")} ${item.route ? `<a href="${escapeHtml(item.route)}">Open</a>` : ""}</li>`).join("")}</ul>` : "<p>No priority actions.</p>"; }
  function activity(items){ return items.length ? `<ul>${items.map((item)=>`<li>${escapeHtml(item.title)} · ${escapeHtml(item.createdAt || "")}</li>`).join("")}</ul>` : "<p>No real activity yet.</p>"; }
  function quick(items){ return `<div class="actions">${items.map((item)=>`<a class="button secondary" href="${escapeHtml(item.route)}">${escapeHtml(item.title)}</a>`).join("")}</div>`; }
  function escapeHtml(value){ return String(value ?? "").replace(/[&<>"']/g,(c)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c])); }
  load().catch((error)=>{ document.getElementById("dashboard").textContent = error.message; });
</script>
</body>
</html>
"""
