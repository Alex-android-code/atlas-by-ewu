"""Premium ATLAS main interface and role pages."""

from __future__ import annotations

from html import escape

from api.components.brand_logo import BRAND_LOGO_CSS, BRAND_LOGO_HTML, BRAND_MARK_HTML
from api.components.design_system import ATLAS_DESIGN_SYSTEM_CSS
from api.observability import observability_body_html, observability_head_html


ROLE_CARDS = [
    {
        "key": "employee",
        "title": "Працівник",
        "subtitle": "Профіль, AI-агент, CV, робота, документи і кар'єрна карта.",
        "href": "/employee",
        "tone": "worker",
        "cta": "Обрати працівника",
    },
    {
        "key": "employer",
        "title": "Роботодавець",
        "subtitle": "Вакансії, AI-підбір, комунікація, рекрутинг і аналітика.",
        "href": "/employer",
        "tone": "employer",
        "cta": "Обрати роботодавця",
    },
    {
        "key": "corporate",
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
.world-section {
  padding: 20px clamp(14px, 4vw, 44px) 70px;
}
.world-inner {
  width: min(1540px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(560px, 1.25fr) minmax(300px, 0.45fr);
  gap: 20px;
  align-items: stretch;
}
.world-copy {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: end;
  border-top: 1px solid var(--atlas-line);
  padding-top: 26px;
}
.world-copy h2 {
  margin: 0;
  font-size: clamp(28px, 4vw, 48px);
}
.world-copy p {
  max-width: 620px;
  margin: 8px 0 0;
  color: var(--atlas-muted);
  line-height: 1.5;
}
.globe-card, .country-details {
  border: 1px solid var(--atlas-line);
  border-radius: 18px;
  background:
    radial-gradient(circle at 50% 10%, rgba(0,96,192,0.16), transparent 30%),
    linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.035));
  box-shadow: var(--atlas-shadow-md);
}
.globe-card {
  min-height: 860px;
  position: relative;
  overflow: hidden;
}
.globe-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 18%, rgba(255,255,255,0.32) 0 1px, transparent 1.8px),
    radial-gradient(circle at 74% 22%, rgba(255,255,255,0.22) 0 1px, transparent 1.8px),
    radial-gradient(circle at 62% 76%, rgba(255,255,255,0.2) 0 1px, transparent 1.8px);
  opacity: 0.55;
}
.globe-canvas {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  min-height: 860px;
  display: block;
  cursor: grab;
}
.globe-canvas:active { cursor: grabbing; }
.globe-legend {
  position: absolute;
  left: 16px;
  bottom: 16px;
  z-index: 2;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.status-chip {
  min-height: 28px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 1px solid var(--atlas-line);
  border-radius: 999px;
  padding: 0 10px;
  color: var(--atlas-muted);
  background: rgba(5,7,13,0.72);
  font-size: 12px;
  backdrop-filter: blur(12px);
}
.status-chip::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--atlas-silver-600);
}
.status-chip.active::before { background: var(--atlas-gold-400); box-shadow: 0 0 14px rgba(255,192,64,0.5); }
.status-chip.launching::before { background: var(--atlas-info); box-shadow: 0 0 14px rgba(56,189,248,0.34); }
.status-chip.planned::before { background: var(--atlas-silver-500); }
.country-details {
  min-height: 560px;
  padding: 18px;
  display: grid;
  align-content: start;
  gap: 14px;
}
.country-details h3 { margin: 0; font-size: 25px; }
.country-flag {
  width: 54px;
  height: 36px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid var(--atlas-line);
  background: rgba(255,255,255,0.08);
}
.country-head {
  display: flex;
  gap: 12px;
  align-items: center;
}
.country-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.country-stat {
  padding: 11px;
  border: 1px solid rgba(238,241,246,0.1);
  border-radius: 12px;
  background: rgba(255,255,255,0.04);
}
.country-stat span { display: block; color: var(--atlas-muted); font-size: 12px; }
.country-stat strong { display: block; margin-top: 3px; color: var(--atlas-platinum); }
.country-stat small { display: block; margin-top: 4px; color: var(--atlas-muted); line-height: 1.3; }
.audience-card {
  border-color: rgba(214,178,94,0.24);
  background: linear-gradient(180deg, rgba(214,178,94,0.13), rgba(255,255,255,0.04));
}
.audience-card.employer {
  border-color: rgba(56,189,248,0.22);
  background: linear-gradient(180deg, rgba(56,189,248,0.12), rgba(255,255,255,0.04));
}
.audience-card strong { font-size: 28px; color: var(--atlas-gold-soft); }
.button.disabled {
  opacity: 0.72;
  cursor: not-allowed;
  pointer-events: none;
}
.country-services {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
}
.country-services span {
  min-height: 28px;
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(214,178,94,0.24);
  border-radius: 999px;
  padding: 0 9px;
  color: var(--atlas-gold-soft);
  background: rgba(214,178,94,0.065);
  font-size: 12px;
}
.globe-fallback {
  display: none;
  position: absolute;
  inset: 20px;
  z-index: 3;
  align-content: center;
  gap: 10px;
}
.globe-card.fallback .globe-canvas { opacity: 0.18; }
.globe-card.fallback .globe-fallback { display: grid; }
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
  .world-inner { grid-template-columns: 1fr; }
  .globe-card, .globe-canvas { min-height: 700px; }
  .country-details { min-height: 460px; }
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
  .world-section { padding-bottom: 42px; }
  .world-copy { display: grid; }
  .globe-card, .globe-canvas { min-height: 560px; }
  .country-details { min-height: 0; }
  .country-details { min-height: 0; }
  .country-grid { grid-template-columns: 1fr; }
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

