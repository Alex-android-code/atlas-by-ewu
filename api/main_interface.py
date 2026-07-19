"""Premium ATLAS main interface and role pages."""

from __future__ import annotations

from html import escape

from api.components.brand_logo import BRAND_LOGO_CSS, BRAND_LOGO_HTML, BRAND_MARK_HTML
from api.components.design_system import ATLAS_DESIGN_SYSTEM_CSS
from api.observability import observability_body_html, observability_head_html


ROLE_CARDS = [
    {
        "title": "Працівник",
        "subtitle": "Профіль, AI-агент, CV, робота, документи і кар'єрна карта.",
        "href": "/employee",
        "tone": "worker",
        "cta": "Обрати працівника",
    },
    {
        "title": "Роботодавець",
        "subtitle": "Вакансії, AI-підбір, комунікація, рекрутинг і аналітика.",
        "href": "/employer",
        "tone": "employer",
        "cta": "Обрати роботодавця",
    },
    {
        "title": "Корпорація",
        "subtitle": "Enterprise CRM, HRM, аудит, автоматизація, безпека і API.",
        "href": "/corporate",
        "tone": "corporate",
        "cta": "Обрати корпорацію",
    },
]

EMPLOYEE_FEATURES = [
    "Створення професійного профілю",
    "Персональний AI-агент",
    "Пошук роботи",
    "Створення CV",
    "Перевірка навичок і документів",
    "Рекомендації навчальних курсів",
    "Легалізація",
    "Страхування",
    "Карта кар'єри",
    "Повідомлення роботодавців",
    "Історія заявок",
    "Налаштування приватності",
]

EMPLOYER_FEATURES = [
    "Створення вакансій",
    "AI-підбір кандидатів",
    "Рекомендовані кандидати",
    "Комунікація",
    "Управління вакансіями",
    "Рекрутаційна воронка",
    "Аналітика",
    "Документи",
    "Підписки",
    "Рахунки",
    "Доступ до CRM",
    "AI-рекомендації рекрутингу",
]

CORPORATE_FEATURES = [
    "Корпоративна CRM",
    "HRM",
    "Управління філіями",
    "AI-аудит підприємства",
    "Оптимізація бізнес-процесів",
    "Прогнозування персоналу",
    "Аналіз продуктивності",
    "Навчання працівників",
    "Оцінка ризиків",
    "Автоматизація документообігу",
    "Управління ролями",
    "Корпоративна аналітика",
    "ERP, CRM та API інтеграції",
    "Audit Log",
    "GDPR-панель",
    "Enterprise Security Center",
]


