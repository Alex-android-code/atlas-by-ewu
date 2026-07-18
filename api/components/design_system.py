"""Centralized ATLAS premium design system tokens and shared CSS."""


ATLAS_DESIGN_SYSTEM_CSS = """
:root {
  color-scheme: dark;
  /* Audited from approved ATLAS assets on 2026-07-18. */
  --atlas-navy-950: #05070d;
  --atlas-navy-925: #001020;
  --atlas-navy-900: #090d18;
  --atlas-navy-850: #0b1324;
  --atlas-blue-800: #002050;
  --atlas-blue-700: #003070;
  --atlas-blue-600: #004090;
  --atlas-blue-500: #0060c0;
  --atlas-gold-700: #a06010;
  --atlas-gold-600: #b06010;
  --atlas-gold-500: #d6b25e;
  --atlas-gold-400: #ffc040;
  --atlas-gold-300: #f0d58b;
  --atlas-silver-600: #a0a0a0;
  --atlas-silver-500: #d0d0d0;
  --atlas-silver-300: #eef1f6;
  --atlas-white: #ffffff;
  --atlas-text-primary: var(--atlas-silver-300);
  --atlas-text-secondary: rgba(238,241,246,0.68);
  --atlas-text-subtle: rgba(238,241,246,0.48);
  --atlas-ai-glow: rgba(0,96,192,0.42);
  --atlas-info: #38bdf8;
  --atlas-bg: var(--atlas-navy-950);
  --atlas-bg-2: var(--atlas-navy-900);
  --atlas-midnight: var(--atlas-navy-850);
  --atlas-panel: rgba(255,255,255,0.055);
  --atlas-panel-strong: rgba(255,255,255,0.082);
  --atlas-elevated: rgba(12,18,32,0.86);
  --atlas-platinum: var(--atlas-silver-300);
  --atlas-muted: var(--atlas-text-secondary);
  --atlas-subtle: var(--atlas-text-subtle);
  --atlas-line: rgba(238,241,246,0.115);
  --atlas-line-strong: rgba(238,241,246,0.18);
  --atlas-gold: var(--atlas-gold-500);
  --atlas-gold-soft: var(--atlas-gold-300);
  --atlas-success: #4ade80;
  --atlas-danger: #fb7185;
  --atlas-warning: #f7c66a;
  --atlas-radius-xs: 8px;
  --atlas-radius-sm: 10px;
  --atlas-radius-md: 14px;
  --atlas-radius-lg: 18px;
  --atlas-radius-xl: 24px;
  --atlas-space-1: 4px;
  --atlas-space-2: 8px;
  --atlas-space-3: 12px;
  --atlas-space-4: 16px;
  --atlas-space-5: 20px;
  --atlas-space-6: 24px;
  --atlas-space-8: 32px;
  --atlas-space-10: 40px;
  --atlas-space-12: 48px;
  --atlas-shadow-sm: 0 1px 0 rgba(255,255,255,0.05), 0 12px 30px rgba(0,0,0,0.24);
  --atlas-shadow-md: 0 1px 0 rgba(255,255,255,0.06), 0 22px 60px rgba(0,0,0,0.34);
  --atlas-shadow-lg: 0 1px 0 rgba(255,255,255,0.07), 0 32px 90px rgba(0,0,0,0.42);
  --atlas-font: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --atlas-page-max: 1240px;
}
* { box-sizing: border-box; }
html { text-rendering: geometricPrecision; -webkit-font-smoothing: antialiased; }
body {
  font-family: var(--atlas-font);
  color: var(--atlas-platinum);
  background:
    radial-gradient(circle at 20% -10%, rgba(214,178,94,0.13), transparent 31%),
    radial-gradient(circle at 78% 0%, rgba(238,241,246,0.055), transparent 26%),
    linear-gradient(180deg, var(--atlas-bg) 0%, var(--atlas-bg-2) 46%, var(--atlas-midnight) 100%);
}
body::before {
  opacity: 0.45;
}
a { color: inherit; }
button, input, textarea, select {
  font: inherit;
}
button, a, input, textarea, select {
  -webkit-tap-highlight-color: transparent;
}
:focus-visible {
  outline: 2px solid rgba(240,213,139,0.92);
  outline-offset: 3px;
}
::selection {
  background: rgba(214,178,94,0.28);
  color: var(--atlas-white);
}
.brand-logo-image {
  filter: drop-shadow(0 18px 40px rgba(0,0,0,0.32));
}
.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--atlas-white);
  text-decoration: none;
  min-width: 0;
}
.brand-mark-image {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  object-fit: cover;
  box-shadow: var(--atlas-shadow-sm);
}
.brand-mark-text {
  display: grid;
  gap: 2px;
  line-height: 1;
  min-width: 0;
}
.brand-mark-name {
  font-size: 13px;
  font-weight: 760;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--atlas-platinum);
}
.brand-mark-subtitle {
  color: var(--atlas-subtle);
  font-size: 11px;
  font-weight: 560;
  letter-spacing: 0.03em;
}
header {
  border-bottom: 1px solid var(--atlas-line) !important;
  background: rgba(5,7,13,0.78) !important;
  backdrop-filter: blur(22px) saturate(135%);
}
nav, .top-nav {
  color: var(--atlas-muted) !important;
}
nav a, .top-nav a, .language-button {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0 10px;
  color: inherit;
  text-decoration: none;
  transition: color 160ms ease, background 160ms ease, border-color 160ms ease;
}
nav a:hover, nav a.active, .top-nav a:hover, .top-nav a.active {
  color: var(--atlas-white) !important;
  background: rgba(255,255,255,0.06);
}
.login-link, .nav-primary {
  border: 1px solid rgba(214,178,94,0.42) !important;
  background: rgba(214,178,94,0.075) !important;
  color: var(--atlas-gold-soft) !important;
}
.language-current {
  color: var(--atlas-gold-soft) !important;
}
.language-menu {
  border: 1px solid var(--atlas-line-strong) !important;
  border-radius: var(--atlas-radius-md) !important;
  background: rgba(8,11,20,0.97) !important;
  box-shadow: var(--atlas-shadow-md);
}
.language-option {
  border-radius: var(--atlas-radius-sm) !important;
  color: var(--atlas-muted) !important;
}
.language-option:hover, .language-option.active {
  color: var(--atlas-white) !important;
  background: rgba(255,255,255,0.07) !important;
}
.button, .cta-button, button.primary, .send, form button[type="submit"] {
  border-radius: var(--atlas-radius-md) !important;
  transition: transform 140ms ease, background 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}
.button:hover, .cta-button:hover, button.primary:hover, .send:hover, form button[type="submit"]:hover {
  transform: translateY(-1px);
}
.button:active, .cta-button:active, button.primary:active, .send:active, form button[type="submit"]:active {
  transform: translateY(0);
}
.button.primary, button.primary, .send, form button[type="submit"] {
  background: linear-gradient(135deg, #e1bf72 0%, #f4dc9e 48%, #c99a3d 100%) !important;
  color: #080b13 !important;
  border-color: rgba(255,255,255,0.18) !important;
  box-shadow: 0 14px 34px rgba(214,178,94,0.20) !important;
}
.button:not(.primary), .cta-button:not(.primary), button:not(.primary):not(.send):not(.language-button):not(.menu-toggle) {
  border-color: var(--atlas-line-strong);
}
input, textarea, select {
  border-color: var(--atlas-line-strong) !important;
  background: rgba(255,255,255,0.045) !important;
  color: var(--atlas-platinum) !important;
}
input::placeholder, textarea::placeholder {
  color: rgba(238,241,246,0.43) !important;
}
input:focus, textarea:focus, select:focus, .inputbar:focus-within {
  border-color: rgba(240,213,139,0.62) !important;
  box-shadow: 0 0 0 4px rgba(214,178,94,0.11);
}
.card, .dashboard-card, .top-status, .chat-shell, .smart-dashboard, .analysis-panel,
.profile-preview-card, .trust-card, .step-card, .map-card, .box, .panel .card {
  border: 1px solid var(--atlas-line) !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.075), rgba(255,255,255,0.038)) !important;
  box-shadow: var(--atlas-shadow-sm) !important;
  backdrop-filter: blur(18px) saturate(130%);
}
.chip, .badge, .eyebrow, .live-pill {
  border-color: rgba(238,241,246,0.15) !important;
  background: rgba(255,255,255,0.055) !important;
  color: var(--atlas-muted) !important;
  box-shadow: none !important;
}
.pulse-dot, .eyebrow::before {
  box-shadow: none !important;
}
table {
  border-collapse: collapse;
}
th {
  color: var(--atlas-subtle);
  font-weight: 640;
}
@media (max-width: 760px) {
  header {
    gap: 10px !important;
    min-height: 64px !important;
    padding: calc(8px + env(safe-area-inset-top)) 12px 8px !important;
    align-items: center !important;
  }
  .brand-mark-image {
    width: 36px;
    height: 36px;
    border-radius: 11px;
  }
  .brand-mark {
    gap: 9px;
    flex: 0 0 auto;
  }
  .brand-mark-name {
    font-size: 12px;
    letter-spacing: 0.14em;
  }
  .brand-mark-subtitle {
    display: none;
  }
  nav, .top-nav {
    width: 100% !important;
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
    overflow-x: auto;
    scrollbar-width: none;
    padding-bottom: 2px;
  }
  nav::-webkit-scrollbar, .top-nav::-webkit-scrollbar {
    display: none;
  }
  nav a, .top-nav a, .language-button {
    min-height: 34px;
    flex: 0 0 auto;
    padding: 0 9px;
    font-size: 12px;
  }
  .language-menu {
    left: 0;
    right: auto !important;
    min-width: min(220px, calc(100vw - 24px)) !important;
  }
  .card, .dashboard-card, .top-status, .chat-shell, .smart-dashboard, .analysis-panel,
  .profile-preview-card, .trust-card, .step-card, .map-card, .box, .panel .card {
    border-radius: 14px !important;
  }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.001ms !important;
  }
}
"""