GLOBE_SCRIPT = """
<script>
  (function () {
    const canvas = document.getElementById("atlas-globe");
    const panel = document.getElementById("country-panel");
    const fallback = document.getElementById("globe-fallback-list");
    const globeCard = document.querySelector(".globe-card");
    if (!canvas || !panel) return;

    const ctx = canvas.getContext("2d");
    const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const lowPower = window.innerWidth < 720 || (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4);
    let countries = [];
    let countryShapes = [];
    let countryByCode = new Map();
    let lastCountryPaths = [];
    let markers = [];
    let rotation = -18;
    let selected = null;
    let dragging = false;
    let lastX = 0;
    const textures = {
      day: loadTexture("/static/assets/earth_atmos_2048.jpg"),
      night: loadTexture("/static/assets/earth_lights_2048.png"),
      clouds: loadTexture("/static/assets/earth_clouds_1024.png"),
    };
    let texturesReady = false;

    fetch("/static/assets/world-countries-110m.geojson", {cache: "force-cache"})
      .then(response => response.ok ? response.json() : null)
      .then(data => {
        countryShapes = (data?.features || [])
          .map(feature => ({
            code: String(feature.properties?.ISO_A2 || feature.properties?.iso_a2 || "").toUpperCase(),
            name: feature.properties?.ADMIN || feature.properties?.NAME || "Country",
            geometry: feature.geometry,
          }))
          .filter(feature => feature.code && feature.code !== "-99" && feature.geometry);
        draw();
      })
      .catch(() => {
        countryShapes = [];
      });

    function loadTexture(src) {
      const image = new Image();
      image.onload = () => {
        texturesReady = Object.values(textures).every(texture => texture.complete && texture.naturalWidth > 0);
        draw();
      };
      image.onerror = () => globeCard.classList.add("fallback");
      image.src = src;
      return image;
    }

    function supportsWebGL() {
      try {
        const test = document.createElement("canvas");
        return Boolean(test.getContext("webgl") || test.getContext("experimental-webgl"));
      } catch (error) {
        return false;
      }
    }

    function resize() {
      const rect = canvas.getBoundingClientRect();
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(320, Math.floor(rect.width * ratio));
      canvas.height = Math.max(320, Math.floor(rect.height * ratio));
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      draw();
    }

    function statusLabel(status) {
      const key = {active: "main.status.active", launching: "main.status.launching", planned: "main.status.planned"}[status] || "main.status.planned";
      return tr(key, {active: "Active", launching: "Launching", planned: "Planned"}[status] || "Planned");
    }

    function tr(key, fallback) {
      return window.AtlasI18n?.t ? window.AtlasI18n.t(key, fallback) : (fallback || key);
    }

    function statusColor(status) {
      if (status === "active") return "#ffc040";
      if (status === "launching") return "#38bdf8";
      return "#d0d0d0";
    }

    function countryRecord(shape) {
      return countryByCode.get(shape.code) || {
        id: `shape-${shape.code}`,
        code: shape.code,
        name: shape.name,
        flag_url: "",
        latitude: 0,
        longitude: 0,
        status: "planned",
        languages: [],
        currency: "-",
        services: [],
        partners: [],
        vacancies_count: 0,
        candidates_count: 0,
        legalization_available: false,
        training_available: false,
        route: `/countries/${shape.code.toLowerCase()}`,
        is_visible: false,
      };
    }

    function project(lat, lon, radius, centerX, centerY) {
      const phi = lat * Math.PI / 180;
      const theta = (lon - rotation) * Math.PI / 180;
      const x = centerX + radius * Math.cos(phi) * Math.sin(theta);
      const y = centerY - radius * Math.sin(phi) * 0.92;
      const z = Math.cos(phi) * Math.cos(theta);
      return {x, y, z};
    }

    function drawEarth(cx, cy, radius) {
      drawStarField(cx, cy, radius);

      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.clip();
      if (texturesReady) {
        drawTexturedSphere(textures.day, cx, cy, radius, 1, rotation, "source-over");
        if (!lowPower) drawTexturedSphere(textures.night, cx, cy, radius, 0.72, rotation, "screen");
        drawTexturedSphere(textures.clouds, cx, cy, radius, lowPower ? 0.18 : 0.3, rotation * 1.12 + 18, "screen");
      } else {
        const loadingOcean = ctx.createRadialGradient(cx - radius * 0.34, cy - radius * 0.36, radius * 0.04, cx, cy, radius);
        loadingOcean.addColorStop(0, "#85d7ff");
        loadingOcean.addColorStop(0.36, "#0050a0");
        loadingOcean.addColorStop(1, "#000010");
        ctx.fillStyle = loadingOcean;
        ctx.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);
      }
      ctx.restore();

      drawCountryLayer(cx, cy, radius);

      const shade = ctx.createRadialGradient(cx - radius * 0.34, cy - radius * 0.28, radius * 0.2, cx + radius * 0.24, cy + radius * 0.18, radius * 1.05);
      shade.addColorStop(0, "rgba(255,255,255,0.18)");
      shade.addColorStop(0.42, "rgba(255,255,255,0)");
      shade.addColorStop(0.74, "rgba(1,7,20,0.42)");
      shade.addColorStop(1, "rgba(0,0,12,0.78)");
      ctx.fillStyle = shade;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      const atmosphere = ctx.createRadialGradient(cx, cy, radius * 0.76, cx, cy, radius * 1.28);
      atmosphere.addColorStop(0, "rgba(56,189,248,0)");
      atmosphere.addColorStop(0.72, "rgba(56,189,248,0.18)");
      atmosphere.addColorStop(0.92, "rgba(120,210,255,0.2)");
      atmosphere.addColorStop(1, "rgba(240,213,139,0.1)");
      ctx.fillStyle = atmosphere;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.24, 0, Math.PI * 2);
      ctx.fill();
    }

    function drawCountryLayer(cx, cy, radius) {
      lastCountryPaths = [];
      if (!countryShapes.length) return;
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.clip();
      countryShapes.forEach(shape => {
        const record = countryRecord(shape);
        const path = buildCountryPath(shape.geometry, cx, cy, radius);
        if (!path) return;
        const isAtlasCountry = countryByCode.has(shape.code);
        if (isAtlasCountry) {
          ctx.globalAlpha = record.id === selected ? 0.42 : 0.22;
          ctx.fillStyle = statusColor(record.status);
          ctx.fill(path);
        }
        ctx.globalAlpha = isAtlasCountry ? 0.82 : 0.42;
        ctx.strokeStyle = isAtlasCountry ? "rgba(255,214,125,0.9)" : "rgba(224,240,255,0.48)";
        ctx.lineWidth = isAtlasCountry ? 1.55 : 0.9;
        ctx.stroke(path);
        lastCountryPaths.push({path, shape, country: record, isAtlasCountry});
      });
      ctx.globalAlpha = 1;
      ctx.restore();
    }

    function buildCountryPath(geometry, cx, cy, radius) {
      const path = new Path2D();
      let hasVisiblePoint = false;
      const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.type === "MultiPolygon" ? geometry.coordinates : [];
      polygons.forEach(polygon => {
        polygon.forEach(ring => {
          let drawing = false;
          ring.forEach(([lon, lat]) => {
            const point = project(Number(lat), Number(lon), radius, cx, cy);
            if (point.z < -0.08) {
              drawing = false;
              return;
            }
            hasVisiblePoint = true;
            if (!drawing) {
              path.moveTo(point.x, point.y);
              drawing = true;
            } else {
              path.lineTo(point.x, point.y);
            }
          });
          if (drawing) path.closePath();
        });
      });
      return hasVisiblePoint ? path : null;
    }

    function drawTexturedSphere(image, cx, cy, radius, alpha, spin, compositeOperation) {
      if (!image.complete || !image.naturalWidth) return;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.globalCompositeOperation = compositeOperation || "source-over";
      const step = lowPower ? 2 : 0.75;
      for (let dx = -radius; dx <= radius; dx += step) {
        const nx = dx / radius;
        const z = Math.sqrt(Math.max(0, 1 - nx * nx));
        const stripHeight = radius * 2 * z;
        const longitude = Math.atan2(nx, z) * 180 / Math.PI;
        const sourceX = ((((longitude + spin + 540) % 360) / 360) * image.naturalWidth) | 0;
        ctx.drawImage(
          image,
          sourceX,
          0,
          2,
          image.naturalHeight,
          cx + dx,
          cy - stripHeight / 2,
          step + 0.8,
          stripHeight
        );
      }
      ctx.restore();
    }

    function drawStarField(cx, cy, radius) {
      if (lowPower) return;
      ctx.save();
      ctx.globalAlpha = 0.42;
      ctx.fillStyle = "rgba(224,240,255,0.9)";
      for (let i = 0; i < 90; i += 1) {
        const x = (i * 47 % canvas.clientWidth);
        const y = (i * 83 % canvas.clientHeight);
        if (Math.hypot(x - cx, y - cy) < radius * 1.22) continue;
        ctx.fillRect(x, y, i % 7 === 0 ? 1.6 : 1, i % 7 === 0 ? 1.6 : 1);
      }
      ctx.restore();
    }

    function drawRoutes(cx, cy, radius) {
      const active = markers.filter(item => item.country.status === "active" && item.z > -0.1);
      if (active.length < 2 || lowPower) return;
      ctx.save();
      ctx.strokeStyle = "rgba(240,213,139,0.36)";
      ctx.lineWidth = 1;
      active.slice(0, 4).forEach((from, index) => {
        const to = active[(index + 1) % active.length];
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.quadraticCurveTo(cx, cy - radius * 0.76, to.x, to.y);
        ctx.stroke();
      });
      ctx.restore();
    }

    function drawMarkers(cx, cy, radius) {
      markers = countries.map(country => ({country, ...project(Number(country.latitude), Number(country.longitude), radius, cx, cy)}));
      drawRoutes(cx, cy, radius);
      markers.forEach(marker => {
        if (marker.z < -0.18) return;
        const color = statusColor(marker.country.status);
        const size = marker.country.id === selected ? 9 : 6;
        ctx.globalAlpha = Math.max(0.35, marker.z);
        ctx.fillStyle = color;
        ctx.shadowColor = color;
        ctx.shadowBlur = marker.country.status === "active" ? 18 : 10;
        ctx.beginPath();
        ctx.arc(marker.x, marker.y, size, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.strokeStyle = "rgba(255,255,255,0.72)";
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.globalAlpha = 1;
      });
    }

    function draw() {
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      ctx.clearRect(0, 0, width, height);
      const cx = width / 2;
      const cy = height / 2;
      const radius = Math.min(width, height) * 0.48;
      drawEarth(cx, cy, radius);
      drawMarkers(cx, cy, radius);
    }

    function renderPanel(country) {
      if (!country) {
        panel.innerHTML = `<h3>${tr("main.country.choose_title", "Оберіть країну")}</h3><p class='lead'>${tr("main.country.choose_lead", "Натисніть золотий або срібний маркер на глобусі, щоб побачити локальні можливості ATLAS.")}</p>`;
        return;
      }
      selected = country.id;
      const services = (country.services || []).map(item => `<span>${escapeHtml(item)}</span>`).join("");
      const nationalLink = country.is_visible === false
        ? `<span class="button primary disabled" aria-disabled="true">${tr("main.country.not_connected", "ATLAS не подключён в этой стране")}</span>`
        : `<a class="button primary" href="${escapeHtml(country.route || "/employee")}">${tr("main.country.open", "Перейти до національного розділу")}</a>`;
      panel.innerHTML = `
        <div class="country-head">
          <img class="country-flag" src="${escapeHtml(country.flag_url || "/static/brand/atlas-symbol.png")}" alt="${escapeHtml(country.name)} flag" />
          <div><h3>${escapeHtml(country.name)}</h3><span class="status-chip ${escapeHtml(country.status)}">${statusLabel(country.status)}</span></div>
        </div>
        <div class="country-grid">
          <div class="country-stat audience-card worker"><span>${tr("main.country.worker_view", "Для работника")}</span><strong>${country.vacancies_count || 0}</strong><small>${tr("main.country.worker_vacancies", "вакансий в этой стране")}</small></div>
          <div class="country-stat audience-card employer"><span>${tr("main.country.employer_view", "Для работодателя")}</span><strong>${country.candidates_count || 0}</strong><small>${tr("main.country.employer_candidates", "людей ищут работу")}</small></div>
        </div>
        <div class="country-grid">
          <div class="country-stat"><span>${tr("main.country.vacancies", "Активні вакансії")}</span><strong>${country.vacancies_count || 0}</strong></div>
          <div class="country-stat"><span>${tr("main.country.candidates", "Кандидати")}</span><strong>${country.candidates_count || 0}</strong></div>
          <div class="country-stat"><span>${tr("main.country.languages", "Мови")}</span><strong>${escapeHtml((country.languages || []).join(", ") || "-")}</strong></div>
          <div class="country-stat"><span>${tr("main.country.currency", "Валюта")}</span><strong>${escapeHtml(country.currency || "-")}</strong></div>
          <div class="country-stat"><span>${tr("main.country.legalization", "Легалізація")}</span><strong>${country.legalization_available ? tr("common.yes", "Так") : tr("common.no", "Ні")}</strong></div>
          <div class="country-stat"><span>${tr("main.country.training", "Навчання")}</span><strong>${country.training_available ? tr("common.yes", "Так") : tr("common.no", "Ні")}</strong></div>
        </div>
        <div><strong>${tr("main.country.services", "Сервіси")}</strong><div class="country-services">${services || "<span>ATLAS onboarding</span>"}</div></div>
        <div class="country-stat"><span>${tr("main.country.partners", "Партнери ATLAS")}</span><strong>${escapeHtml((country.partners || []).join(", ") || "EWU network")}</strong></div>
        ${nationalLink}
      `;
      draw();
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
      }[char]));
    }

    function handleClick(event) {
      const rect = canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      for (let index = lastCountryPaths.length - 1; index >= 0; index -= 1) {
        const item = lastCountryPaths[index];
        if (ctx.isPointInPath(item.path, x, y)) {
          renderPanel(item.country);
          return;
        }
      }
      const hit = markers
        .filter(marker => marker.z > -0.18)
        .find(marker => Math.hypot(marker.x - x, marker.y - y) < 18);
      if (hit) renderPanel(hit.country);
    }

    function animate() {
      if (!reduceMotion && !dragging) rotation += 0.045;
      draw();
      requestAnimationFrame(animate);
    }

    async function loadCountries() {
      try {
        const response = await fetch("/api/public/countries", {cache: "no-store"});
        const data = await response.json();
        countries = data.countries || [];
        countryByCode = new Map(countries.map(country => [String(country.code || "").toUpperCase(), country]));
        fallback.innerHTML = countries.map(country => `<button class="button" type="button" data-country="${escapeHtml(country.id)}">${escapeHtml(country.name)} · ${statusLabel(country.status)}</button>`).join("");
        fallback.querySelectorAll("[data-country]").forEach(button => {
          button.addEventListener("click", () => renderPanel(countries.find(country => country.id === button.dataset.country)));
        });
        renderPanel(countries[0]);
      } catch (error) {
        globeCard.classList.add("fallback");
        fallback.innerHTML = `<div class='country-stat'><strong>${tr("main.country.unavailable", "Country data unavailable")}</strong><span>${tr("main.country.refresh_hint", "Try refreshing the page.")}</span></div>`;
      }
    }

    if (!ctx) globeCard.classList.add("fallback");
    canvas.addEventListener("click", handleClick);
    canvas.addEventListener("pointerdown", event => { dragging = true; lastX = event.clientX; canvas.setPointerCapture(event.pointerId); });
    canvas.addEventListener("pointermove", event => {
      if (!dragging) return;
      rotation += (event.clientX - lastX) * 0.25;
      lastX = event.clientX;
      draw();
    });
    canvas.addEventListener("pointerup", () => { dragging = false; });
    window.addEventListener("resize", resize);
    document.addEventListener("atlas:i18n", () => renderPanel(countries.find(country => country.id === selected) || countries[0]));
    resize();
    loadCountries().then(() => requestAnimationFrame(animate));
  })();
</script>
"""