BASE_CSS = """
:root {
  color-scheme: dark;
}
* { box-sizing: border-box; }
html, body { width: 100%; max-width: 100%; overflow-x: hidden; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: var(--atlas-font);
  color: var(--atlas-platinum);
  background:
    radial-gradient(circle at 18% -8%, rgba(214,178,94,0.16), transparent 30%),
    radial-gradient(circle at 86% 4%, rgba(0,96,192,0.18), transparent 29%),
    linear-gradient(180deg, var(--atlas-bg) 0%, var(--atlas-bg-2) 48%, var(--atlas-midnight) 100%);
}
.page-shell { min-height: 100vh; position: relative; z-index: 1; }
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  min-height: 78px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 12px clamp(14px, 4vw, 44px);
  border-bottom: 1px solid var(--atlas-line);
  background: rgba(5,7,13,0.82);
  backdrop-filter: blur(22px) saturate(135%);
}
.site-header .brand-mark-image { width: 48px; height: 48px; border-radius: 13px; }
.main-nav {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--atlas-muted);
  font-size: 14px;
  font-weight: 650;
}
.main-nav a {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  padding: 0 10px;
  text-decoration: none;
}
.main-nav a:hover, .main-nav a.active { color: var(--atlas-white); background: rgba(255,255,255,0.065); }
.crm-login {
  border: 1px solid rgba(214,178,94,0.48);
  color: var(--atlas-gold-soft) !important;
  background: linear-gradient(135deg, rgba(214,178,94,0.16), rgba(255,255,255,0.045));
  box-shadow: 0 12px 32px rgba(214,178,94,0.12);
}
.shield-icon {
  width: 15px;
  height: 17px;
  display: inline-block;
  border: 2px solid currentColor;
  border-radius: 8px 8px 10px 10px;
  position: relative;
}
.shield-icon::before {
  content: "";
  position: absolute;
  left: 3px;
  top: -8px;
  width: 7px;
  height: 7px;
  border: 2px solid currentColor;
  border-bottom: 0;
  border-radius: 7px 7px 0 0;
}
.language-selector { position: relative; }
.language-button {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 0;
  border-radius: 999px;
  padding: 0 10px;
  background: transparent;
  color: inherit;
  cursor: pointer;
}
.language-current { color: var(--atlas-gold-soft); font-size: 12px; font-weight: 800; text-transform: uppercase; }
.language-menu {
  position: absolute;
  top: 42px;
  right: 0;
  z-index: 60;
  min-width: 220px;
  display: none;
  padding: 8px;
  border: 1px solid var(--atlas-line-strong);
  border-radius: 14px;
  background: rgba(8,11,20,0.98);
  box-shadow: var(--atlas-shadow-md);
}
.language-menu.open { display: grid; gap: 4px; }
.language-option {
  min-height: 40px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--atlas-muted);
  text-align: left;
  cursor: pointer;
  padding: 0 10px;
}
.language-option:hover, .language-option.active { color: var(--atlas-white); background: rgba(255,255,255,0.07); }
.menu-toggle { display: none; }
.hero-home {
  min-height: calc(100vh - 78px);
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  gap: clamp(24px, 4vw, 54px);
  align-items: center;
  padding: clamp(34px, 5vw, 68px) clamp(14px, 4vw, 44px) 42px;
}
.hero-copy { display: grid; gap: 18px; max-width: 700px; }
.eyebrow {
  width: fit-content;
  min-height: 32px;
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(214,178,94,0.34);
  border-radius: 999px;
  padding: 0 12px;
  color: var(--atlas-gold-soft);
  background: rgba(214,178,94,0.075);
  font-size: 12px;
  font-weight: 820;
  text-transform: uppercase;
}
h1 {
  margin: 0;
  font-size: clamp(42px, 7vw, 86px);
  line-height: 0.95;
  letter-spacing: 0;
}
.lead {
  margin: 0;
  max-width: 620px;
  color: var(--atlas-muted);
  font-size: clamp(17px, 2.2vw, 22px);
  line-height: 1.5;
}
.role-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}
.role-card {
  min-height: 430px;
  display: grid;
  grid-template-rows: 178px 1fr auto;
  gap: 16px;
  padding: 18px;
  border: 1px solid var(--atlas-line);
  border-radius: 18px;
  color: var(--atlas-platinum);
  text-decoration: none;
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.035));
  box-shadow: var(--atlas-shadow-sm);
  overflow: hidden;
  transform: translateY(0);
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}
.role-card:hover {
  transform: translateY(-4px);
  border-color: rgba(214,178,94,0.46);
  box-shadow: var(--atlas-shadow-md);
}
.role-visual {
  position: relative;
  min-height: 178px;
  border-radius: 14px;
  border: 1px solid rgba(238,241,246,0.11);
  background:
    radial-gradient(circle at 50% 40%, rgba(214,178,94,0.24), transparent 32%),
    linear-gradient(135deg, rgba(0,32,80,0.92), rgba(5,7,13,0.48));
  overflow: hidden;
}
.role-visual::before {
  content: "";
  position: absolute;
  inset: 28px;
  border: 2px solid rgba(240,213,139,0.54);
  border-radius: 50%;
  transform: rotate(-18deg);
}
.role-visual::after {
  content: "";
  position: absolute;
  left: 50%;
  top: 50%;
  width: 72px;
  height: 72px;
  border-radius: 18px;
  transform: translate(-50%, -50%) rotate(45deg);
  background: linear-gradient(135deg, rgba(240,213,139,0.96), rgba(176,96,16,0.92));
  box-shadow: 0 0 38px rgba(214,178,94,0.32);
}
.role-card.worker .role-visual { background: radial-gradient(circle at 48% 38%, rgba(56,189,248,0.22), transparent 34%), linear-gradient(135deg, #001020, #0b1324); }
.role-card.employer .role-visual { background: radial-gradient(circle at 48% 38%, rgba(214,178,94,0.24), transparent 34%), linear-gradient(135deg, #101020, #002050); }
.role-card.corporate .role-visual { background: radial-gradient(circle at 48% 38%, rgba(208,208,208,0.19), transparent 34%), linear-gradient(135deg, #05070d, #003070); }
.role-card h2 { margin: 0; font-size: 25px; letter-spacing: 0; }
.role-card p { margin: 0; color: var(--atlas-muted); line-height: 1.45; }
.role-cta {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(214,178,94,0.12);
  color: var(--atlas-gold-soft);
  font-weight: 760;
}
.section-page {
  width: min(1180px, 100%);
  margin: 0 auto;
  padding: clamp(34px, 6vw, 72px) clamp(14px, 4vw, 32px);
}
.section-hero {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(280px, 0.6fr);
  gap: 26px;
  align-items: center;
  margin-bottom: 24px;
}
.section-hero-card {
  min-height: 280px;
  border: 1px solid var(--atlas-line);
  border-radius: 18px;
  background:
    radial-gradient(circle at 50% 42%, rgba(214,178,94,0.2), transparent 34%),
    linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.035));
  box-shadow: var(--atlas-shadow-md);
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
.feature-card {
  min-height: 118px;
  display: grid;
  align-content: space-between;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--atlas-line);
  border-radius: 14px;
  background: rgba(255,255,255,0.045);
}
.feature-card span { color: var(--atlas-gold-soft); font-size: 12px; font-weight: 800; }
.feature-card strong { font-size: 15px; line-height: 1.3; }
.page-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 22px; }
.button {
  min-height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--atlas-line-strong);
  border-radius: 12px;
  padding: 0 16px;
  color: var(--atlas-platinum);
  text-decoration: none;
  font-weight: 720;
}
.button.primary {
  color: #080b13;
  background: linear-gradient(135deg, #e1bf72, #f4dc9e 48%, #c99a3d);
  border-color: rgba(255,255,255,0.16);
}
.gdpr-copy {
  display: grid;
  gap: 14px;
  color: var(--atlas-muted);
  line-height: 1.62;
}
.gdpr-copy h2 { color: var(--atlas-platinum); margin: 18px 0 0; }
@media (max-width: 1080px) {
  .hero-home { grid-template-columns: 1fr; }
  .role-grid { grid-template-columns: 1fr; }
  .role-card { min-height: 0; grid-template-columns: 180px 1fr; grid-template-rows: auto auto; }
  .role-card .role-cta { grid-column: 2; }
  .feature-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .site-header { align-items: flex-start; flex-direction: column; gap: 10px; }
  .site-header .brand-mark-subtitle { display: none; }
  .site-header .brand-mark-image { width: 38px; height: 38px; border-radius: 10px; }
  .main-nav {
    width: 100%;
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 7px;
    font-size: 12px;
  }
  .main-nav a, .language-button { min-height: 34px; justify-content: center; padding-inline: 8px; width: 100%; }
  .main-nav .crm-login { grid-column: 1 / -1; }
  .language-selector { display: grid; grid-column: 1 / -1; }
  .language-menu { right: auto; left: 0; width: min(260px, calc(100vw - 28px)); }
  .hero-home { min-height: auto; padding-top: 28px; }
  .role-card { grid-template-columns: 1fr; grid-template-rows: 170px auto auto; }
  .role-card .role-cta { grid-column: auto; }
  .section-hero { grid-template-columns: 1fr; }
  .section-hero-card { min-height: 190px; }
  .feature-grid { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
"""

