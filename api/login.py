"""Coordinator login page HTML."""

from api.components.brand_logo import BRAND_LOGO_CSS, BRAND_LOGO_HTML
from api.observability import observability_body_html, observability_head_html


LOGIN_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="atlas-title-key" content="app.title" />
  <title>ATLAS Login</title>
  <link rel="icon" href="/static/assets/atlas_brand_icon.png" type="image/png" />
  {{OBSERVABILITY_HEAD}}
  <style>
    :root {
      --atlas-navy: #0B132B;
      --atlas-dark: #1A2338;
      --atlas-slate: #2E3A4F;
      --atlas-gold: #D4AF37;
      --atlas-gold-light: #F5D98A;
      --atlas-light: #E6E8EB;
      --atlas-white: #FFFFFF;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: Inter, Poppins, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 50% 8%, rgba(212,175,55,0.12), transparent 32%),
        var(--atlas-navy);
      color: var(--atlas-white);
      padding: 20px;
    }
    {{BRAND_LOGO_CSS}}
    .box {
      width: min(400px, 100%);
      background: rgba(26,35,56,0.88);
      border: 1px solid rgba(230,232,235,0.12);
      border-radius: 22px;
      padding: 26px;
      display: grid;
      gap: 16px;
    }
    h1 {
      margin: 8px 0 0;
      font-size: 28px;
      font-weight: 700;
    }
    p { margin: 0; color: var(--atlas-light); line-height: 1.5; }
    input, button {
      width: 100%;
      min-height: 50px;
      border-radius: 14px;
      font: inherit;
    }
    input {
      border: 1px solid rgba(230,232,235,0.16);
      background: rgba(255,255,255,0.06);
      color: var(--atlas-white);
      padding: 0 14px;
      outline: 0;
    }
    input:focus { border-color: var(--atlas-gold); }
    input::placeholder { color: rgba(230,232,235,0.55); }
    button {
      border: 0;
      background: linear-gradient(135deg, var(--atlas-gold), var(--atlas-gold-light));
      color: var(--atlas-navy);
      font-weight: 800;
      cursor: pointer;
    }
    .status { color: #fca5a5; min-height: 20px; }
  </style>
</head>
<body>
  <form class="box" id="login-form">
    {{BRAND_LOGO_HTML}}
    <h1 data-i18n="nav.login">Login</h1>
    <p data-i18n="login.subtitle">Secure access for the ATLAS operations team.</p>
    <input name="password" type="password" data-i18n-placeholder="login.access_code" placeholder="Access code" autocomplete="current-password" />
    <button type="submit" data-i18n="nav.login">Login</button>
    <div class="status" id="status"></div>
  </form>
  {{OBSERVABILITY_BODY}}
  <script src="/static/i18n.js?v=20260711-langfix"></script>
  <script>
    window.AtlasI18n.init();
    function tr(key) { return window.AtlasI18n ? window.AtlasI18n.t(key) : key; }
    document.getElementById("login-form").addEventListener("submit", async event => {
      event.preventDefault();
      const password = new FormData(event.currentTarget).get("password");
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
      });
      if (res.ok) {
        location.href = "/dashboard";
      } else {
        document.getElementById("status").textContent = tr("login.invalid");
      }
    });
  </script>
</body>
</html>
""".replace("{{BRAND_LOGO_CSS}}", BRAND_LOGO_CSS).replace("{{BRAND_LOGO_HTML}}", BRAND_LOGO_HTML).replace("{{OBSERVABILITY_HEAD}}", observability_head_html()).replace("{{OBSERVABILITY_BODY}}", observability_body_html("login"))
