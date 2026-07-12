"""Coordinator chat page HTML."""

from api.components.brand_logo import BRAND_LOGO_CSS, BRAND_LOGO_HTML
from api.observability import observability_body_html, observability_head_html


AI_CHAT_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="atlas-title-key" content="coordinator.title" />
  <title>ATLAS Coordinator</title>
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
      --atlas-green: #20c787;
      --atlas-red: #ef4444;
      --atlas-warning: #f4c95d;
      --glass: rgba(255,255,255,0.065);
      --glass-strong: rgba(26,35,56,0.82);
      --line: rgba(230,232,235,0.11);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, Poppins, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 18% 12%, rgba(212,175,55,0.10), transparent 28%),
        radial-gradient(circle at 84% 6%, rgba(245,217,138,0.07), transparent 26%),
        linear-gradient(160deg, #071026 0%, var(--atlas-navy) 48%, #101a33 100%);
      color: var(--atlas-white);
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(230,232,235,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(230,232,235,0.03) 1px, transparent 1px);
      background-size: 54px 54px;
      mask-image: radial-gradient(circle at 50% 16%, black, transparent 72%);
    }
    {{BRAND_LOGO_CSS}}
    header {
      min-height: 76px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px clamp(16px, 3vw, 34px);
      background: rgba(11, 19, 43, 0.78);
      border-bottom: 1px solid rgba(230,232,235,0.10);
      backdrop-filter: blur(22px);
      position: sticky;
      top: 0;
      z-index: 5;
    }
    nav {
      display: flex;
      align-items: center;
      gap: 18px;
      color: var(--atlas-light);
      font-size: 14px;
      font-weight: 500;
    }
    nav a { color: inherit; text-decoration: none; }
    nav a:hover, nav a.active { color: var(--atlas-gold); }
    .login-link {
      border: 1px solid rgba(212,175,55,0.74);
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
      box-shadow: 0 20px 45px rgba(0,0,0,0.28);
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
    .app {
      position: relative;
      min-height: calc(100vh - 76px);
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 18px;
      padding: 18px clamp(14px, 2.5vw, 34px) 24px;
    }
    .top-status {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 16px;
      align-items: center;
      border: 1px solid rgba(212,175,55,0.18);
      border-radius: 22px;
      background: linear-gradient(135deg, rgba(255,255,255,0.075), rgba(255,255,255,0.035));
      box-shadow: 0 18px 48px rgba(0,0,0,0.18);
      padding: 16px;
      backdrop-filter: blur(18px);
    }
    .status-copy { display: grid; gap: 5px; }
    .eyebrow {
      color: var(--atlas-gold-light);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    .status-copy h1 {
      margin: 0;
      font-size: clamp(22px, 2.2vw, 34px);
      line-height: 1.12;
      letter-spacing: 0;
    }
    .status-copy p {
      margin: 0;
      max-width: 760px;
      color: rgba(230,232,235,0.72);
      font-size: 14px;
      line-height: 1.5;
    }
    .status-chips {
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 8px;
    }
    .chip {
      min-height: 36px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid rgba(230,232,235,0.12);
      border-radius: 999px;
      background: rgba(11,19,43,0.34);
      color: var(--atlas-light);
      padding: 0 12px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }
    .chip strong { color: var(--atlas-gold-light); }
    .workspace {
      min-height: 0;
      display: grid;
      grid-template-columns: minmax(0, 70fr) minmax(320px, 30fr);
      gap: 18px;
    }
    .chat-shell,
    .smart-dashboard,
    .dashboard-card {
      border: 1px solid var(--line);
      background: linear-gradient(145deg, rgba(255,255,255,0.075), rgba(255,255,255,0.035));
      box-shadow: 0 18px 48px rgba(0,0,0,0.18);
      backdrop-filter: blur(18px);
    }
    .chat-shell {
      min-height: calc(100vh - 190px);
      display: grid;
      grid-template-rows: auto auto 1fr auto;
      border-radius: 24px;
      overflow: hidden;
    }
    .chat-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      background: rgba(11,19,43,0.28);
    }
    .agent-mini {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .avatar {
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      border: 1px solid rgba(212,175,55,0.36);
      background: radial-gradient(circle at 32% 22%, var(--atlas-gold-light), var(--atlas-gold) 38%, #7e6417 100%);
      color: var(--atlas-navy);
      font-weight: 900;
      box-shadow: 0 0 28px rgba(212,175,55,0.22);
    }
    .avatar.user-avatar {
      border-color: rgba(230,232,235,0.18);
      background: linear-gradient(135deg, #3d4a62, #202b42);
      color: var(--atlas-white);
      box-shadow: none;
    }
    .agent-mini h2 {
      margin: 0;
      font-size: 16px;
      line-height: 1.2;
    }
    .agent-mini span {
      color: rgba(230,232,235,0.66);
      font-size: 12px;
      font-weight: 600;
    }
    .live-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid rgba(32,199,135,0.28);
      border-radius: 999px;
      background: rgba(32,199,135,0.10);
      color: #a9f5d5;
      padding: 8px 11px;
      font-size: 12px;
      font-weight: 800;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--atlas-green);
      box-shadow: 0 0 0 0 rgba(32,199,135,0.55);
      animation: pulse 1.8s infinite;
    }
    .ai-status-panel {
      margin: 10px 20px 0;
      padding: 10px 14px;
      border: 1px solid rgba(212,175,55,0.22);
      border-radius: 18px;
      background: linear-gradient(135deg, rgba(212,175,55,0.11), rgba(255,255,255,0.045));
      display: grid;
      gap: 8px;
    }
    .ai-status-title {
      color: var(--atlas-gold-light);
      font-weight: 800;
      font-size: 14px;
    }
    .ai-status-list {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      color: var(--atlas-light);
      font-size: 12px;
    }
    .ai-status-list div {
      min-height: 30px;
      display: flex;
      align-items: center;
      gap: 7px;
      border: 1px solid rgba(230,232,235,0.12);
      border-radius: 12px;
      padding: 6px 9px;
      background: rgba(11,19,43,0.28);
    }
    .messages {
      min-height: 0;
      padding: 14px 20px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      overflow: auto;
    }
    .message-row {
      display: grid;
      grid-template-columns: 42px minmax(0, 1fr);
      gap: 11px;
      align-items: end;
      max-width: min(860px, 94%);
      animation: messageIn 220ms ease both;
    }
    .message-row.user-row {
      align-self: flex-end;
      grid-template-columns: minmax(0, 1fr) 42px;
    }
    .message-card {
      display: grid;
      gap: 7px;
    }
    .message {
      padding: 14px 18px;
      border-radius: 24px;
      line-height: 1.55;
      white-space: pre-wrap;
      font-weight: 450;
      box-shadow: 0 18px 38px rgba(0,0,0,0.18);
    }
    .assistant {
      background: rgba(26,35,56,0.94);
      border: 1px solid rgba(212,175,55,0.28);
      border-left: 3px solid var(--atlas-gold);
      color: var(--atlas-light);
      border-top-left-radius: 12px;
    }
    .user {
      background: linear-gradient(135deg, rgba(46,58,79,0.98), rgba(38,50,70,0.96));
      border: 1px solid rgba(230,232,235,0.14);
      color: var(--atlas-white);
      border-top-right-radius: 12px;
    }
    .meta {
      display: flex;
      gap: 8px;
      color: rgba(230,232,235,0.48);
      font-size: 11px;
      font-weight: 700;
    }
    .user-row .meta { justify-content: flex-end; }
    .typing .message {
      min-width: 112px;
      color: rgba(230,232,235,0.70);
    }
    .typing-dots {
      display: inline-flex;
      gap: 4px;
      vertical-align: middle;
    }
    .typing-dots span {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--atlas-gold-light);
      animation: typing 1s infinite ease-in-out;
    }
    .typing-dots span:nth-child(2) { animation-delay: 120ms; }
    .typing-dots span:nth-child(3) { animation-delay: 240ms; }
    .choice-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      max-width: min(820px, 100%);
      margin-left: 53px;
      animation: messageIn 220ms ease both;
    }
    .choice,
    .cta-button,
    .send {
      border: 1px solid rgba(212,175,55,0.24);
      border-radius: 16px;
      background: rgba(255,255,255,0.06);
      color: var(--atlas-white);
      font: inherit;
      font-weight: 800;
      cursor: pointer;
      transition: transform 160ms ease, border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
    }
    .choice {
      min-height: 62px;
      padding: 13px 18px;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: 0;
      color: #111827;
      border-color: rgba(255,236,170,0.72);
      background:
        linear-gradient(180deg, rgba(255,255,255,0.42), rgba(255,255,255,0.02) 28%),
        linear-gradient(135deg, #f9df85 0%, #d4af37 46%, #9d741b 100%);
      box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.58),
        inset 0 -8px 14px rgba(105,72,11,0.26),
        0 12px 0 rgba(94,65,15,0.78),
        0 24px 34px rgba(0,0,0,0.34);
      text-shadow: 0 1px 0 rgba(255,255,255,0.38);
    }
    .choice.wide {
      grid-column: 1 / -1;
      min-height: 60px;
    }
    .choice:hover,
    .cta-button:hover,
    .send:hover {
      transform: translateY(-2px);
      border-color: rgba(212,175,55,0.58);
      box-shadow: 0 14px 30px rgba(212,175,55,0.10);
    }
    .choice:hover {
      border-color: rgba(255,243,190,0.94);
      box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.66),
        inset 0 -8px 14px rgba(105,72,11,0.22),
        0 15px 0 rgba(94,65,15,0.76),
        0 30px 40px rgba(0,0,0,0.38);
    }
    .choice:active {
      transform: translateY(7px);
      box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.42),
        inset 0 -4px 10px rgba(105,72,11,0.30),
        0 5px 0 rgba(94,65,15,0.86),
        0 12px 22px rgba(0,0,0,0.30);
    }
    .composer {
      padding: 16px 20px 18px;
      background: rgba(11,19,43,0.66);
      border-top: 1px solid rgba(230,232,235,0.10);
    }
    .inputbar {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      width: 100%;
      background: rgba(26,35,56,0.96);
      border: 1px solid rgba(230,232,235,0.14);
      border-radius: 18px;
      padding: 8px;
    }
    .inputbar:focus-within {
      border-color: var(--atlas-gold);
      box-shadow: 0 0 0 4px rgba(212,175,55,0.08);
    }
    textarea {
      border: 0;
      resize: none;
      min-height: 48px;
      max-height: 160px;
      padding: 13px 12px;
      background: transparent;
      color: var(--atlas-white);
      font: inherit;
      outline: 0;
    }
    textarea::placeholder { color: rgba(230,232,235,0.55); }
    .send {
      min-width: 54px;
      background: linear-gradient(135deg, var(--atlas-gold), var(--atlas-gold-light));
      color: var(--atlas-navy);
      border-color: transparent;
    }
    .smart-dashboard {
      min-height: calc(100vh - 190px);
      border-radius: 24px;
      padding: 16px;
      overflow: auto;
      display: grid;
      align-content: start;
      gap: 12px;
    }
    .dashboard-tabs {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      position: sticky;
      top: 0;
      z-index: 2;
      padding: 4px;
      border: 1px solid rgba(230,232,235,0.10);
      border-radius: 16px;
      background: rgba(11,19,43,0.88);
      backdrop-filter: blur(16px);
    }
    .dashboard-tab {
      min-height: 38px;
      border: 0;
      border-radius: 12px;
      background: transparent;
      color: rgba(230,232,235,0.68);
      font: inherit;
      font-size: 12px;
      font-weight: 850;
      cursor: pointer;
    }
    .dashboard-tab.active {
      background: rgba(212,175,55,0.16);
      color: var(--atlas-gold-light);
    }
    .dashboard-section {
      display: none;
      gap: 12px;
    }
    .dashboard-section.active {
      display: grid;
    }
    .dashboard-card[data-dashboard-panel] {
      display: none;
    }
    .dashboard-card[data-dashboard-panel].active-panel {
      display: grid;
    }
    .dashboard-card {
      border-radius: 18px;
      padding: 14px;
      display: grid;
      gap: 12px;
    }
    .dashboard-card.compact {
      gap: 10px;
    }
    .dashboard-card.compact .metric {
      grid-template-columns: auto 1fr;
    }
    .crm-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 9px;
    }
    .crm-field {
      min-height: 42px;
      display: grid;
      grid-template-columns: minmax(110px, 0.9fr) minmax(0, 1.1fr);
      align-items: center;
      gap: 10px;
      border: 1px solid rgba(230,232,235,0.09);
      border-radius: 13px;
      background: rgba(11,19,43,0.22);
      padding: 9px 10px;
      color: var(--atlas-light);
      font-size: 12px;
    }
    .crm-field span:first-child {
      color: rgba(230,232,235,0.58);
      font-weight: 700;
    }
    .crm-field strong {
      color: var(--atlas-white);
      text-align: right;
      overflow-wrap: anywhere;
    }
    .dashboard-card h2 {
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      color: var(--atlas-white);
      font-size: 14px;
      font-weight: 850;
    }
    .metric {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 12px;
      align-items: center;
    }
    .score-ring {
      --score: 0%;
      width: 78px;
      height: 78px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      background: conic-gradient(var(--atlas-gold) var(--score), rgba(230,232,235,0.11) 0);
      position: relative;
    }
    .score-ring::after {
      content: "";
      position: absolute;
      inset: 7px;
      border-radius: 50%;
      background: #111b33;
    }
    .score-ring strong {
      position: relative;
      z-index: 1;
      color: var(--atlas-gold-light);
      font-size: 18px;
    }
    .muted {
      margin: 0;
      color: rgba(230,232,235,0.66);
      font-size: 12px;
      line-height: 1.45;
    }
    .next-step {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      border: 1px solid rgba(212,175,55,0.28);
      border-radius: 16px;
      background: rgba(212,175,55,0.10);
      padding: 13px;
      color: var(--atlas-gold-light);
      font-weight: 850;
    }
    .field {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      color: var(--atlas-light);
      font-size: 13px;
    }
    .field span:first-child { color: rgba(230,232,235,0.66); }
    .field strong { color: var(--atlas-white); text-align: right; }
    .cv-map {
      display: grid;
      gap: 10px;
    }
    .cv-map-summary {
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: center;
      gap: 10px;
      color: rgba(230,232,235,0.72);
      font-size: 12px;
      line-height: 1.45;
    }
    .cv-map-summary strong {
      color: var(--atlas-gold-light);
      font-size: 18px;
    }
    .cv-section-list,
    .cv-missing-list {
      display: grid;
      gap: 7px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .cv-section-item,
    .cv-missing-item {
      min-height: 34px;
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      gap: 8px;
      align-items: center;
      border: 1px solid rgba(230,232,235,0.09);
      border-radius: 11px;
      background: rgba(11,19,43,0.22);
      padding: 8px 9px;
      color: var(--atlas-light);
      font-size: 12px;
    }
    .cv-section-item strong {
      display: block;
      color: var(--atlas-white);
      font-size: 12px;
      overflow-wrap: anywhere;
    }
    .cv-section-item span:last-child {
      display: block;
      color: rgba(230,232,235,0.58);
      margin-top: 2px;
    }
    .cv-check {
      width: 18px;
      height: 18px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      background: rgba(32,199,135,0.16);
      color: var(--atlas-green);
      font-size: 11px;
      font-weight: 900;
    }
    .cv-check.pending {
      background: rgba(244,201,93,0.14);
      color: var(--atlas-warning);
    }
    .cv-missing-title {
      margin-top: 2px;
      color: rgba(230,232,235,0.58);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .cv-missing-item {
      color: var(--atlas-gold-light);
      background: rgba(212,175,55,0.08);
      border-color: rgba(212,175,55,0.18);
    }
    .status-icon { color: var(--atlas-gold); }
    .complete-icon { color: var(--atlas-green); }
    .warning-icon { color: var(--atlas-warning); }
    .offer-list { display: grid; gap: 9px; }
    .offer-card {
      border: 1px solid rgba(230,232,235,0.10);
      border-radius: 14px;
      background: rgba(11,19,43,0.28);
      padding: 12px;
      display: grid;
      gap: 5px;
    }
    .offer-card strong { font-size: 13px; }
    .offer-card span { color: rgba(230,232,235,0.68); font-size: 12px; }
    .cta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
    .cta-button {
      min-height: 46px;
      padding: 10px;
      text-align: center;
      font-size: 12px;
    }
    .cta-button.primary {
      background: linear-gradient(135deg, var(--atlas-gold), var(--atlas-gold-light));
      color: var(--atlas-navy);
      border-color: transparent;
    }
    .verification-list { display: grid; gap: 8px; }
    .verification-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      border: 1px solid rgba(230,232,235,0.10);
      border-radius: 12px;
      padding: 10px;
      color: rgba(230,232,235,0.72);
      font-size: 12px;
      font-weight: 750;
    }
    .badge {
      border-radius: 999px;
      padding: 6px 9px;
      font-size: 11px;
      font-weight: 850;
      white-space: nowrap;
    }
    .badge.green { background: rgba(32,199,135,0.12); color: #a9f5d5; }
    .badge.gold { background: rgba(212,175,55,0.13); color: var(--atlas-gold-light); }
    .badge.orange { background: rgba(244,201,93,0.12); color: #ffe19a; }
    .badge.red { background: rgba(239,68,68,0.12); color: #ffb4b4; }
    .microtext {
      color: rgba(230,232,235,0.52);
      font-size: 11px;
      line-height: 1.45;
      padding: 0 3px 2px;
    }
    .history { display: none; }
    @keyframes messageIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes typing {
      0%, 80%, 100% { transform: translateY(0); opacity: 0.45; }
      40% { transform: translateY(-4px); opacity: 1; }
    }
    @keyframes pulse {
      70% { box-shadow: 0 0 0 10px rgba(32,199,135,0); }
      100% { box-shadow: 0 0 0 0 rgba(32,199,135,0); }
    }
    @media (max-width: 1180px) {
      .workspace { grid-template-columns: minmax(0, 60fr) minmax(300px, 40fr); }
      .ai-status-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .choice-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 880px) {
      header { align-items: flex-start; flex-direction: column; }
      nav { width: 100%; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
      .top-status { grid-template-columns: 1fr; }
      .status-chips { justify-content: flex-start; }
      .workspace { grid-template-columns: 1fr; }
      .chat-shell, .smart-dashboard { min-height: auto; }
      .smart-dashboard { order: 2; }
    }
    @media (max-width: 620px) {
      .app { padding: 12px; }
      .messages { padding: 14px; }
      .message-row, .message-row.user-row {
        max-width: 100%;
        grid-template-columns: 34px minmax(0, 1fr);
      }
      .message-row.user-row .user-avatar { grid-column: 1; grid-row: 1; }
      .message-row.user-row .message-card { grid-column: 2; grid-row: 1; }
      .avatar { width: 34px; height: 34px; font-size: 12px; }
      .choice-grid { margin-left: 45px; }
      .ai-status-list, .cta-grid { grid-template-columns: 1fr; }
      .chat-head { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    {{BRAND_LOGO_HTML}}
    <nav aria-label="Main navigation">
      <a href="/ai?intent=job" data-i18n="nav.jobs">Jobs</a>
      <a href="/employer" data-i18n="nav.employers">Employers</a>
      <a class="active" href="/ai" data-i18n="nav.coordinator">Coordinator</a>
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
  <main class="app">
    <section class="top-status">
      <div class="status-copy">
        <div class="eyebrow" data-i18n="smart.platform_label">ATLAS by EWU</div>
        <h1 data-i18n="smart.screen_title">Premium recruitment coordinator</h1>
        <p data-i18n="smart.screen_subtitle">One trusted workspace for your profile, documents, offers and coordinator contact.</p>
      </div>
      <div class="status-chips">
        <span class="chip"><span class="pulse-dot"></span><strong data-i18n="smart.status_active">Active analysis</strong></span>
        <span class="chip" id="top-user-status" data-i18n="smart.user_status_initial">Profile in progress</span>
        <span class="chip"><span data-i18n="smart.session_secure">Secure session</span></span>
      </div>
    </section>

    <section class="workspace">
      <section class="chat-shell" aria-label="Coordinator conversation">
        <div class="chat-head">
          <div class="agent-mini">
            <div class="avatar">A</div>
            <div>
              <h2 data-i18n="coordinator.title">Your personal coordinator</h2>
              <span data-i18n="smart.chat_subtitle">Profile, matching and verification in one conversation</span>
            </div>
          </div>
          <div class="live-pill"><span class="pulse-dot"></span><span data-i18n="smart.live_matching">Live matching</span></div>
        </div>

        <div class="ai-status-panel" id="ai-status">
          <div class="ai-status-title" data-i18n="ai_status.analyzing">Atlas analizuje profil...</div>
          <div class="ai-status-list" id="ai-status-list"></div>
        </div>

        <div class="messages" id="messages"></div>

        <form class="composer" id="chat-form">
          <div class="inputbar">
            <textarea id="message" data-i18n-placeholder="chat.placeholder" placeholder="Tell ATLAS what you need..." autocomplete="off"></textarea>
            <button class="send" type="submit" data-i18n-aria-label="coordinator.send">↑</button>
          </div>
        </form>
      </section>

      <aside class="smart-dashboard" aria-label="Smart Dashboard">
        <div class="dashboard-tabs" role="tablist" aria-label="Workspace sections">
          <button class="dashboard-tab active" type="button" data-dashboard-tab="profile" data-i18n="smart.tab_profile">Profile</button>
          <button class="dashboard-tab" type="button" data-dashboard-tab="offers" data-i18n="smart.tab_offers">Offers</button>
          <button class="dashboard-tab" type="button" data-dashboard-tab="verify" data-i18n="smart.tab_verify">Verify</button>
          <button class="dashboard-tab" type="button" data-dashboard-tab="actions" data-i18n="smart.tab_actions">Actions</button>
        </div>
        <div class="dashboard-card">
          <h2><span data-i18n="crm.card_title">CRM card</span><span class="badge gold" id="user-stage">Start</span></h2>
          <div class="crm-grid">
            <div class="crm-field"><span data-i18n="crm.verification_status">Verification status</span><strong id="crm-verification">-</strong></div>
            <div class="crm-field"><span data-i18n="profile.profession">Profession</span><strong id="dash-profession">-</strong></div>
            <div class="crm-field"><span data-i18n="profile.country">Country</span><strong id="crm-country">-</strong></div>
            <div class="crm-field"><span data-i18n="crm.city">City</span><strong id="crm-city">-</strong></div>
            <div class="crm-field"><span data-i18n="crm.salary">Salary</span><strong id="crm-salary">-</strong></div>
            <div class="crm-field"><span data-i18n="crm.vacancies_count">Vacancies</span><strong id="crm-vacancies">0</strong></div>
            <div class="crm-field"><span data-i18n="crm.housing">Housing</span><strong id="crm-housing">-</strong></div>
            <div class="crm-field"><span data-i18n="profile.documents">Documents</span><strong id="dash-documents">-</strong></div>
            <div class="crm-field"><span data-i18n="crm.ai_match_score">AI Match Score</span><strong id="crm-match-score">0%</strong></div>
            <div class="crm-field"><span data-i18n="crm.found_candidates">Found candidates</span><strong id="crm-found-candidates">0</strong></div>
          </div>
        </div>

        <div class="dashboard-card">
          <h2 data-i18n="smart.next_step">Najbliższy krok</h2>
          <button class="next-step" id="next-step" type="button">Dodaj dokumenty <span>→</span></button>
        </div>

        <div class="dashboard-card">
          <h2 data-i18n="smart.profile_trust">Wiarygodność profilu</h2>
          <div class="metric">
            <div class="score-ring" id="profile-score-ring"><strong id="profile-score">0%</strong></div>
            <p class="muted" id="profile-score-copy" data-i18n="smart.profile_score_hint">Complete your data to increase profile trust.</p>
          </div>
        </div>

        <div class="dashboard-card">
          <h2 data-i18n="dashboard.title.candidateCv">Candidate CV Map</h2>
          <div class="cv-map">
            <div class="cv-map-summary">
              <span id="cv-map-summary" data-i18n="dashboard.empty.candidate">Your candidate CV map will appear here.</span>
              <strong id="cv-map-count">0/8</strong>
            </div>
            <ul class="cv-section-list" id="cv-section-list"></ul>
            <div class="cv-missing-title" data-i18n="profile.what_to_improve">What to improve</div>
            <ul class="cv-missing-list" id="cv-missing-list"></ul>
          </div>
        </div>

        <div class="dashboard-card">
          <h2 data-i18n="smart.employer_trust">Wiarygodność pracodawcy</h2>
          <div class="metric">
            <div class="score-ring" id="employer-score-ring"><strong id="employer-score">0%</strong></div>
            <p class="muted" id="employer-score-copy" data-i18n="smart.employer_review_required">Pracodawca wymaga dodatkowej weryfikacji.</p>
          </div>
          <div class="verification-list">
            <div class="verification-item"><span data-i18n="smart.verified">Zweryfikowany</span><span class="badge green" id="verified-badge">0</span></div>
            <div class="verification-item"><span data-i18n="smart.in_review">W trakcie weryfikacji</span><span class="badge gold">2</span></div>
            <div class="verification-item"><span data-i18n="smart.needs_check">Wymaga sprawdzenia</span><span class="badge orange">1</span></div>
            <div class="verification-item"><span data-i18n="smart.rejected">Odrzucony</span><span class="badge red">0</span></div>
          </div>
        </div>

        <div class="dashboard-card">
          <h2 data-i18n="smart.documents">Dokumenty</h2>
          <p class="muted" id="documents-empty" data-i18n="smart.empty_documents">Dodaj dokumenty, aby zwiększyć wiarygodność profilu.</p>
        </div>

        <div class="dashboard-card">
          <h2 data-i18n="smart.matched_offers">Dopasowane oferty</h2>
          <div class="offer-list" id="offer-list"></div>
          <p class="muted" id="offers-empty" data-i18n="smart.empty_offers">Atlas jeszcze szuka najlepszych ofert dla Ciebie.</p>
        </div>

        <div class="dashboard-card">
          <h2 data-i18n="smart.contact_coordinator">Kontakt z koordynatorem</h2>
          <div class="cta-grid">
            <button class="cta-button primary" type="button" data-workflow="profession" data-i18n="smart.cta_complete_profile">Uzupełnij profil</button>
            <button class="cta-button" type="button" data-workflow="documents" data-i18n="smart.cta_add_documents">Dodaj dokumenty</button>
            <button class="cta-button" type="button" data-workflow="offers" data-i18n="smart.cta_check_offers">Sprawdź oferty</button>
            <button class="cta-button" type="button" data-workflow="consultation" data-i18n="smart.cta_talk">Porozmawiaj z koordynatorem</button>
          </div>
          <div class="microtext" data-i18n="smart.privacy_note">Twoje dane są używane wyłącznie do dopasowania ofert i kontaktu z koordynatorem.</div>
        </div>
      </aside>
    </section>
    <div class="history" id="history" aria-hidden="true"></div>
  </main>

  {{OBSERVABILITY_BODY}}
  <script src="/static/i18n.js?v=20260711-langfix"></script>
  <script>
    const userId = localStorage.getItem("atlas_user_id") || `user-${crypto.randomUUID()}`;
    localStorage.setItem("atlas_user_id", userId);

    const messages = document.getElementById("messages");
    const history = document.getElementById("history");
    const aiStatusList = document.getElementById("ai-status-list");
    const input = document.getElementById("message");
    const chatForm = document.getElementById("chat-form");
    const sendButton = chatForm.querySelector("button[type='submit']");
    let isSending = false;
    const topUserStatus = document.getElementById("top-user-status");
    const crmVerification = document.getElementById("crm-verification");
    const dashProfession = document.getElementById("dash-profession");
    const crmCountry = document.getElementById("crm-country");
    const crmCity = document.getElementById("crm-city");
    const crmSalary = document.getElementById("crm-salary");
    const crmVacancies = document.getElementById("crm-vacancies");
    const crmHousing = document.getElementById("crm-housing");
    const dashDocuments = document.getElementById("dash-documents");
    const crmMatchScore = document.getElementById("crm-match-score");
    const crmFoundCandidates = document.getElementById("crm-found-candidates");
    const userStage = document.getElementById("user-stage");
    const nextStep = document.getElementById("next-step");
    const profileScore = document.getElementById("profile-score");
    const profileScoreRing = document.getElementById("profile-score-ring");
    const profileScoreCopy = document.getElementById("profile-score-copy");
    const cvMapSummary = document.getElementById("cv-map-summary");
    const cvMapCount = document.getElementById("cv-map-count");
    const cvSectionList = document.getElementById("cv-section-list");
    const cvMissingList = document.getElementById("cv-missing-list");
    const employerScore = document.getElementById("employer-score");
    const employerScoreRing = document.getElementById("employer-score-ring");
    const employerScoreCopy = document.getElementById("employer-score-copy");
    const verifiedBadge = document.getElementById("verified-badge");
    const documentsEmpty = document.getElementById("documents-empty");
    const offersEmpty = document.getElementById("offers-empty");
    const offerList = document.getElementById("offer-list");
    const dashboardTabs = Array.from(document.querySelectorAll("[data-dashboard-tab]"));
    const dashboardCards = Array.from(document.querySelectorAll(".smart-dashboard .dashboard-card"));
    const urlIntent = new URLSearchParams(location.search).get("intent");

    let chatBooted = false;
    let currentProfile = {};
    let currentEmployer = {};
    let currentAiStatusKeys = [];

    function tr(key) { return window.AtlasI18n ? window.AtlasI18n.t(key) : key; }
    function nowTime() {
      return new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" }).format(new Date());
    }
    function valueOrDash(value) {
      if (Array.isArray(value)) return value.length ? value.join(", ") : "-";
      return value || "-";
    }
    function hasValue(value) {
      return Array.isArray(value) ? value.length > 0 : Boolean(value);
    }
    function setupDashboardTabs() {
      dashboardCards.forEach(card => {
        if (card.contains(nextStep)) {
          card.style.order = "1";
          return;
        }
        if (card.contains(profileScore)) {
          card.style.order = "2";
          return;
        }
        card.style.order = "3";
        if (card.contains(cvSectionList)) {
          card.dataset.dashboardPanel = "profile";
          card.style.order = "3";
        }
        else if (card.contains(dashProfession)) {
          card.dataset.dashboardPanel = "profile";
          card.style.order = "4";
        }
        else if (card.contains(offerList)) card.dataset.dashboardPanel = "offers";
        else if (card.contains(documentsEmpty) || card.contains(employerScore)) card.dataset.dashboardPanel = "verify";
        else if (card.querySelector("[data-workflow]")) card.dataset.dashboardPanel = "actions";
      });
      setDashboardTab("profile");
      dashboardTabs.forEach(tab => {
        tab.addEventListener("click", () => setDashboardTab(tab.dataset.dashboardTab || "profile"));
      });
    }
    function setDashboardTab(panel) {
      dashboardTabs.forEach(tab => {
        const isActive = tab.dataset.dashboardTab === panel;
        tab.classList.toggle("active", isActive);
        tab.setAttribute("aria-selected", String(isActive));
      });
      dashboardCards.forEach(card => {
        if (!card.dataset.dashboardPanel) return;
        card.classList.toggle("active-panel", card.dataset.dashboardPanel === panel);
      });
    }
    function buildClientCvMap(profile = {}) {
      const sections = [
        ["profession", "profile.profession", profile.profession, 18],
        ["experience", "profile.experience", profile.experience_years ? `${profile.experience_years} years` : "", 16],
        ["country", "profile.country", profile.country, 14],
        ["documents", "profile.documents", profile.documents, 16],
        ["languages", "profile.languages", profile.languages, 12],
        ["ready", "profile.ready", profile.ready_from || profile.ready_to_work, 10],
        ["salary", "crm.salary", profile.desired_salary, 8],
        ["phone", "form.phone", profile.phone || profile.phone_number || profile.contact, 6]
      ].map(([field, label_key, value, weight]) => {
        const complete = hasValue(value);
        return { field, label_key, value: complete ? value : null, complete, weight };
      });
      const completed = sections.filter(section => section.complete);
      return {
        score: completed.reduce((total, section) => total + section.weight, 0),
        completed_count: completed.length,
        total_count: sections.length,
        sections,
        missing: sections.filter(section => !section.complete).slice(0, 4),
        status_key: completed.length >= 6 ? "profile.ready_for_matching" : "smart.profile_score_hint"
      };
    }
    function renderCvMap(profile = {}) {
      const map = profile.cv_map || buildClientCvMap(profile);
      const sections = map.sections || [];
      const missing = map.missing || sections.filter(section => !section.complete).slice(0, 4);
      cvMapCount.textContent = `${map.completed_count || 0}/${map.total_count || sections.length || 8}`;
      cvMapSummary.textContent = tr(map.status_key || "dashboard.empty.candidate");
      cvSectionList.innerHTML = sections.map(section => {
        const value = valueOrDash(section.value);
        const mark = section.complete ? "\\u2713" : "\\u2022";
        const pending = section.complete ? "" : " pending";
        return `
          <li class="cv-section-item">
            <span class="cv-check${pending}">${mark}</span>
            <span><strong>${tr(section.label_key)}</strong><span>${value}</span></span>
          </li>
        `;
      }).join("");
      cvMissingList.innerHTML = missing.length ? missing.map(section => (
        `<li class="cv-missing-item"><span class="cv-check pending">!</span><span>${tr(section.label_key)}</span></li>`
      )).join("") : `<li class="cv-missing-item"><span class="cv-check">\\u2713</span><span>${tr("profile.ready_for_matching")}</span></li>`;
    }
    function translatedValue(value) {
      return typeof value === "string" && value.includes(".") ? tr(value) : value;
    }
    function addMessage(role, text, options = {}) {
      const row = document.createElement("div");
      row.className = `message-row ${role}-row${options.typing ? " typing" : ""}`;
      row.dataset.role = role;
      const avatar = document.createElement("div");
      avatar.className = role === "user" ? "avatar user-avatar" : "avatar";
      avatar.textContent = role === "user" ? "U" : "A";
      const card = document.createElement("div");
      card.className = "message-card";
      const bubble = document.createElement("div");
      bubble.className = `message ${role}`;
      if (options.typing) {
        bubble.innerHTML = `${tr("coordinator.typing")} <span class="typing-dots"><span></span><span></span><span></span></span>`;
      } else {
        bubble.textContent = text;
      }
      const meta = document.createElement("div");
      meta.className = "meta";
      meta.innerHTML = `<span>${role === "user" ? tr("smart.you") : "ATLAS"}</span><span>${nowTime()}</span>`;
      card.appendChild(bubble);
      card.appendChild(meta);
      if (role === "user") {
        row.appendChild(card);
        row.appendChild(avatar);
      } else {
        row.appendChild(avatar);
        row.appendChild(card);
      }
      messages.appendChild(row);
      if (options.scroll !== false) {
        messages.scrollTop = messages.scrollHeight;
      }
      return bubble;
    }
    function addChoices() {
      const grid = document.createElement("div");
      grid.className = "choice-grid";
      [
        ["coordinator.choice_job", "actions.find_job"],
        ["coordinator.choice_employees", "actions.hire_employees"],
        ["coordinator.choice_consultation", "actions.talk_to_coordinator"]
      ].forEach(([labelKey, textKey], index) => {
        const button = document.createElement("button");
        button.className = index === 2 ? "choice wide" : "choice";
        button.type = "button";
        button.dataset.labelKey = labelKey;
        button.dataset.messageKey = textKey;
        button.textContent = tr(labelKey);
        button.addEventListener("click", () => sendMessage(tr(textKey)));
        grid.appendChild(button);
      });
      messages.appendChild(grid);
    }
    function refreshChatTranslations() {
      messages.querySelectorAll("[data-i18n-message]").forEach(element => {
        element.textContent = tr(element.dataset.i18nMessage);
      });
      messages.querySelectorAll("[data-label-key]").forEach(button => {
        button.textContent = tr(button.dataset.labelKey);
      });
    }
    function addHistory(text) {
      const button = document.createElement("button");
      button.textContent = text.length > 38 ? `${text.slice(0, 38)}...` : text;
      history.prepend(button);
    }
    function renderAiStatus(keys = currentAiStatusKeys) {
      currentAiStatusKeys = keys;
      const fallback = ["ai_status.analyzing", "ai_status.checking_documents", "ai_status.comparing_offers", "ai_status.best_matches_found"];
      const source = keys.length ? keys : fallback;
      aiStatusList.innerHTML = source.map((key, index) => {
        const cls = keys.length && index < keys.length ? "complete-icon" : index === 0 ? "status-icon" : "warning-icon";
        const symbol = keys.length && index < keys.length ? "\\u2713" : index === 0 ? "\\u25cf" : "\\u25cb";
        return `<div><span class="${cls}">${symbol}</span> ${tr(key)}</div>`;
      }).join("");
    }
    function calculateProfileTrust(profile) {
      let score = 0;
      if (profile.full_name || profile.name || (profile.first_name && profile.last_name)) score += 20;
      if (profile.phone || profile.phone_number) score += 20;
      if (profile.profession) score += 20;
      if (hasValue(profile.documents)) score += 20;
      if (profile.ready_from || profile.ready_to_work) score += 20;
      return score;
    }
    function calculateEmployerTrust(source = {}) {
      const employer = source.employer || source.company || source;
      let score = 0;
      if (employer.nip || employer.regon || employer.vat_id || employer.company_registration) score += 20;
      if (employer.address || employer.company_address) score += 20;
      if (employer.contact || employer.phone || employer.email) score += 20;
      if (employer.work_conditions || employer.salary || employer.housing || employer.contract_type) score += 20;
      if (employer.offer_history || employer.completed_recruitments || employer.history) score += 20;
      return score;
    }
    function getNextStep(profile, offersAvailable) {
      if (!hasValue(profile.documents)) return ["smart.next_add_documents", "documents"];
      if (!profile.phone && !profile.phone_number) return ["smart.next_add_phone", "phone"];
      if (offersAvailable) return ["smart.next_confirm_interest", "offers"];
      return ["smart.next_wait_matching", "offers"];
    }
    function yesNo(value) {
      if (value === true) return tr("common.yes");
      if (value === false) return tr("common.no");
      return "-";
    }
    function verificationLabel(status, fallbackTrusted) {
      const map = {
        trusted: "smart.verified",
        under_review: "smart.in_review",
        high_risk: "smart.needs_check",
        critical_risk: "smart.rejected"
      };
      return tr(map[status] || (fallbackTrusted ? "smart.verified" : "smart.in_review"));
    }
    function crmSource(profile, employerExperience) {
      const experience = employerExperience || profile.employer_experience || {};
      const vacancy = experience.vacancy_card || profile.vacancy || {};
      const dashboard = experience.dashboard || {};
      const quality = experience.vacancy_quality || {};
      const trust = experience.trust_score || {};
      return { experience, vacancy, dashboard, quality, trust };
    }
    function renderOffers(showOffers = true) {
      const offers = [
        ["Spawacz MIG/MAG", "Niemcy", "od 15 \\u20ac/h"],
        ["Monter konstrukcji", "Polska", "od 32 z\\u0142/h"],
        ["Pracownik produkcji", "Czechy", "od 28 z\\u0142/h"]
      ];
      offerList.innerHTML = showOffers ? offers.map(([title, country, salary]) => (
        `<div class="offer-card"><strong>${title}</strong><span>${country} - ${salary}</span></div>`
      )).join("") : "";
      offersEmpty.style.display = showOffers ? "none" : "block";
    }
    function renderSmartDashboard(profile = currentProfile, employer = currentEmployer) {
      currentProfile = profile || {};
      currentEmployer = employer || {};
      const { vacancy, dashboard, quality, trust } = crmSource(currentProfile, currentEmployer);
      const offersAvailable = Boolean(currentProfile.profession || currentProfile.ready_from || currentProfile.ready_to_work);
      const profileTrust = currentProfile.cv_map?.score || calculateProfileTrust(currentProfile);
      const employerTrust = calculateEmployerTrust(currentEmployer);
      const [nextKey, workflow] = getNextStep(currentProfile, offersAvailable);
      const housingValue = vacancy.housing === undefined || vacancy.housing === null ? currentProfile.housing : vacancy.housing;

      const matchScore = quality.score || currentProfile.employment_probability?.score || 0;
      crmVerification.textContent = verificationLabel(trust.status, employerTrust >= 80);
      dashProfession.textContent = valueOrDash(vacancy.profession || currentProfile.profession);
      crmCountry.textContent = valueOrDash(vacancy.country || currentProfile.country);
      crmCity.textContent = valueOrDash(vacancy.city || vacancy.location || currentProfile.city);
      crmSalary.textContent = valueOrDash(vacancy.salary || currentProfile.desired_salary);
      crmVacancies.textContent = valueOrDash(vacancy.quantity || dashboard.active_vacancies || 0);
      crmHousing.textContent = yesNo(housingValue);
      dashDocuments.textContent = valueOrDash(currentProfile.documents || vacancy.required_documents);
      crmMatchScore.textContent = `${matchScore}%`;
      crmFoundCandidates.textContent = valueOrDash(dashboard.candidates_in_progress || vacancy.found || (matchScore >= 50 ? 3 : 0));
      documentsEmpty.style.display = hasValue(currentProfile.documents) ? "none" : "block";
      profileScore.textContent = `${profileTrust}%`;
      profileScoreRing.style.setProperty("--score", `${profileTrust}%`);
      profileScoreCopy.textContent = profileTrust >= 80 ? tr("smart.profile_score_strong") : tr("smart.profile_score_hint");
      renderCvMap(currentProfile);
      employerScore.textContent = `${employerTrust}%`;
      employerScoreRing.style.setProperty("--score", `${employerTrust}%`);
      employerScoreCopy.textContent = employerTrust >= 80 ? tr("smart.employer_verified") : tr("smart.employer_review_required");
      verifiedBadge.textContent = employerTrust >= 80 ? "1" : "0";
      nextStep.innerHTML = `${tr(nextKey)} <span>\\u2192</span>`;
      nextStep.dataset.workflow = workflow;
      topUserStatus.textContent = profileTrust >= 80 ? tr("smart.user_status_ready") : tr("smart.user_status_initial");
      userStage.textContent = profileTrust >= 80 ? tr("smart.ready") : tr("smart.in_progress");
      userStage.className = profileTrust >= 80 ? "badge green" : "badge gold";
      renderOffers(offersAvailable);
    }
    function startWorkflow(workflow) {
      const promptKeys = {
        documents: "profile.workflow_documents_prompt",
        ready: "profile.workflow_ready_prompt",
        country: "profile.workflow_country_prompt",
        profession: "profile.workflow_profession_prompt",
        phone: "smart.workflow_phone_prompt",
        offers: "smart.workflow_offers_prompt",
        consultation: "coordinator.consultation_start"
      };
      addMessage("assistant", tr(promptKeys[workflow] || "coordinator.placeholder"));
      input.focus();
    }
    async function sendMessage(text) {
      if (isSending) return;
      isSending = true;
      sendButton.disabled = true;
      const detectedConversationLanguage = window.AtlasI18n?.detectConversationLanguageFromText(text);
      if (detectedConversationLanguage && detectedConversationLanguage !== "unknown") {
        window.AtlasI18n?.setConversationLanguage(detectedConversationLanguage);
      }
      addMessage("user", text);
      addHistory(text);
      input.value = "";
      const typingBubble = addMessage("assistant", "", { typing: true });
      renderAiStatus(["ai_status.analyzing", "ai_status.checking_documents"]);
      try {
        const res = await fetch("/api/ai/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: userId,
            agent_type: urlIntent === "employees" ? "employer" : "candidate",
            message: text,
            browser_language: navigator.language,
            saved_language: localStorage.getItem("atlas_language"),
            ui_language: window.AtlasI18n?.state?.uiLanguage || localStorage.getItem("atlas_language"),
            conversation_language: window.AtlasI18n?.state?.conversationLanguage || detectedConversationLanguage
          })
        });
        const data = await res.json();
        typingBubble.closest(".typing")?.classList.remove("typing");
        typingBubble.textContent = data.reply || tr("coordinator.welcome");
        const employerExperience = data.employer_experience || {};
        currentEmployer = employerExperience || currentEmployer;
        renderSmartDashboard(data.profile || {}, currentEmployer);
        renderAiStatus(["ai_status.analyzing", "ai_status.checking_documents", "ai_status.comparing_offers", "ai_status.best_matches_found"]);
      } catch (error) {
        typingBubble.closest(".typing")?.classList.remove("typing");
        typingBubble.textContent = tr("coordinator.welcome");
        renderAiStatus([]);
      } finally {
        isSending = false;
        sendButton.disabled = false;
      }
    }
    chatForm.addEventListener("submit", async event => {
      event.preventDefault();
      const text = input.value.trim();
      if (text) await sendMessage(text);
    });
    document.querySelectorAll("[data-workflow]").forEach(button => {
      button.addEventListener("click", () => startWorkflow(button.dataset.workflow));
    });
    nextStep.addEventListener("click", () => startWorkflow(nextStep.dataset.workflow || "documents"));
    setupDashboardTabs();
    function bootChat() {
      if (chatBooted) {
        renderSmartDashboard(currentProfile, currentEmployer);
        renderAiStatus();
        return;
      }
      chatBooted = true;
      messages.innerHTML = "";
      const openingKey = urlIntent === "employees" ? "chat.opening.employer" : urlIntent === "job" ? "chat.opening.candidate" : "chat.opening.general";
      const welcomeBubble = addMessage("assistant", tr(openingKey), { scroll: false });
      welcomeBubble.dataset.i18nMessage = openingKey;
      addChoices();
      messages.scrollTop = 0;
      const revealChoices = () => {
        const choiceGrid = document.querySelector(".choice-grid");
        if (!choiceGrid) return;
        const targetTop = choiceGrid.getBoundingClientRect().top + window.scrollY - Math.round(window.innerHeight * 0.48);
        window.scrollTo({ top: Math.max(0, targetTop), left: 0, behavior: "auto" });
      };
      requestAnimationFrame(revealChoices);
      setTimeout(revealChoices, 120);
      renderSmartDashboard({}, {});
      renderAiStatus([]);
    }
    document.addEventListener("atlas:i18n", () => {
      if (!chatBooted) bootChat();
      refreshChatTranslations();
      renderSmartDashboard(currentProfile, currentEmployer);
      renderAiStatus();
    });
    window.AtlasI18n.init().then(() => {
      if (!chatBooted) bootChat();
    });
  </script>
</body>
</html>
""".replace("{{BRAND_LOGO_CSS}}", BRAND_LOGO_CSS).replace("{{BRAND_LOGO_HTML}}", BRAND_LOGO_HTML).replace("{{OBSERVABILITY_HEAD}}", observability_head_html()).replace("{{OBSERVABILITY_BODY}}", observability_body_html("ai_chat"))