SPLASH_CSS = """
.splash {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 50% 34%, rgba(214,178,94,0.16), transparent 30%),
    radial-gradient(circle at 50% 50%, rgba(0,96,192,0.18), transparent 38%),
    #05070d;
  transition: opacity 520ms ease, visibility 520ms ease;
}
.splash.done { opacity: 0; visibility: hidden; pointer-events: none; }
.splash-inner { display: grid; justify-items: center; gap: 16px; text-align: center; }
.splash-logo {
  position: relative;
  width: min(360px, 78vw);
  aspect-ratio: 1;
  display: grid;
  place-items: center;
}
.splash-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 0 28px rgba(214,178,94,0.28));
  animation: goldGlow 2.1s ease-in-out infinite;
}
.splash-logo::after {
  content: "";
  position: absolute;
  width: 82%;
  height: 30%;
  border: 2px solid rgba(240,213,139,0.76);
  border-left-color: transparent;
  border-right-color: rgba(255,255,255,0.18);
  border-radius: 50%;
  transform: rotate(-17deg);
  animation: orbitSweep 1.95s linear infinite;
  box-shadow: 0 0 22px rgba(214,178,94,0.24);
}
.splash-title {
  opacity: 0;
  color: var(--atlas-platinum);
  font-weight: 820;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  animation: titleIn 900ms ease 300ms forwards;
}
.splash-status {
  min-height: 22px;
  color: var(--atlas-muted);
  font-size: 14px;
}
.splash-loader {
  width: min(240px, 62vw);
  height: 3px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(255,255,255,0.1);
}
.splash-loader span {
  display: block;
  height: 100%;
  width: 44%;
  border-radius: inherit;
  background: linear-gradient(90deg, transparent, var(--atlas-gold-soft), transparent);
  animation: loaderMove 1.2s ease-in-out infinite;
}
@keyframes goldGlow {
  0%, 100% { filter: drop-shadow(0 0 18px rgba(214,178,94,0.18)); }
  50% { filter: drop-shadow(0 0 38px rgba(214,178,94,0.42)); }
}
@keyframes orbitSweep {
  to { transform: rotate(343deg); }
}
@keyframes titleIn {
  to { opacity: 1; }
}
@keyframes loaderMove {
  0% { transform: translateX(-110%); }
  100% { transform: translateX(240%); }
}
@media (prefers-reduced-motion: reduce) {
  .splash { transition: none; }
  .splash-logo::after, .splash-logo img, .splash-title, .splash-loader span { animation: none !important; opacity: 1; }
}
"""