def _header(active: str = "") -> str:
    nav = [
        ("/employee", "Працівник", "employee"),
        ("/employer", "Роботодавець", "employer"),
        ("/corporate", "Корпорація", "corporate"),
        ("/gdpr", "GDPR / RODO", "gdpr"),
    ]
    links = "\n".join(
        f'<a href="{href}" class="{"active" if active == key else ""}" data-i18n="main.nav.{key}">{label}</a>'
        for href, label, key in nav
    )
    return f"""
<header class="site-header">
  {BRAND_MARK_HTML}
  <nav class="main-nav" aria-label="Main navigation">
    {links}
    <div class="language-selector" data-language-selector>
      <button class="language-button" type="button" aria-expanded="false" data-language-button>
        <span data-i18n="main.nav.language">Мова</span><span class="language-current" data-language-current>UK</span>
      </button>
      <div class="language-menu" role="menu" data-language-menu></div>
    </div>
    <a class="crm-login" href="/crm/login"><span class="shield-icon" aria-hidden="true"></span><span data-i18n="main.nav.crm_login">Увійти в CRM</span></a>
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
    <h2 data-i18n="main.role.{card["key"]}.title">{escape(card["title"])}</h2>
    <p data-i18n="main.role.{card["key"]}.subtitle">{escape(card["subtitle"])}</p>
  </div>
  <span class="role-cta" data-i18n="main.role.{card["key"]}.cta">{escape(card["cta"])}</span>
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
    <div class="splash-status" id="splash-status" data-i18n="main.splash.initializing">Ініціалізація AI-системи</div>
    <div class="splash-loader" aria-hidden="true"><span></span></div>
  </div>
</div>
<style>{SPLASH_CSS}</style>
<main>
  <section class="hero-home">
    <div class="hero-copy">
      <span class="eyebrow" data-i18n="main.hero.eyebrow">AI workforce platform</span>
      <h1 data-i18n="main.hero.title">ATLAS для роботи, людей і бізнесу</h1>
      <p class="lead" data-i18n="main.hero.lead">Преміальна платформа EWU для працівників, роботодавців і корпорацій: профілі, вакансії, AI-підбір, документи, CRM і захищене керування даними.</p>
    </div>
    <div class="role-grid" aria-label="Оберіть роль">
      {"".join(_role_card(card) for card in ROLE_CARDS)}
    </div>
  </section>
  <section class="world-section" aria-labelledby="world-title">
    <div class="world-inner">
      <div class="world-copy">
        <div>
          <span class="eyebrow" data-i18n="main.world.eyebrow">Global AI ecosystem</span>
          <h2 id="world-title" data-i18n="main.world.title">ATLAS у світі</h2>
          <p data-i18n="main.world.lead">Країни підключення ATLAS, статус запуску, локальні сервіси, вакансії, кандидати, партнери, легалізаційна підтримка та навчальні програми.</p>
        </div>
      </div>
      <div class="globe-card">
        <canvas class="globe-canvas" id="atlas-globe" aria-label="Інтерактивний 3D-глобус ATLAS" data-i18n-aria-label="main.world.globe_label"></canvas>
        <div class="globe-legend" aria-hidden="true">
          <span class="status-chip active">Active</span>
          <span class="status-chip launching">Launching</span>
          <span class="status-chip planned">Planned</span>
        </div>
        <div class="globe-fallback" id="globe-fallback-list"></div>
      </div>
      <aside class="country-details" id="country-panel">
        <h3 data-i18n="main.country.choose_title">Оберіть країну</h3>
        <p class="lead" data-i18n="main.country.loading">Дані країн завантажуються з API ATLAS.</p>
      </aside>
    </div>
  </section>
</main>
{GLOBE_SCRIPT}
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
      ["main.splash.initializing", "Ініціалізація AI-системи"],
      ["main.splash.loading_agents", "Завантаження персональних агентів"],
      ["main.splash.secure_environment", "Підготовка захищеного середовища"]
    ];
    const statusNode = document.getElementById("splash-status");
    let index = 0;
    const interval = window.setInterval(() => {{
      index = (index + 1) % statuses.length;
      statusNode.textContent = window.AtlasI18n?.t(statuses[index][0], statuses[index][1]) || statuses[index][1];
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
      <span class="eyebrow" data-i18n="main.role_workspace.eyebrow">ATLAS role workspace</span>
      <h1 data-i18n="main.role.{active}.title">{escape(title)}</h1>
      <p class="lead" data-i18n="main.role_page.{active}.subtitle">{escape(subtitle)}</p>
      <div class="page-actions">
        <a class="button primary" href="{primary_href}" data-i18n="main.role_page.{active}.primary">{escape(primary_label)}</a>
        <a class="button" href="/" data-i18n="main.role_page.back">Повернутись до вибору ролі</a>
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


def country_detail_html(country: dict) -> str:
    services = country.get("services") or []
    partners = country.get("partners") or []
    return _html(
        f"ATLAS | {country.get('name', country.get('code', 'Country'))}",
        f"""