def _header(active: str = "") -> str:
    nav = [
        ("/employee", "Працівник", "employee"),
        ("/employer", "Роботодавець", "employer"),
        ("/corporate", "Корпорація", "corporate"),
        ("/gdpr", "GDPR / RODO", "gdpr"),
    ]
    links = "\n".join(
        f'<a href="{href}" class="{"active" if active == key else ""}">{label}</a>'
        for href, label, key in nav
    )
    return f"""
<header class="site-header">
  {BRAND_MARK_HTML}
  <nav class="main-nav" aria-label="Main navigation">
    {links}
    <div class="language-selector" data-language-selector>
      <button class="language-button" type="button" aria-expanded="false" data-language-button>
        <span>Мова</span><span class="language-current" data-language-current>UK</span>
      </button>
      <div class="language-menu" role="menu" data-language-menu></div>
    </div>
    <a class="crm-login" href="/crm/login"><span class="shield-icon" aria-hidden="true"></span>Увійти в CRM</a>
  </nav>
</header>
"""


def _html(title: str, body: str, page_name: str, active: str = "") -> str:
    return f"""<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <link rel="icon" href="/static/brand/atlas-symbol.png" type="image/png" />
  {observability_head_html()}
  <style>
    {BRAND_LOGO_CSS}
    {ATLAS_DESIGN_SYSTEM_CSS}
    {BASE_CSS}
  </style>
</head>
<body>
  <div class="page-shell">
    {_header(active)}
    {body}
  </div>
  {observability_body_html(page_name)}
  <script src="/static/i18n.js?v=20260711-langfix"></script>
  <script>
    if (window.AtlasI18n) window.AtlasI18n.init();
  </script>
</body>
</html>"""


def _role_card(card: dict[str, str]) -> str:
    return f"""
<a class="role-card {card["tone"]}" href="{card["href"]}">
  <div class="role-visual" aria-hidden="true"></div>
  <div>
    <h2>{escape(card["title"])}</h2>
    <p>{escape(card["subtitle"])}</p>
  </div>
  <span class="role-cta">{escape(card["cta"])}</span>
</a>
"""


LANDING_HTML = _html(
    "ATLAS by EWU",
    f"""
<div class="splash" id="splash" aria-live="polite">
  <div class="splash-inner">
    <div class="splash-logo">
      <img src="/static/brand/atlas-logo-primary.png?v=20260718-brand-system" alt="ATLAS by EWU" />
    </div>
    <div class="splash-title">ATLAS by EWU</div>
    <div class="splash-status" id="splash-status">Ініціалізація AI-системи</div>
    <div class="splash-loader" aria-hidden="true"><span></span></div>
  </div>
</div>
<style>{SPLASH_CSS}</style>
<main>
  <section class="hero-home">
    <div class="hero-copy">
      <span class="eyebrow">AI workforce platform</span>
      <h1>ATLAS для роботи, людей і бізнесу</h1>
      <p class="lead">Преміальна платформа EWU для працівників, роботодавців і корпорацій: профілі, вакансії, AI-підбір, документи, CRM і захищене керування даними.</p>
    </div>
    <div class="role-grid" aria-label="Оберіть роль">
      {"".join(_role_card(card) for card in ROLE_CARDS)}
    </div>
  </section>
</main>
<script>
  (function () {{
    const splash = document.getElementById("splash");
    if (!splash) return;
    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const firstVisit = !sessionStorage.getItem("atlasSplashSeen");
    if (!firstVisit || reduce) {{
      splash.classList.add("done");
      sessionStorage.setItem("atlasSplashSeen", "1");
      return;
    }}
    const statuses = [
      "Ініціалізація AI-системи",
      "Завантаження персональних агентів",
      "Підготовка захищеного середовища"
    ];
    const statusNode = document.getElementById("splash-status");
    let index = 0;
    const interval = window.setInterval(() => {{
      index = (index + 1) % statuses.length;
      statusNode.textContent = statuses[index];
    }}, 620);
    const started = performance.now();
    const finish = () => {{
      const elapsed = performance.now() - started;
      window.setTimeout(() => {{
        window.clearInterval(interval);
        sessionStorage.setItem("atlasSplashSeen", "1");
        splash.classList.add("done");
      }}, Math.max(0, 1850 - elapsed));
    }};
    if (document.readyState === "complete") finish();
    else window.addEventListener("load", finish, {{ once: true }});
    window.setTimeout(finish, 2450);
  }})();
</script>
""",
    "landing",
)


def _feature_cards(features: list[str]) -> str:
    return "".join(
        f'<article class="feature-card"><span>{idx:02d}</span><strong>{escape(feature)}</strong></article>'
        for idx, feature in enumerate(features, start=1)
    )


def role_page(title: str, subtitle: str, features: list[str], active: str, primary_href: str, primary_label: str) -> str:
    return _html(
        f"ATLAS | {title}",
        f"""
<main class="section-page">
  <section class="section-hero">
    <div class="hero-copy">
      <span class="eyebrow">ATLAS role workspace</span>
      <h1>{escape(title)}</h1>
      <p class="lead">{escape(subtitle)}</p>
      <div class="page-actions">
        <a class="button primary" href="{primary_href}">{escape(primary_label)}</a>
        <a class="button" href="/">Повернутись до вибору ролі</a>
      </div>
    </div>
    <div class="section-hero-card" aria-hidden="true"></div>
  </section>
  <section class="feature-grid" aria-label="Можливості">
    {_feature_cards(features)}
  </section>
</main>
""",
        active,
        active,
    )


EMPLOYEE_HTML = role_page(
    "Працівник",
    "Персональний простір для створення професійного профілю, CV, пошуку роботи, перевірки документів і керування приватністю.",
    EMPLOYEE_FEATURES,
    "employee",
    "/agent/onboarding",
    "Створити профіль",
)

EMPLOYER_HTML = role_page(
    "Роботодавець",
    "Робочий простір для вакансій, AI-підбору кандидатів, рекрутаційної воронки, документів, аналітики та CRM.",
    EMPLOYER_FEATURES,
    "employer",
    "/employer/chat",
    "Почати підбір",
)

CORPORATE_HTML = role_page(
    "Корпорація",
    "Enterprise-рівень ATLAS для HRM, CRM, AI-аудиту, прогнозування персоналу, автоматизації, інтеграцій і безпеки.",
    CORPORATE_FEATURES,
    "corporate",
    "/control-center",
    "Відкрити Control Center",
)


GDPR_HTML = _html(
    "ATLAS | GDPR / RODO",
    """
<main class="section-page">
  <section class="section-hero">
    <div class="hero-copy">
      <span class="eyebrow">Data protection</span>
      <h1>GDPR / RODO</h1>
      <p class="lead">Політика захисту персональних даних ATLAS by EWU для кандидатів, роботодавців, корпоративних клієнтів і координаторів.</p>
    </div>
    <div class="section-hero-card" aria-hidden="true"></div>
  </section>
  <section class="gdpr-copy">
    <p>ATLAS обробляє персональні дані лише для створення профілів, підбору вакансій, рекрутингової комунікації, перевірки документів, підтримки AI-агентів і виконання операційних обов'язків EWU.</p>
    <h2>Категорії даних</h2>
    <p>Контактні дані, професійний досвід, навички, мови, документи, бажані країни роботи, історія заявок, статуси CRM, технічні журнали безпеки та згода на обробку.</p>
    <h2>Права користувача</h2>
    <p>Користувач може запросити доступ, виправлення, експорт, обмеження обробки або видалення даних. Запити обробляються через захищені CRM-процеси ATLAS.</p>
    <h2>Безпека</h2>
    <p>CRM-маршрути захищені авторизацією. Адміністративний доступ контролюється сесією, обмеженням спроб входу та окремими server-side перевірками.</p>
    <div class="page-actions">
      <a class="button primary" href="/crm/login">Увійти в CRM</a>
      <a class="button" href="/">На головну</a>
    </div>
  </section>
</main>
""",
    "gdpr",
    "gdpr",
)