<main class="section-page">
  <section class="section-hero">
    <div class="hero-copy">
      <span class="eyebrow">{escape(str(country.get("status", "planned")).title())}</span>
      <h1>{escape(str(country.get("name", country.get("code", "Country"))))}</h1>
      <p class="lead">{escape(str(country.get("seo_description") or "Національний розділ ATLAS із локальними сервісами, вакансіями, партнерами та підтримкою."))}</p>
      <div class="page-actions">
        <a class="button primary" href="/employee">Для працівника</a>
        <a class="button" href="/employer">Для роботодавця</a>
      </div>
    </div>
    <div class="section-hero-card" aria-hidden="true"></div>
  </section>
  <section class="feature-grid" aria-label="Country details">
    <article class="feature-card"><span>01</span><strong>Вакансії: {int(country.get("vacancies_count") or 0)}</strong></article>
    <article class="feature-card"><span>02</span><strong>Кандидати: {int(country.get("candidates_count") or 0)}</strong></article>
    <article class="feature-card"><span>03</span><strong>Мови: {escape(", ".join(country.get("languages") or []) or "-")}</strong></article>
    <article class="feature-card"><span>04</span><strong>Валюта: {escape(str(country.get("currency") or "-"))}</strong></article>
    <article class="feature-card"><span>05</span><strong>Легалізація: {"Так" if country.get("legalization_available") else "Ні"}</strong></article>
    <article class="feature-card"><span>06</span><strong>Навчання: {"Так" if country.get("training_available") else "Ні"}</strong></article>
    <article class="feature-card"><span>07</span><strong>Сервіси: {escape(", ".join(services) or "ATLAS onboarding")}</strong></article>
    <article class="feature-card"><span>08</span><strong>Партнери: {escape(", ".join(partners) or "EWU network")}</strong></article>
  </section>
</main>
""",
        "country",
    )
