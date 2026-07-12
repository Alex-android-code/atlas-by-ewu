"""Landing page HTML."""

from api.components.brand_logo import BRAND_LOGO_CSS, BRAND_LOGO_HTML
from api.observability import observability_body_html, observability_head_html


LANDING_HTML = f"""
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="atlas-title-key" content="app.title" />
  <title>ATLAS by EWU</title>
  <link rel="icon" href="/static/assets/atlas_brand_icon.png" type="image/png" />
  {observability_head_html()}
  <style>
    :root {{
      --ink: #f7f8fb;
      --muted: rgba(247,248,251,0.68);
      --line: rgba(247,248,251,0.12);
      --panel: rgba(17, 24, 39, 0.72);
      --panel-strong: rgba(15, 23, 42, 0.88);
      --atlas-navy: #0B132B;
      --atlas-dark: #111827;
      --atlas-slate: #273347;
      --atlas-gold: #D4AF37;
      --atlas-gold-light: #F5D98A;
      --atlas-cyan: #7dd3fc;
      --atlas-green: #20c787;
      --atlas-plum: #8b5cf6;
      --atlas-white: #ffffff;
      --atlas-light: #E6E8EB;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, Poppins, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(120deg, rgba(125,211,252,0.10), transparent 32%),
        linear-gradient(240deg, rgba(139,92,246,0.12), transparent 30%),
        linear-gradient(180deg, #090d18 0%, #101827 48%, #eef1f6 48%, #f8fafc 100%);
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
      background-size: 64px 64px;
      mask-image: linear-gradient(180deg, black, transparent 58%);
    }}
    {BRAND_LOGO_CSS}
    .brand-logo-image {{ width: 267px; }}
    .shell {{ position: relative; z-index: 1; }}
    header {{
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      min-height: 116px;
      padding: 10px clamp(18px, 4vw, 52px);
      border-bottom: 1px solid rgba(255,255,255,0.10);
      background: rgba(9,13,24,0.76);
      backdrop-filter: blur(22px);
    }}
    nav {{
      display: flex;
      align-items: center;
      gap: 18px;
      color: rgba(247,248,251,0.76);
      font-size: 14px;
      font-weight: 650;
    }}
    nav a {{ color: inherit; text-decoration: none; }}
    nav a:hover, nav a.active {{ color: var(--atlas-gold-light); }}
    .nav-primary {{
      min-height: 38px;
      display: inline-flex;
      align-items: center;
      border: 1px solid rgba(212,175,55,0.42);
      border-radius: 999px;
      padding: 0 14px;
      color: var(--atlas-gold-light);
      background: rgba(212,175,55,0.08);
    }}
    .language-selector {{ position: relative; }}
    .language-button {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 0;
      background: transparent;
      color: inherit;
      font: inherit;
      cursor: pointer;
      padding: 0;
    }}
    .language-current {{ color: var(--atlas-gold-light); font-size: 12px; font-weight: 850; text-transform: uppercase; }}
    .language-menu {{
      position: absolute;
      top: 30px;
      right: 0;
      z-index: 30;
      min-width: 220px;
      display: none;
      padding: 8px;
      border: 1px solid rgba(212,175,55,0.28);
      border-radius: 14px;
      background: rgba(9,13,24,0.98);
      box-shadow: 0 18px 42px rgba(0,0,0,0.34);
    }}
    .language-menu.open {{ display: grid; gap: 4px; }}
    .language-option {{
      min-height: 40px;
      border: 0;
      border-radius: 10px;
      background: transparent;
      color: var(--atlas-light);
      font: inherit;
      text-align: left;
      cursor: pointer;
      padding: 0 10px;
    }}
    .language-option:hover, .language-option.active {{ background: rgba(212,175,55,0.13); color: #fff; }}
    .menu-toggle {{
      display: none;
      width: 42px;
      height: 42px;
      place-items: center;
      border: 1px solid rgba(212,175,55,0.42);
      border-radius: 12px;
      background: rgba(255,255,255,0.05);
      color: var(--atlas-gold-light);
      font-size: 22px;
      cursor: pointer;
    }}
    main {{ overflow: hidden; }}
    section {{ padding: 72px clamp(18px, 4vw, 56px); }}
    .hero {{
      position: relative;
      min-height: calc(100vh - 116px);
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(360px, 0.78fr);
      gap: clamp(28px, 5vw, 72px);
      align-items: center;
      padding-top: 46px;
      isolation: isolate;
    }}
    .hero::before {{
      content: "";
      position: absolute;
      inset: -12% -8% auto -8%;
      height: 44%;
      pointer-events: none;
      background:
        radial-gradient(circle at 22% 18%, rgba(245,217,138,0.18), transparent 30%),
        radial-gradient(circle at 80% 8%, rgba(125,211,252,0.10), transparent 28%);
      filter: blur(2px);
      z-index: -1;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(115deg, transparent 0 28%, rgba(245,217,138,0.08) 28.2%, transparent 28.6%),
        linear-gradient(145deg, transparent 0 58%, rgba(125,211,252,0.06) 58.2%, transparent 58.7%),
        radial-gradient(circle at 17% 34%, rgba(245,217,138,0.24) 0 1px, transparent 2px),
        radial-gradient(circle at 88% 22%, rgba(245,217,138,0.18) 0 1px, transparent 2px);
      opacity: 0.7;
      z-index: -1;
    }}
    .hero-copy {{ display: grid; gap: 24px; max-width: 760px; }}
    .eyebrow {{
      width: fit-content;
      display: inline-flex;
      align-items: center;
      gap: 9px;
      min-height: 34px;
      border: 1px solid rgba(125,211,252,0.26);
      border-radius: 999px;
      padding: 0 12px;
      color: #c7f0ff;
      background: rgba(125,211,252,0.08);
      font-size: 12px;
      font-weight: 850;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .eyebrow::before {{
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--atlas-green);
      box-shadow: 0 0 18px rgba(32,199,135,0.72);
      animation: statusPulse 2.3s ease-in-out infinite;
    }}
    h1 {{
      margin: 0;
      max-width: 820px;
      font-size: clamp(54px, 8vw, 112px);
      line-height: 0.9;
      letter-spacing: 0;
      font-weight: 900;
    }}
    .hero-copy p {{
      margin: 0;
      max-width: 620px;
      color: var(--muted);
      font-size: clamp(20px, 2.1vw, 28px);
      line-height: 1.42;
    }}
    .hero-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }}
    .button {{
      min-height: 52px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 14px;
      padding: 0 18px;
      color: var(--ink);
      background: rgba(255,255,255,0.06);
      text-decoration: none;
      font-weight: 850;
      transition: transform 180ms ease, border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
    }}
    .button.primary {{
      border-color: transparent;
      color: #111827;
      background: linear-gradient(135deg, #f8e7a6, var(--atlas-gold) 46%, #a97818);
      box-shadow: 0 18px 46px rgba(212,175,55,0.26);
    }}
    .button:hover {{ transform: translateY(-2px); border-color: rgba(245,217,138,0.7); }}
    .button:active {{ transform: translateY(1px) scale(0.985); }}
    .button .play-icon {{
      width: 22px;
      height: 22px;
      display: inline-grid;
      place-items: center;
      border: 1px solid rgba(245,217,138,0.34);
      border-radius: 999px;
      color: var(--atlas-gold-light);
      font-size: 11px;
      line-height: 1;
    }}
    .hero-visual {{
      display: grid;
      gap: 18px;
      align-content: center;
    }}
    .atlas-for-you {{
      display: grid;
      gap: 8px;
      color: rgba(247,248,251,0.74);
      font-size: 14px;
      line-height: 1.45;
    }}
    .atlas-for-you strong {{
      color: var(--atlas-gold-light);
      font-size: 18px;
      letter-spacing: 0;
    }}
    .brand-stage {{
      position: relative;
      min-height: 360px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 28px;
      background:
        linear-gradient(145deg, rgba(255,255,255,0.11), rgba(255,255,255,0.04)),
        radial-gradient(circle at 50% 38%, rgba(212,175,55,0.18), transparent 38%);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.12), 0 28px 72px rgba(0,0,0,0.30);
      overflow: hidden;
    }}
    .brand-stage::before {{
      content: "";
      position: absolute;
      width: 92%;
      height: 92%;
      border: 1px solid rgba(125,211,252,0.20);
      border-radius: 50%;
      transform: rotate(-18deg) scaleY(0.42);
      animation: orbit 9s linear infinite;
    }}
    .hero-logo {{
      position: relative;
      width: min(390px, 86%);
      height: auto;
      filter: drop-shadow(0 28px 36px rgba(0,0,0,0.32));
    }}
    .analysis-panel {{
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 22px;
      background: rgba(13,20,34,0.80);
      box-shadow: 0 18px 52px rgba(0,0,0,0.24);
      padding: 18px;
    }}
    .ai-coordinator-card {{
      position: relative;
      overflow: hidden;
      border-color: rgba(245,217,138,0.20);
      background:
        linear-gradient(145deg, rgba(255,255,255,0.09), rgba(255,255,255,0.035)),
        radial-gradient(circle at 24% 0%, rgba(245,217,138,0.14), transparent 42%),
        rgba(8,14,28,0.86);
    }}
    .ai-coordinator-card::before {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: linear-gradient(90deg, transparent, rgba(245,217,138,0.08), transparent);
      transform: translateX(-100%);
      animation: softSweep 4.8s ease-in-out infinite;
    }}
    .analysis-title {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
      color: var(--atlas-gold-light);
      font-size: 13px;
      font-weight: 850;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .analysis-list {{ display: grid; gap: 8px; }}
    .analysis-step {{
      min-height: 38px;
      display: flex;
      align-items: center;
      gap: 10px;
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 12px;
      padding: 0 12px;
      color: rgba(247,248,251,0.66);
      background: rgba(255,255,255,0.035);
      transition: color 250ms ease, border-color 250ms ease, background 250ms ease;
    }}
    .analysis-step::before {{
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: rgba(247,248,251,0.22);
    }}
    .analysis-step.active {{
      color: #fff;
      border-color: rgba(32,199,135,0.38);
      background: rgba(32,199,135,0.08);
    }}
    .analysis-step.active::before {{
      background: var(--atlas-green);
      box-shadow: 0 0 18px rgba(32,199,135,0.75);
    }}
    .analysis-subtitle {{
      margin: -4px 0 14px;
      color: rgba(247,248,251,0.68);
      font-size: 14px;
      line-height: 1.45;
    }}
    .profile-progress {{
      display: grid;
      gap: 9px;
      margin-top: 14px;
    }}
    .profile-progress-label {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      color: rgba(247,248,251,0.76);
      font-size: 13px;
      font-weight: 750;
    }}
    .profile-progress-label strong {{ color: var(--atlas-gold-light); }}
    .progress-track {{
      height: 9px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255,255,255,0.10);
      box-shadow: inset 0 1px 2px rgba(0,0,0,0.26);
    }}
    .progress-fill {{
      width: 78%;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #20c787, #f5d98a 72%, #d4af37);
      box-shadow: 0 0 18px rgba(212,175,55,0.38);
      animation: progressGlow 2.8s ease-in-out infinite;
    }}
    .profile-preview-card {{
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 22px;
      padding: 16px;
      background:
        linear-gradient(145deg, rgba(255,255,255,0.09), rgba(255,255,255,0.035)),
        rgba(8,14,28,0.78);
      box-shadow: 0 18px 52px rgba(0,0,0,0.22);
    }}
    .candidate-head {{
      display: grid;
      grid-template-columns: 58px minmax(0, 1fr);
      gap: 13px;
      align-items: center;
      margin-bottom: 14px;
    }}
    .candidate-photo {{
      width: 58px;
      height: 58px;
      display: grid;
      place-items: center;
      border-radius: 18px;
      color: #071126;
      font-weight: 900;
      background:
        linear-gradient(145deg, rgba(255,255,255,0.75), rgba(255,255,255,0.08) 38%),
        linear-gradient(135deg, #f8e7a6, #d4af37 58%, #9b711b);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.62), 0 12px 28px rgba(212,175,55,0.20);
    }}
    .candidate-name {{
      display: block;
      color: #fff;
      font-size: 18px;
      font-weight: 900;
      line-height: 1.1;
    }}
    .candidate-role, .candidate-meta {{
      display: block;
      margin-top: 4px;
      color: rgba(247,248,251,0.68);
      font-size: 13px;
      line-height: 1.35;
    }}
    .candidate-statuses {{
      display: grid;
      gap: 8px;
    }}
    .candidate-status {{
      min-height: 34px;
      display: flex;
      align-items: center;
      gap: 9px;
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 12px;
      padding: 0 10px;
      color: rgba(247,248,251,0.78);
      background: rgba(255,255,255,0.035);
      font-size: 13px;
      font-weight: 720;
    }}
    .candidate-status::before {{
      content: "✓";
      width: 18px;
      height: 18px;
      display: inline-grid;
      place-items: center;
      border-radius: 50%;
      color: #071126;
      background: var(--atlas-gold-light);
      font-size: 12px;
      font-weight: 900;
      flex: 0 0 auto;
    }}
    .light-section {{
      color: #111827;
      background: #f8fafc;
    }}
    .section-head {{
      max-width: 780px;
      display: grid;
      gap: 10px;
      margin-bottom: 28px;
    }}
    .section-head h2 {{
      margin: 0;
      color: inherit;
      font-size: clamp(32px, 5vw, 58px);
      line-height: 1;
      letter-spacing: 0;
    }}
    .section-head p {{
      margin: 0;
      color: rgba(17,24,39,0.62);
      font-size: 17px;
      line-height: 1.55;
    }}
    .map-layout {{
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(300px, 0.85fr);
      gap: 24px;
      align-items: stretch;
    }}
    .map-card, .country-panel, .ai-block {{
      border: 1px solid rgba(15,23,42,0.10);
      border-radius: 24px;
      background: #fff;
      box-shadow: 0 18px 60px rgba(15,23,42,0.08);
    }}
    .map-card {{ min-height: 480px; padding: 22px; position: relative; overflow: hidden; }}
    .europe-map {{ width: 100%; height: 100%; min-height: 430px; display: block; }}
    .map-country {{
      fill: #e7ebf2;
      stroke: #cbd5e1;
      stroke-width: 2;
      transition: fill 180ms ease, transform 180ms ease, filter 180ms ease;
      transform-box: fill-box;
      transform-origin: center;
    }}
    .map-country.active {{ fill: #f2d673; stroke: #b8891d; filter: drop-shadow(0 8px 14px rgba(212,175,55,0.28)); }}
    .map-country:hover {{ transform: translateY(-3px); }}
    .map-region {{
      fill: #edf2f7;
      stroke: #d5deea;
      stroke-width: 1.3;
    }}
    .map-graticule {{
      fill: none;
      stroke: rgba(148,163,184,0.18);
      stroke-width: 1;
    }}
    .map-coast {{
      fill: none;
      stroke: rgba(100,116,139,0.36);
      stroke-width: 1.2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    .map-border {{
      fill: none;
      stroke: rgba(148,163,184,0.55);
      stroke-width: 1;
      stroke-dasharray: 4 5;
    }}
    .map-route {{
      fill: none;
      stroke: #d4af37;
      stroke-width: 2;
      stroke-dasharray: 8 10;
      opacity: 0.55;
    }}
    .map-city {{
      display: none;
      fill: #f8fafc;
      stroke: #d4af37;
      stroke-width: 2;
      filter: drop-shadow(0 2px 6px rgba(212,175,55,0.32));
    }}
    .map-label {{
      fill: #334155;
      stroke: rgba(248,250,252,0.72);
      stroke-width: 3px;
      paint-order: stroke;
      font-size: 15px;
      font-weight: 850;
      text-anchor: middle;
      dominant-baseline: central;
      pointer-events: none;
    }}
    .country-panel {{ padding: 22px; display: grid; align-content: start; gap: 14px; }}
    .country-list {{ display: grid; gap: 10px; }}
    .country-item {{
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 12px;
      align-items: center;
      border: 1px solid rgba(15,23,42,0.08);
      border-radius: 14px;
      padding: 12px;
      background: #f8fafc;
    }}
    .country-dot {{ width: 10px; height: 10px; border-radius: 50%; background: var(--atlas-gold); }}
    .country-item strong {{ color: #111827; }}
    .country-item span {{ color: #64748b; font-size: 13px; }}
    .neutral-note {{
      border: 1px dashed rgba(15,23,42,0.18);
      border-radius: 14px;
      padding: 12px;
      color: #64748b;
      background: #f8fafc;
      font-size: 14px;
      line-height: 1.45;
    }}
    .steps-grid, .trust-grid, .support-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }}
    .trust-grid {{ grid-template-columns: repeat(5, minmax(0, 1fr)); }}
    .support-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .step-card, .trust-card, .support-card {{
      border: 1px solid rgba(15,23,42,0.10);
      border-radius: 20px;
      background: #fff;
      padding: 18px;
      box-shadow: 0 14px 36px rgba(15,23,42,0.06);
      transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }}
    .step-card:hover, .trust-card:hover, .support-card:hover {{
      transform: translateY(-4px);
      border-color: rgba(212,175,55,0.42);
      box-shadow: 0 20px 54px rgba(15,23,42,0.10);
    }}
    .step-icon, .trust-icon, .support-icon {{
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      border-radius: 13px;
      margin-bottom: 16px;
      color: #111827;
      background: linear-gradient(135deg, #f8e7a6, #d4af37);
      font-weight: 900;
    }}
    .support-card {{
      min-height: 190px;
      display: grid;
      align-content: start;
    }}
    .support-card ul {{
      display: grid;
      gap: 7px;
      margin: 14px 0 0;
      padding: 0;
      list-style: none;
    }}
    .support-card li {{
      display: flex;
      gap: 8px;
      color: #475569;
      font-size: 13px;
      line-height: 1.35;
    }}
    .support-card li::before {{
      content: "";
      width: 6px;
      height: 6px;
      margin-top: 6px;
      flex: 0 0 auto;
      border-radius: 999px;
      background: var(--atlas-gold);
      box-shadow: 0 0 12px rgba(212,175,55,0.34);
    }}
    .step-card h3, .trust-card h3, .support-card h3 {{ margin: 0 0 8px; color: #111827; font-size: 17px; }}
    .step-card p, .trust-card p, .support-card p {{ margin: 0; color: #64748b; font-size: 14px; line-height: 1.45; }}
    .ai-section {{
      color: var(--ink);
      background:
        linear-gradient(120deg, rgba(125,211,252,0.12), transparent 34%),
        linear-gradient(250deg, rgba(212,175,55,0.14), transparent 34%),
        #0b1020;
    }}
    .ai-block {{
      display: grid;
      grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
      gap: 28px;
      padding: clamp(22px, 4vw, 42px);
      color: var(--ink);
      background: rgba(255,255,255,0.06);
      border-color: rgba(255,255,255,0.12);
      box-shadow: 0 26px 72px rgba(0,0,0,0.22);
    }}
    .ai-block h2 {{ margin: 0 0 14px; font-size: clamp(34px, 5vw, 62px); line-height: 1; }}
    .ai-block p {{ margin: 0; color: var(--muted); line-height: 1.6; font-size: 17px; }}
    .ai-capabilities {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .ai-capability {{
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 16px;
      padding: 14px;
      background: rgba(255,255,255,0.055);
    }}
    .ai-capability strong {{ display: block; margin-bottom: 6px; color: #fff; }}
    .ai-capability span {{ color: var(--muted); font-size: 14px; line-height: 1.45; }}
    footer {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      padding: 26px clamp(18px, 4vw, 56px);
      color: rgba(247,248,251,0.62);
      background: #0b1020;
      border-top: 1px solid rgba(255,255,255,0.10);
      font-size: 13px;
    }}
    .fade-up {{
      opacity: 1;
      transform: translateY(0);
      transition: opacity 420ms ease, transform 420ms ease;
    }}
    .motion-ready .fade-up.motion-visible {{
      opacity: 1;
      transform: translateY(0);
    }}
    @keyframes orbit {{
      from {{ transform: rotate(-18deg) scaleY(0.42); }}
      to {{ transform: rotate(342deg) scaleY(0.42); }}
    }}
    @keyframes statusPulse {{
      0%, 100% {{ transform: scale(1); box-shadow: 0 0 12px rgba(32,199,135,0.42); }}
      50% {{ transform: scale(1.32); box-shadow: 0 0 22px rgba(32,199,135,0.78); }}
    }}
    @keyframes progressGlow {{
      0%, 100% {{ filter: brightness(1); }}
      50% {{ filter: brightness(1.14); }}
    }}
    @keyframes softSweep {{
      0%, 46% {{ transform: translateX(-110%); opacity: 0; }}
      58% {{ opacity: 1; }}
      100% {{ transform: translateX(110%); opacity: 0; }}
    }}
    .hero-brand-stack {{
      position: relative;
      display: grid;
      justify-items: center;
      gap: 10px;
      width: 100%;
    }}
    .hero-brand-caption {{
      color: rgba(245,217,138,0.90);
      font-size: 12px;
      font-weight: 760;
      letter-spacing: 0.22em;
      text-transform: uppercase;
      text-shadow: 0 0 22px rgba(212,175,55,0.42);
    }}
    .premium-skin {{
      background:
        radial-gradient(circle at 50% 8%, rgba(245,217,138,0.16), transparent 24%),
        radial-gradient(circle at 78% 18%, rgba(37,99,235,0.18), transparent 30%),
        radial-gradient(circle at 15% 26%, rgba(125,211,252,0.11), transparent 34%),
        linear-gradient(180deg, #020714 0%, #061226 45%, #020714 100%);
    }}
    .premium-skin::before {{
      opacity: 0.82;
      background-image:
        linear-gradient(rgba(245,217,138,0.042) 1px, transparent 1px),
        linear-gradient(90deg, rgba(125,211,252,0.028) 1px, transparent 1px);
      background-size: 56px 56px;
      mask-image: radial-gradient(circle at 50% 18%, black, transparent 74%);
    }}
    .premium-skin header {{
      min-height: 104px;
      background: rgba(2,7,20,0.86);
      border-bottom-color: rgba(245,217,138,0.14);
      box-shadow: 0 22px 60px rgba(0,0,0,0.28);
    }}
    .premium-skin nav {{
      letter-spacing: 0.01em;
      text-transform: uppercase;
      font-size: 12px;
    }}
    .premium-skin .hero {{
      min-height: calc(100vh - 104px);
      background:
        radial-gradient(ellipse at 50% 100%, rgba(212,175,55,0.18), transparent 34%),
        radial-gradient(ellipse at 50% 112%, rgba(125,211,252,0.18), transparent 42%);
    }}
    .premium-skin .hero-copy h1 {{
      max-width: 760px;
      text-transform: uppercase;
      font-size: clamp(48px, 7vw, 98px);
      line-height: 0.92;
      text-shadow: 0 18px 55px rgba(0,0,0,0.45);
    }}
    .premium-skin .hero-copy p {{
      max-width: 520px;
      color: rgba(230,232,235,0.82);
      font-size: clamp(17px, 1.55vw, 23px);
    }}
    .premium-skin .eyebrow {{
      border-color: rgba(212,175,55,0.38);
      color: var(--atlas-gold-light);
      background: rgba(212,175,55,0.10);
      letter-spacing: 0.11em;
    }}
    .premium-skin .light-section,
    .premium-skin .ai-section {{
      color: var(--ink);
      background:
        radial-gradient(circle at 16% 8%, rgba(212,175,55,0.12), transparent 28%),
        radial-gradient(circle at 82% 18%, rgba(125,211,252,0.10), transparent 30%),
        linear-gradient(180deg, #081124 0%, #0b1020 100%);
    }}
    .premium-skin .section-head h2 {{
      color: #ffffff;
      text-shadow: 0 0 34px rgba(212,175,55,0.14);
    }}
    .premium-skin .section-head p {{
      color: rgba(230,232,235,0.72);
    }}
    .premium-skin .map-card,
    .premium-skin .country-panel,
    .premium-skin .step-card,
    .premium-skin .trust-card,
    .premium-skin .support-card,
    .premium-skin .ai-block {{
      border-color: rgba(245,217,138,0.16);
      background:
        linear-gradient(145deg, rgba(255,255,255,0.095), rgba(255,255,255,0.035)),
        rgba(7,17,38,0.78);
      box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.10),
        0 24px 70px rgba(0,0,0,0.30);
      backdrop-filter: blur(18px);
    }}
    .premium-skin .step-card,
    .premium-skin .trust-card,
    .premium-skin .support-card,
    .premium-skin .ai-capability {{
      border-radius: 8px;
      position: relative;
      overflow: hidden;
    }}
    .premium-skin .step-card::after,
    .premium-skin .trust-card::after,
    .premium-skin .support-card::after,
    .premium-skin .ai-capability::after {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: linear-gradient(135deg, rgba(245,217,138,0.13), transparent 34%);
      opacity: 0.55;
    }}
    .premium-skin .step-card h3,
    .premium-skin .trust-card h3,
    .premium-skin .support-card h3,
    .premium-skin .country-item strong {{
      color: #ffffff;
    }}
    .premium-skin .step-card p,
    .premium-skin .trust-card p,
    .premium-skin .support-card p,
    .premium-skin .support-card li,
    .premium-skin .country-item span,
    .premium-skin .neutral-note {{
      color: rgba(230,232,235,0.68);
    }}
    .premium-skin .country-item,
    .premium-skin .neutral-note,
    .premium-skin .ai-capability {{
      border-color: rgba(230,232,235,0.12);
      background: rgba(3,8,22,0.42);
    }}
    .premium-skin .step-icon,
    .premium-skin .trust-icon,
    .premium-skin .support-icon {{
      border-radius: 4px;
      background:
        linear-gradient(145deg, rgba(255,255,255,0.58), rgba(255,255,255,0.02) 28%),
        linear-gradient(135deg, #f9df85 0%, #d4af37 46%, #8d6518 100%);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.56), 0 12px 24px rgba(212,175,55,0.20);
    }}
    .premium-skin .map-card {{
      background:
        radial-gradient(circle at 50% 45%, rgba(29,78,216,0.18), transparent 42%),
        linear-gradient(145deg, rgba(255,255,255,0.09), rgba(255,255,255,0.032)),
        #071126;
    }}
    .premium-skin .europe-map rect {{
      fill: #071126;
    }}
    .premium-skin .map-country {{
      fill: #1b2740;
      stroke: rgba(230,232,235,0.25);
    }}
    .premium-skin .map-region {{
      fill: #111d33;
      stroke: rgba(230,232,235,0.16);
    }}
    .premium-skin .map-graticule {{
      stroke: rgba(125,211,252,0.12);
    }}
    .premium-skin .map-coast {{
      stroke: rgba(125,211,252,0.25);
    }}
    .premium-skin .map-border {{
      stroke: rgba(230,232,235,0.16);
    }}
    .premium-skin .map-route {{
      stroke: #f5d98a;
      opacity: 0.62;
    }}
    .premium-skin .map-city {{
      fill: #071126;
      stroke: #f5d98a;
      filter: drop-shadow(0 0 8px rgba(245,217,138,0.48));
    }}
    .premium-skin .map-country.active {{
      fill: #d4af37;
      stroke: #f5d98a;
      filter: drop-shadow(0 0 15px rgba(212,175,55,0.55));
    }}
    .premium-skin .map-label {{
      fill: #071126;
      stroke: rgba(245,217,138,0.82);
    }}
    .premium-skin footer {{
      background: #030816;
    }}
    @media (max-width: 980px) {{
      .hero, .map-layout, .ai-block {{ grid-template-columns: 1fr; }}
      .hero {{ min-height: auto; }}
      .brand-stage {{ min-height: 300px; }}
      .steps-grid, .trust-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 720px) {{
      body {{
        padding-bottom: env(safe-area-inset-bottom);
      }}
      header {{
        flex-wrap: wrap;
        align-content: center;
        min-height: 158px;
        padding: calc(10px + env(safe-area-inset-top)) 16px 12px;
        background: rgba(5,10,22,0.88);
      }}
      .brand-logo {{
        justify-items: start;
        max-width: calc(100vw - 86px);
        gap: 0;
      }}
      .brand-logo-image {{
        width: min(266px, calc(100vw - 98px));
        max-height: 112px;
        object-fit: contain;
      }}
      .menu-toggle {{ display: grid; }}
      nav {{
        width: 100%;
        display: none;
        grid-template-columns: 1fr;
        gap: 4px;
        padding-top: 8px;
      }}
      nav.open {{ display: grid; }}
      nav a, .language-button {{
        min-height: 42px;
        padding: 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
      }}
      nav .secondary {{ display: none; }}
      .language-selector {{ width: 100%; }}
      .language-button {{ width: 100%; justify-content: space-between; }}
      .language-menu {{ position: static; width: 100%; margin-top: 8px; }}
      section {{ padding: 44px 24px; }}
      .hero {{
        gap: 18px;
        padding-top: 28px;
        padding-bottom: 34px;
      }}
      .hero::before {{
        height: 34%;
        background:
          radial-gradient(circle at 36% 4%, rgba(245,217,138,0.17), transparent 38%),
          radial-gradient(circle at 80% 10%, rgba(125,211,252,0.10), transparent 28%);
      }}
      .eyebrow {{
        min-height: 29px;
        gap: 7px;
        padding: 0 10px;
        font-size: 10px;
        letter-spacing: 0.065em;
      }}
      .eyebrow::before {{ width: 7px; height: 7px; }}
      h1 {{
        max-width: 318px;
        font-size: clamp(42px, 13.7vw, 60px);
        line-height: 0.86;
      }}
      .hero-copy {{ gap: 16px; max-width: 100%; }}
      .hero-copy p {{
        max-width: 322px;
        color: rgba(247,248,251,0.82);
        font-size: 18px;
        line-height: 1.34;
      }}
      .hero-actions {{ display: grid; grid-template-columns: 1fr; }}
      .button {{
        width: 100%;
        border-radius: 19px;
        font-size: 16px;
      }}
      .button.primary {{
        min-height: 66px;
        box-shadow: 0 16px 34px rgba(212,175,55,0.28);
      }}
      .hero-actions .button:not(.primary) {{
        min-height: 62px;
        border-color: rgba(230,232,235,0.24);
        background: rgba(255,255,255,0.045);
      }}
      .brand-stage {{ display: none; }}
      .brand-logo-caption {{
        max-width: calc(100vw - 98px);
        overflow: hidden;
        color: rgba(245,217,138,0.74);
        font-size: 7.5px;
        font-weight: 650;
        letter-spacing: 0.13em;
        text-overflow: ellipsis;
      }}
      .hero-brand-caption {{ font-size: 10px; letter-spacing: 0.16em; }}
      .hero-visual {{ gap: 14px; }}
      .atlas-for-you {{ gap: 5px; font-size: 13px; }}
      .atlas-for-you strong {{ font-size: 17px; }}
      .analysis-panel {{ padding: 15px; border-radius: 20px; }}
      .analysis-title {{ margin-bottom: 8px; font-size: 12px; }}
      .analysis-subtitle {{ font-size: 13px; margin-bottom: 12px; }}
      .analysis-step {{ min-height: 36px; font-size: 13px; }}
      .profile-preview-card {{ padding: 14px; border-radius: 20px; }}
      .map-card {{ min-height: 330px; padding: 12px; }}
      .europe-map {{ min-height: 300px; }}
      .steps-grid, .trust-grid, .ai-capabilities {{ grid-template-columns: 1fr; }}
      .step-card, .trust-card {{ min-height: 132px; }}
      footer {{ display: grid; }}
    }}
    @media (max-width: 340px) {{
      section {{ padding-left: 24px; padding-right: 24px; }}
      header {{ gap: 8px; padding-left: 14px; padding-right: 14px; }}
      .brand-logo {{ max-width: calc(100vw - 76px); }}
      .brand-logo-image {{ width: min(220px, calc(100vw - 100px)); }}
      .brand-logo-caption {{ max-width: calc(100vw - 100px); font-size: 7px; }}
      h1 {{ font-size: clamp(39px, 13.2vw, 52px); }}
      .hero-copy p {{ font-size: 17px; }}
      .button.primary {{ min-height: 64px; }}
      .hero-actions .button:not(.primary) {{ min-height: 60px; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
      }}
    }}
  </style>
</head>
<body class="premium-skin">
  <div class="shell">
    <header>
      {BRAND_LOGO_HTML}
      <button class="menu-toggle" type="button" aria-label="Menu" aria-expanded="false" id="menu-toggle">☰</button>
      <nav aria-label="Main navigation" id="main-nav">
        <a class="nav-primary" href="/ai?intent=job" data-i18n="landing.cta_create">Створити профіль</a>
        <a href="#how" data-i18n="landing.nav_how">Як працює</a>
        <a href="#map" data-i18n="landing.nav_europe">Європа</a>
        <a class="secondary" href="#support" data-i18n="landing.nav_support">Супровід</a>
        <a class="secondary" href="#trust" data-i18n="landing.nav_trust">Довіра</a>
        <a class="secondary" href="#atlas-ai">Atlas AI</a>
        <div class="language-selector" data-language-selector>
          <button class="language-button" type="button" aria-expanded="false" data-language-button>
            <span data-i18n="nav.languages">Мови</span>
            <span class="language-current" data-language-current>UK</span>
          </button>
          <div class="language-menu" role="menu" data-language-menu></div>
        </div>
      </nav>
    </header>

    <main>
      <section class="hero">
        <div class="hero-copy fade-up">
          <div class="eyebrow" data-i18n="landing.eyebrow">ATLAS Premium Workforce OS</div>
          <h1 data-i18n="landing.hero_title">AI Workforce Platform</h1>
          <p data-i18n="landing.hero_subtitle">Один профіль. Вся кар'єра. Уся Європа.</p>
          <div class="hero-actions">
            <a class="button primary" href="/ai?intent=job" data-analytics-event="create_profile_click" data-i18n="landing.cta_create">Створити профіль</a>
            <a class="button" href="/ai?demo=atlas" data-analytics-event="demo_click"><span class="play-icon" aria-hidden="true">▶</span><span data-i18n="landing.cta_demo">Переглянути демо</span></a>
          </div>
        </div>
        <div class="hero-visual fade-up">
          <div class="atlas-for-you">
            <strong data-i18n="landing.for_you_title">ATLAS працює для вас</strong>
            <span data-i18n="landing.for_you_text">Створює професійний профіль і веде кандидата до наступного кроку.</span>
          </div>
          <div class="analysis-panel ai-coordinator-card" aria-label="AI Analysis">
            <div class="analysis-title"><span data-i18n="landing.ai_coordinator_title">Ваш AI-координатор</span><span id="analysis-state" data-i18n="landing.analysis_live">Live</span></div>
            <p class="analysis-subtitle" data-i18n="landing.ai_coordinator_subtitle">Аналізує профіль, документи та можливості в реальному часі.</p>
            <div class="analysis-list" id="analysis-list">
              <div class="analysis-step active" data-i18n="landing.ai_step_experience">Аналізую ваш досвід</div>
              <div class="analysis-step" data-i18n="landing.ai_step_documents">Перевіряю документи</div>
              <div class="analysis-step" data-i18n="landing.ai_step_vacancies">Порівнюю доступні вакансії</div>
              <div class="analysis-step" data-i18n="landing.ai_step_opportunities">Визначаю найкращі можливості</div>
              <div class="analysis-step" data-i18n="landing.ai_step_route">Формую персональний маршрут</div>
            </div>
            <div class="profile-progress" aria-label="Profile progress">
              <div class="profile-progress-label"><span data-i18n="landing.profile_status_label">Статус профілю</span><strong data-i18n="landing.profile_ready">Профіль готовий на 78%</strong></div>
              <div class="progress-track"><div class="progress-fill"></div></div>
            </div>
          </div>
          <div class="profile-preview-card">
            <div class="candidate-head">
              <div class="candidate-photo" aria-hidden="true">O</div>
              <div>
                <strong class="candidate-name" data-i18n="landing.candidate_name">Oleksandr</strong>
                <span class="candidate-role" data-i18n="landing.candidate_role">Координатор / Recruiter</span>
                <span class="candidate-meta"><span data-i18n="country.PL">Польща</span> · <span data-i18n="landing.candidate_experience">Досвід: 4+ роки</span></span>
              </div>
            </div>
            <div class="candidate-statuses">
              <div class="candidate-status" data-i18n="landing.candidate_verified">Профіль підтверджено</div>
              <div class="candidate-status" data-i18n="landing.candidate_docs">Документи перевіряються</div>
              <div class="candidate-status" data-i18n="landing.candidate_matching">Підбір активний</div>
            </div>
          </div>
        </div>
      </section>

      <section class="light-section" id="map">
        <div class="section-head fade-up">
          <h2 data-i18n="landing.map_title">Європа в одному профілі</h2>
          <p data-i18n="landing.map_subtitle">ATLAS показує країни присутності та підтягує реальні показники з бекенда. До появи даних інтерфейс залишається нейтральним.</p>
        </div>
        <div class="map-layout">
          <div class="map-card fade-up">
            <svg class="europe-map" viewBox="0 0 760 520" role="img" aria-label="Europe presence map" data-i18n-aria-label="landing.map_aria">
              <rect x="0" y="0" width="760" height="520" rx="24" fill="#f8fafc"></rect>
              <path class="map-graticule" d="M28 120 H732 M28 214 H732 M28 308 H732 M28 402 H732 M154 26 V494 M280 26 V494 M406 26 V494 M532 26 V494 M658 26 V494"></path>
              <path class="map-region" d="M440.9 398.3 L441.1 396.8 L441.1 395.9 L440.1 394.7 L441.6 392.6 L443.4 390.8 L444.8 389.1 L445.7 389.0 L445.8 390.4 L446.5 391.0 L448.4 390.6 L449.9 390.1 L451.5 391.6 L453.5 393.0 L455.2 394.0 L456.4 396.6 L456.3 398.3 L455.5 400.3 L455.6 401.9 L454.8 402.6 L455.3 404.8 L456.3 407.4 L457.4 408.2 L458.5 410.1 L460.9 410.1 L461.3 410.7 L461.6 412.3 L462.1 413.5 L461.1 415.1 L459.3 415.7 L458.6 417.0 L457.9 418.1 L457.4 419.6 L455.8 420.2 L454.3 420.5 L453.4 421.2 L453.1 421.7 L453.9 423.0 L453.7 423.6 L452.8 423.7 L452.6 424.7 L451.7 425.3 L449.9 424.7 L449.2 424.6 L448.7 422.6 L442.7 418.5 L441.1 416.8 L441.1 416.1 L442.1 416.5 L442.1 415.3 L440.8 413.0 L442.4 409.7 L442.6 406.0 L442.1 403.7 L443.4 401.7 L443.8 399.3 L440.9 398.3 L440.9 398.3 Z"><title>Albania</title></path>
              <path class="map-region" d="M219.2 390.6 L218.8 390.7 L217.7 391.2 L217.0 391.4 L216.4 391.5 L215.9 391.4 L215.7 391.1 L215.7 390.7 L215.6 390.3 L215.5 390.1 L215.7 389.5 L216.1 389.2 L216.6 388.9 L217.4 389.0 L219.2 389.4 L219.6 389.8 L219.6 390.0 L219.3 390.4 L219.2 390.6 Z"><title>Andorra</title></path>
              <path class="map-region" d="M317.5 332.7 L318.7 330.3 L317.4 329.6 L319.0 329.6 L320.3 329.0 L323.1 329.8 L324.2 330.5 L324.3 331.2 L325.4 331.4 L325.8 332.1 L326.5 332.5 L328.1 331.5 L328.8 329.4 L329.5 329.4 L332.8 329.6 L334.4 329.9 L335.4 330.8 L336.5 331.2 L338.4 330.8 L339.7 330.8 L340.9 330.1 L343.2 329.3 L350.9 328.4 L351.0 327.4 L351.9 327.4 L354.0 327.9 L355.2 328.2 L357.2 327.8 L358.6 328.6 L358.4 329.1 L359.6 329.8 L361.3 330.2 L361.7 328.9 L361.6 327.5 L360.2 327.3 L360.0 326.9 L360.6 325.1 L358.1 322.9 L358.8 321.9 L362.2 320.5 L363.8 320.1 L365.9 319.4 L366.9 317.0 L367.3 316.7 L369.8 317.3 L371.0 316.7 L371.2 315.5 L371.4 314.5 L372.8 315.0 L374.3 316.5 L378.3 316.8 L379.9 316.2 L382.4 316.5 L383.6 314.7 L385.3 314.4 L385.9 311.9 L387.1 311.7 L388.3 312.3 L389.5 312.1 L391.4 312.2 L395.1 313.4 L396.7 313.3 L401.6 314.8 L404.1 314.4 L405.7 314.1 L407.8 314.9 L409.3 315.1 L410.5 316.3 L410.8 316.7 L410.2 317.7 L409.7 319.1 L412.3 322.8 L413.3 323.7 L412.4 325.0 L411.8 325.8 L412.0 326.7 L411.1 327.5 L409.2 327.5 L408.3 327.6 L406.3 326.9 L405.4 327.2 L404.2 327.8 L406.9 328.6 L406.9 330.2 L406.1 330.8 L404.4 331.1 L404.7 332.7 L404.1 333.3 L404.9 334.3 L405.0 334.9 L404.7 335.7 L404.2 336.0 L402.0 336.3 L399.3 337.9 L398.6 339.5 L398.3 339.9 L395.8 339.5 L393.1 340.2 L389.0 340.3 L385.6 340.7 L384.3 341.1 L383.2 342.1 L381.2 342.8 L380.6 343.3 L379.6 343.1 L377.1 342.8 L374.0 342.3 L371.6 341.9 L369.9 341.8 L365.6 341.3 L358.7 340.5 L356.1 340.2 L353.5 339.6 L351.9 338.0 L350.2 336.2 L351.1 335.2 L350.7 335.0 L345.8 336.1 L343.9 336.0 L341.4 336.2 L337.7 336.7 L336.3 338.4 L335.1 338.8 L333.0 338.5 L330.7 337.8 L329.1 337.6 L328.6 336.4 L325.7 337.6 L323.4 337.4 L321.7 336.3 L320.2 335.5 L318.2 335.3 L318.5 334.7 L318.0 334.1 L317.8 333.4 L317.6 332.9 L317.5 332.7 Z"><title>Austria</title></path>
              <path class="map-region" d="M597.0 274.0 L591.8 273.9 L589.5 274.4 L587.2 274.6 L584.4 276.5 L582.9 278.0 L581.6 280.1 L582.4 281.6 L582.8 283.0 L581.7 284.1 L579.0 283.4 L577.6 281.9 L575.7 281.5 L571.2 282.0 L568.2 282.4 L566.0 282.3 L564.5 280.3 L563.6 279.7 L562.5 280.1 L561.4 280.5 L559.7 281.1 L558.4 282.0 L557.2 280.8 L555.1 280.5 L552.0 280.0 L550.7 280.5 L547.9 280.1 L547.1 280.9 L545.9 281.5 L545.8 280.4 L542.8 280.0 L540.9 280.1 L538.9 278.2 L536.5 278.2 L531.7 277.6 L529.5 277.1 L523.6 276.2 L519.3 276.1 L512.8 276.0 L510.3 276.4 L507.1 276.5 L504.0 276.8 L502.9 277.9 L499.2 280.2 L497.7 279.8 L495.7 279.6 L494.5 279.9 L494.5 281.1 L493.7 278.7 L494.7 277.5 L495.0 275.5 L494.8 274.3 L493.2 273.5 L491.0 272.7 L489.1 271.7 L489.4 271.1 L492.0 268.9 L497.5 267.1 L498.4 265.8 L498.3 264.2 L497.7 261.7 L494.4 255.8 L493.9 251.9 L497.8 251.7 L499.5 251.7 L501.8 251.5 L503.4 252.2 L507.2 251.1 L509.4 250.9 L510.4 249.1 L513.4 249.0 L515.6 247.8 L517.8 247.3 L518.6 248.3 L518.4 248.9 L520.6 249.2 L521.6 248.7 L521.4 247.7 L519.8 247.1 L518.9 246.8 L519.8 245.3 L521.1 244.0 L521.1 243.2 L521.8 240.8 L524.1 239.4 L526.8 238.7 L527.5 237.6 L528.2 237.0 L532.7 236.2 L533.8 235.7 L534.1 235.2 L530.8 234.9 L530.5 234.2 L531.7 232.1 L532.0 230.6 L534.3 230.3 L536.6 228.8 L541.0 229.0 L542.9 229.0 L544.6 228.9 L545.9 227.3 L550.1 225.0 L551.6 224.8 L553.7 225.9 L554.8 225.5 L557.7 225.8 L559.0 227.1 L561.6 226.5 L563.4 226.3 L567.0 227.3 L567.3 228.0 L566.7 229.2 L568.3 230.4 L570.9 229.4 L572.6 229.1 L574.1 228.5 L577.8 228.5 L580.8 229.4 L582.7 230.6 L583.9 231.2 L585.6 231.3 L586.3 231.8 L586.2 233.9 L585.2 234.7 L585.1 235.3 L586.9 237.1 L587.1 238.1 L585.3 239.8 L584.8 241.1 L587.2 242.4 L589.3 243.3 L588.5 244.6 L589.8 245.4 L591.2 247.3 L595.3 249.5 L597.8 250.5 L597.8 251.7 L596.9 253.2 L599.9 253.4 L605.7 254.6 L605.3 255.5 L605.9 256.4 L608.9 257.9 L608.9 259.0 L607.3 259.2 L605.4 260.5 L601.8 261.9 L598.1 261.7 L596.8 260.8 L594.5 260.6 L592.3 260.8 L591.2 262.3 L591.1 263.2 L593.0 264.7 L594.5 266.0 L594.0 266.7 L595.2 268.6 L594.7 270.0 L595.0 271.7 L596.1 272.5 L597.0 274.0 L597.0 274.0 Z"><title>Belarus</title></path>
              <path class="map-region" d="M250.8 282.7 L252.7 283.0 L252.8 282.2 L254.3 281.6 L255.4 282.2 L257.5 281.4 L258.2 281.8 L258.3 282.3 L259.9 282.4 L261.0 281.6 L261.5 282.4 L263.3 284.0 L266.0 284.0 L267.0 284.0 L268.2 284.9 L270.6 285.5 L270.9 286.3 L269.9 287.8 L269.8 288.2 L268.6 289.3 L269.3 290.1 L270.0 290.3 L271.8 290.4 L273.2 290.6 L275.1 291.8 L275.3 292.9 L275.7 293.4 L277.4 294.0 L277.7 295.7 L274.7 297.8 L274.5 298.0 L273.8 297.6 L271.5 298.5 L270.5 300.0 L269.8 301.0 L269.7 301.5 L270.5 302.4 L271.6 303.8 L271.1 304.6 L270.5 305.1 L268.2 305.2 L266.9 305.5 L265.0 304.1 L264.1 303.4 L262.1 302.9 L260.7 302.2 L258.9 302.1 L258.6 300.5 L258.8 297.9 L257.7 297.8 L256.5 298.9 L254.9 300.0 L250.2 300.0 L249.7 299.7 L249.9 299.2 L250.4 298.4 L249.7 297.8 L250.1 296.8 L248.6 295.6 L246.2 295.4 L244.8 295.3 L244.1 295.8 L243.3 293.9 L241.4 293.4 L238.9 293.0 L238.4 291.4 L237.4 290.4 L235.7 290.2 L233.7 290.8 L232.4 290.4 L230.4 288.9 L230.4 287.9 L229.6 286.7 L234.9 284.1 L239.8 282.8 L240.5 284.1 L241.4 284.4 L242.7 283.9 L244.9 284.3 L245.9 284.8 L248.5 284.3 L250.7 283.1 L250.8 282.7 Z"><title>Belgium</title></path>
              <path class="map-region" d="M441.0 361.7 L440.8 363.0 L439.4 365.0 L438.2 366.6 L438.1 368.1 L438.5 368.8 L440.8 369.7 L443.5 371.5 L443.9 372.3 L442.2 372.7 L440.4 372.5 L439.7 372.9 L441.1 374.3 L442.8 376.8 L442.2 377.8 L441.1 377.4 L439.8 377.5 L438.6 378.1 L437.6 378.3 L436.2 378.0 L435.8 378.6 L437.0 380.3 L436.3 381.1 L435.3 380.4 L433.4 381.2 L432.3 382.2 L431.8 383.1 L430.1 384.4 L429.6 385.0 L429.9 387.3 L430.9 389.0 L430.0 389.7 L429.5 389.9 L427.8 389.5 L424.6 387.7 L422.0 386.5 L420.7 385.6 L418.8 385.3 L419.7 384.8 L419.3 384.1 L415.1 380.9 L414.9 379.2 L412.5 378.3 L407.8 375.1 L406.3 373.5 L403.6 371.7 L401.6 369.8 L400.5 366.7 L399.5 365.9 L395.5 363.1 L395.9 360.2 L396.6 357.8 L398.4 357.7 L400.8 359.4 L402.5 360.2 L404.6 358.3 L408.8 357.9 L413.0 358.2 L414.7 358.2 L417.3 358.7 L418.3 358.8 L420.1 358.4 L422.4 359.3 L424.0 358.6 L426.7 358.7 L428.5 358.8 L430.1 359.2 L433.4 360.0 L433.8 360.9 L434.5 361.7 L436.7 361.9 L438.2 361.5 L440.5 361.5 L441.0 361.7 Z"><title>Bosnia and Herzegovina</title></path>
              <path class="map-region" d="M549.9 397.1 L547.6 397.0 L546.4 397.2 L544.4 397.6 L543.1 397.4 L540.9 395.8 L539.6 395.8 L536.8 396.4 L534.6 397.1 L532.3 397.2 L531.5 398.0 L531.0 398.9 L528.7 399.5 L528.6 400.2 L525.9 400.1 L525.4 400.7 L526.0 401.5 L526.5 403.6 L525.4 404.6 L521.9 404.9 L519.8 405.1 L516.8 405.7 L513.7 405.1 L510.1 404.1 L509.2 404.6 L506.9 403.5 L505.9 402.2 L504.3 402.5 L502.3 402.5 L499.8 403.2 L499.1 403.4 L496.4 403.9 L493.6 404.2 L491.5 404.2 L488.8 405.0 L485.8 404.8 L486.2 401.5 L486.9 399.9 L486.2 399.5 L484.8 396.8 L482.9 396.0 L480.5 394.7 L479.6 392.8 L480.9 391.4 L480.9 390.6 L479.8 389.1 L480.1 387.6 L480.2 386.5 L481.3 386.1 L484.3 384.8 L485.8 383.7 L486.5 382.9 L485.1 381.5 L483.9 380.3 L481.3 379.1 L480.2 377.3 L479.2 376.0 L478.9 375.1 L479.3 372.8 L480.2 372.2 L481.9 370.6 L482.7 369.8 L484.0 370.1 L487.2 371.5 L486.7 372.2 L485.2 373.1 L485.2 374.1 L489.7 374.0 L498.8 375.0 L504.8 374.9 L514.0 376.3 L520.6 375.9 L523.7 374.0 L530.7 371.4 L538.2 370.4 L542.5 372.2 L545.6 372.5 L546.4 373.0 L549.1 373.4 L552.5 375.2 L555.0 375.6 L556.8 378.5 L553.7 379.4 L550.2 381.3 L548.8 382.3 L548.3 387.6 L546.6 388.2 L545.2 391.9 L547.5 394.2 L549.9 397.1 L549.9 397.1 Z"><title>Bulgaria</title></path>
              <path class="map-region" d="M368.4 354.0 L372.2 355.1 L373.3 354.4 L373.6 354.1 L375.7 354.4 L378.4 354.4 L380.1 353.1 L380.9 352.3 L381.4 352.9 L382.9 354.1 L384.4 354.6 L385.7 354.2 L389.3 354.9 L390.4 354.2 L389.9 353.2 L390.8 352.4 L389.7 351.6 L392.0 350.6 L394.5 349.8 L394.8 348.3 L393.8 346.8 L393.9 346.0 L395.1 345.5 L396.9 345.0 L398.9 344.4 L400.2 343.5 L402.0 343.4 L402.1 342.0 L402.9 341.6 L405.3 342.1 L408.3 343.1 L410.7 345.0 L413.3 346.4 L415.3 348.2 L418.1 348.8 L419.5 349.7 L421.6 350.7 L427.3 351.0 L428.5 351.1 L430.7 350.6 L432.4 349.3 L434.5 349.2 L435.4 349.0 L435.2 349.8 L435.2 351.0 L435.5 353.0 L437.3 353.9 L437.0 354.2 L436.6 355.4 L440.0 356.9 L441.0 357.3 L441.6 357.7 L441.5 358.2 L439.2 358.2 L438.2 358.2 L437.4 358.6 L437.6 361.2 L437.0 361.3 L436.5 361.5 L435.8 361.9 L433.9 361.3 L433.8 360.6 L432.3 359.3 L429.3 359.0 L427.6 358.7 L425.7 358.8 L423.4 358.9 L421.6 359.3 L419.6 358.3 L417.7 358.8 L415.5 358.3 L414.1 358.4 L410.4 356.9 L405.5 357.7 L403.4 359.6 L401.8 360.0 L399.2 358.0 L397.5 357.7 L396.2 358.1 L395.6 362.0 L397.3 364.2 L400.2 366.1 L401.0 368.2 L402.6 370.9 L404.8 372.4 L407.5 374.7 L410.2 376.7 L414.5 378.9 L414.9 380.4 L416.5 382.2 L419.6 384.5 L419.5 385.1 L418.2 385.1 L413.1 382.0 L406.4 379.0 L402.2 378.1 L399.4 378.5 L398.1 377.7 L398.1 376.6 L394.5 374.7 L388.6 370.3 L388.6 369.1 L389.9 368.9 L392.2 369.1 L389.7 367.8 L385.0 363.9 L385.1 360.6 L381.7 357.6 L378.6 356.1 L377.1 356.9 L374.9 360.3 L373.3 362.3 L372.0 362.3 L369.1 359.0 L368.7 357.5 L368.4 354.0 L368.4 354.0 Z M407.0 384.6 L409.4 385.0 L411.1 384.8 L412.6 385.0 L413.6 385.4 L413.8 385.6 L412.6 385.6 L411.1 385.5 L409.6 385.9 L408.1 385.7 L407.6 385.4 L407.2 385.1 L407.0 384.6 Z M413.9 383.1 L413.0 383.2 L407.4 383.1 L405.8 382.8 L404.0 382.2 L403.6 382.0 L405.4 381.8 L407.1 382.0 L407.6 382.5 L412.2 382.8 L413.9 383.1 Z M408.7 381.3 L406.7 381.3 L405.0 381.1 L404.2 380.7 L404.2 380.4 L404.5 379.9 L406.4 380.0 L409.3 380.3 L410.1 380.8 L409.8 381.0 L408.7 381.3 Z M389.2 371.7 L389.4 372.1 L387.8 371.3 L387.2 370.8 L387.1 370.5 L389.2 371.7 Z M383.9 360.6 L382.4 360.8 L381.6 360.4 L381.4 360.0 L380.1 359.9 L379.4 359.3 L379.2 359.1 L380.3 358.5 L380.9 357.6 L381.6 358.1 L382.5 359.2 L383.0 359.5 L383.9 360.6 Z M384.2 363.2 L384.5 363.8 L383.3 363.3 L382.2 363.1 L382.0 362.7 L382.2 362.4 L382.4 362.1 L383.2 362.2 L383.3 362.5 L384.2 363.2 Z M388.7 368.4 L388.3 368.7 L387.5 368.1 L386.8 367.7 L386.2 367.2 L385.2 366.5 L384.8 365.8 L383.3 364.4 L383.0 364.0 L383.8 364.6 L384.5 364.9 L385.0 365.0 L386.4 365.9 L387.7 367.1 L389.3 368.2 L389.0 368.2 L388.7 368.4 Z M388.7 373.4 L388.8 373.6 L388.8 373.7 L388.2 373.5 L388.0 373.6 L384.9 370.9 L384.6 370.4 L385.7 371.0 L388.7 373.4 Z M391.0 372.8 L391.8 373.7 L391.0 373.5 L390.2 372.9 L389.7 372.3 L391.0 372.8 Z M379.9 364.4 L379.8 364.9 L379.0 364.3 L378.6 363.2 L377.6 361.5 L377.5 361.0 L378.0 360.5 L378.0 360.0 L377.3 358.5 L377.9 358.3 L378.2 358.3 L378.4 359.3 L378.7 359.9 L379.6 360.6 L379.4 361.9 L379.6 363.6 L379.8 364.0 L379.9 364.4 Z M419.1 387.4 L420.8 388.2 L415.8 387.1 L416.3 387.0 L416.9 387.0 L419.1 387.4 Z M429.5 389.9 L429.5 390.4 L430.0 390.9 L430.5 391.5 L428.2 390.3 L426.0 389.0 L421.8 387.1 L418.8 386.6 L414.7 385.0 L412.0 384.4 L413.0 384.3 L414.2 384.3 L420.5 386.4 L419.8 385.8 L420.7 385.6 L421.5 385.8 L422.0 386.5 L423.0 386.9 L424.6 387.7 L425.6 388.4 L427.8 389.5 L428.4 389.6 L429.5 389.9 Z"><title>Croatia</title></path>
              <path class="map-region" d="M609.0 479.8 L609.1 480.1 L609.9 480.4 L610.9 480.8 L611.6 480.8 L612.4 480.4 L613.5 480.1 L615.0 479.7 L615.7 479.9 L616.7 480.0 L617.4 479.9 L617.9 480.1 L618.3 480.6 L618.4 481.8 L618.6 481.8 L619.2 481.4 L620.3 481.6 L621.1 481.6 L621.7 481.4 L622.1 481.4 L622.5 481.3 L623.0 481.0 L623.5 480.7 L623.9 480.8 L624.7 481.2 L625.2 481.1 L625.4 481.3 L625.8 482.0 L624.3 482.2 L622.9 482.3 L622.1 482.2 L621.4 482.2 L619.0 484.2 L617.8 484.9 L616.3 485.3 L614.8 485.5 L614.0 485.5 L613.4 485.8 L612.9 486.3 L612.9 486.7 L612.7 487.1 L611.8 487.0 L611.5 486.3 L610.9 486.0 L609.4 486.1 L608.7 486.1 L606.4 485.4 L605.6 485.1 L605.2 484.5 L604.0 482.4 L603.8 480.8 L604.9 481.2 L606.0 480.8 L607.0 480.0 L608.2 479.6 L609.0 479.8 Z"><title>Cyprus</title></path>
              <path class="map-region" d="M434.5 305.5 L433.4 305.7 L431.5 305.7 L430.0 306.5 L428.8 307.2 L426.0 308.5 L425.4 309.5 L425.1 310.9 L423.3 311.5 L422.7 312.0 L421.0 313.0 L417.5 313.8 L413.8 313.4 L412.2 314.3 L410.8 316.5 L410.0 315.3 L408.5 315.0 L406.4 314.3 L404.9 314.1 L403.5 314.8 L399.6 314.6 L395.9 313.3 L393.8 313.0 L390.2 312.0 L388.8 312.3 L388.0 312.0 L386.2 311.6 L385.6 313.8 L384.0 314.4 L382.6 315.7 L380.7 316.4 L379.1 316.3 L376.1 316.8 L373.6 315.4 L371.7 314.6 L370.8 313.9 L368.0 312.2 L366.2 311.9 L365.4 310.9 L364.0 310.3 L361.4 308.5 L358.8 307.7 L357.1 306.6 L355.6 304.7 L354.3 303.4 L353.5 302.7 L354.5 301.6 L355.0 301.0 L354.3 300.0 L352.0 299.0 L350.9 297.7 L350.2 296.9 L349.7 295.8 L350.3 295.7 L351.5 296.5 L352.4 297.0 L354.3 295.3 L356.6 294.7 L358.2 294.3 L360.4 294.6 L361.1 294.0 L363.4 293.3 L364.5 292.5 L365.4 292.1 L366.2 292.1 L367.1 292.0 L368.1 290.9 L372.4 290.3 L374.9 289.5 L378.4 288.6 L377.5 287.9 L376.9 287.3 L377.7 286.9 L380.1 287.2 L380.8 287.9 L381.6 288.4 L382.0 289.4 L383.4 289.6 L383.9 289.1 L386.1 288.7 L386.1 287.3 L387.9 287.4 L389.8 288.8 L390.7 289.6 L392.1 289.9 L395.5 290.5 L397.5 291.3 L398.5 291.8 L399.7 291.8 L403.4 292.0 L404.1 292.5 L403.6 293.2 L402.4 293.6 L401.5 294.4 L402.5 295.0 L403.3 295.3 L406.4 298.0 L407.4 298.3 L408.6 297.6 L410.1 297.1 L411.3 296.3 L409.8 294.5 L411.2 294.4 L416.6 296.4 L418.4 296.3 L420.3 295.8 L420.7 296.7 L418.8 297.6 L419.3 298.1 L420.8 298.8 L421.9 299.7 L423.8 299.5 L424.4 299.1 L425.1 299.4 L426.6 299.9 L427.8 300.6 L430.5 300.7 L431.3 301.4 L431.5 302.5 L434.4 305.1 L434.5 305.5 Z"><title>Czech Republic</title></path>
              <path class="map-region" d="M355.7 229.2 L355.8 230.4 L355.4 230.8 L354.9 231.0 L353.7 231.2 L352.6 231.6 L351.6 232.2 L351.3 233.1 L352.0 233.7 L353.4 234.0 L353.8 235.2 L352.6 235.8 L349.7 236.4 L349.4 237.9 L349.5 239.0 L349.4 239.8 L349.2 241.0 L346.8 241.5 L345.3 239.8 L345.3 239.1 L344.8 238.3 L344.8 237.6 L344.2 236.5 L342.0 236.2 L341.1 236.1 L339.9 236.3 L339.6 236.2 L338.1 234.7 L338.4 233.1 L337.6 232.2 L337.5 231.8 L337.5 231.4 L336.9 231.1 L336.1 230.9 L335.7 230.0 L336.6 229.7 L338.8 229.8 L339.5 229.8 L340.1 229.6 L341.8 228.0 L341.8 227.7 L342.0 227.3 L343.9 227.1 L344.7 227.7 L344.6 228.6 L344.7 229.9 L345.9 230.2 L346.3 230.2 L346.8 229.3 L347.1 228.9 L347.6 228.7 L347.7 227.8 L347.5 227.3 L346.9 227.0 L349.1 225.9 L351.3 225.1 L352.6 225.1 L354.0 225.3 L355.2 225.6 L355.8 225.8 L356.2 226.2 L355.4 227.1 L355.2 227.6 L355.7 229.2 Z M320.2 240.8 L319.2 240.7 L317.1 240.7 L314.1 241.1 L309.6 240.0 L306.7 239.9 L306.6 238.9 L305.5 237.1 L306.5 234.7 L302.6 232.5 L300.6 227.8 L299.8 224.9 L300.3 219.2 L301.8 219.1 L305.2 219.8 L306.7 220.5 L307.5 218.9 L310.8 217.2 L312.6 217.4 L313.5 216.7 L312.2 213.9 L309.3 215.8 L305.9 217.9 L302.6 217.9 L301.6 216.7 L303.7 214.6 L308.5 213.1 L311.3 212.5 L316.3 212.3 L321.1 208.6 L326.7 206.9 L331.1 205.5 L329.2 206.9 L330.2 209.0 L330.0 211.5 L327.7 214.2 L327.0 216.6 L327.0 219.0 L329.6 220.2 L334.5 220.6 L334.7 222.2 L332.9 223.6 L330.2 224.1 L328.1 223.5 L326.3 226.5 L325.4 228.3 L323.6 228.1 L323.0 228.8 L323.4 229.8 L321.0 230.8 L319.2 232.0 L318.7 233.7 L319.3 235.5 L317.2 237.3 L318.1 238.2 L319.5 238.7 L319.7 239.6 L320.2 240.8 Z M331.5 231.3 L332.1 231.9 L332.7 233.3 L333.7 234.8 L333.3 235.4 L333.6 236.3 L333.3 237.1 L331.3 238.1 L329.0 238.1 L326.6 237.7 L323.3 236.7 L323.0 236.2 L322.5 235.9 L321.7 234.4 L321.7 232.5 L323.4 232.2 L327.0 231.3 L327.9 231.4 L328.8 231.9 L329.8 231.9 L331.3 231.3 L331.5 231.3 Z M340.5 240.0 L342.8 240.8 L344.3 240.8 L345.3 241.1 L345.5 241.6 L345.6 242.6 L344.6 242.9 L343.4 242.8 L341.8 243.2 L336.4 241.5 L336.5 240.0 L336.7 239.4 L339.2 239.3 L340.5 240.0 Z M332.7 241.8 L332.1 241.8 L331.3 240.8 L331.2 240.5 L332.1 239.9 L332.7 239.2 L334.2 238.1 L335.1 236.8 L335.4 236.8 L335.0 238.0 L333.0 241.2 L332.7 241.8 Z M355.5 239.1 L355.0 239.3 L353.1 239.2 L350.9 240.0 L350.1 239.8 L350.4 239.2 L350.6 239.0 L351.3 238.8 L351.8 238.5 L352.0 237.9 L352.5 238.2 L353.8 238.3 L354.5 238.5 L355.0 238.8 L355.5 239.1 Z M356.9 231.5 L355.8 232.0 L355.5 232.0 L355.1 231.3 L355.7 230.8 L356.1 230.5 L356.4 230.5 L356.7 230.9 L356.9 231.5 Z M329.5 240.6 L328.7 240.7 L327.7 240.4 L326.1 239.4 L325.9 239.2 L326.8 239.3 L327.8 239.9 L328.6 240.0 L329.8 240.4 L329.5 240.6 Z M324.2 240.1 L322.9 240.3 L322.2 240.0 L321.0 239.9 L320.6 238.0 L320.7 237.9 L321.3 238.0 L323.4 238.9 L324.2 239.8 L324.2 240.1 Z M331.1 229.2 L330.8 229.4 L330.1 229.2 L330.0 228.4 L330.3 227.7 L329.9 227.1 L330.3 226.7 L331.4 227.6 L331.7 228.1 L331.3 228.6 L331.1 229.2 Z M336.7 211.3 L336.1 211.6 L334.4 211.2 L335.2 210.7 L337.1 210.4 L338.2 210.5 L337.0 211.0 L336.7 211.3 Z M387.4 238.5 L386.9 238.7 L384.8 238.3 L382.3 237.5 L382.7 235.8 L383.3 235.1 L388.0 237.0 L388.0 237.7 L387.4 238.5 Z"><title>Denmark</title></path>
              <path class="map-region" d="M541.6 208.0 L539.5 207.9 L536.7 207.0 L534.9 207.3 L530.4 207.8 L527.3 206.4 L524.8 204.5 L522.0 203.9 L520.3 203.2 L516.3 201.8 L515.4 201.9 L515.2 202.3 L514.2 201.9 L510.9 202.2 L509.2 202.4 L504.0 203.9 L503.6 203.4 L505.6 199.1 L506.3 198.6 L504.4 197.6 L503.0 198.3 L500.9 199.0 L496.5 197.9 L495.6 196.1 L493.3 194.3 L495.0 193.1 L493.6 192.8 L493.1 192.3 L493.0 190.6 L492.7 189.7 L493.4 188.8 L494.9 187.2 L500.5 186.6 L501.6 185.5 L506.8 184.6 L517.6 183.8 L518.4 182.8 L519.7 182.5 L530.4 183.4 L535.3 184.4 L541.4 184.6 L549.7 184.4 L550.5 184.6 L551.6 185.6 L550.5 185.9 L549.9 186.4 L548.4 186.7 L546.7 189.5 L543.6 191.5 L542.6 192.7 L543.8 197.0 L543.5 198.3 L543.5 199.6 L545.2 202.1 L546.2 203.4 L546.9 203.8 L546.6 204.2 L543.6 205.1 L542.2 206.3 L541.6 207.7 L541.6 208.0 Z M482.0 194.7 L482.9 195.0 L483.8 194.9 L484.6 194.7 L486.4 194.9 L490.5 196.4 L490.9 196.8 L488.5 197.0 L487.9 197.4 L487.3 197.7 L486.6 197.8 L485.4 198.5 L483.8 199.1 L483.5 199.5 L480.6 199.4 L479.0 199.6 L477.7 200.3 L477.1 201.6 L476.2 202.7 L475.2 203.0 L474.2 203.1 L474.0 202.7 L474.1 202.3 L476.2 200.9 L476.6 200.4 L475.6 200.2 L474.7 199.7 L472.8 199.1 L472.5 198.6 L472.9 198.6 L473.3 198.4 L473.8 198.0 L474.1 197.6 L472.6 196.2 L473.3 196.0 L474.3 196.1 L475.3 196.4 L476.4 196.0 L476.9 195.9 L477.6 196.1 L478.4 195.2 L480.2 194.9 L481.2 194.6 L482.0 194.7 Z M485.9 192.2 L484.9 192.8 L484.3 192.6 L483.9 192.3 L482.6 193.6 L481.1 193.9 L480.2 193.6 L480.3 193.1 L479.5 191.8 L478.2 191.4 L476.3 191.3 L475.0 190.8 L480.1 190.4 L480.6 189.8 L481.7 189.1 L482.4 189.0 L483.1 189.2 L483.2 189.7 L483.4 189.9 L485.7 190.2 L486.6 191.1 L487.0 192.1 L485.9 192.2 Z M491.2 195.6 L490.1 195.7 L487.7 194.8 L488.2 194.2 L488.9 194.0 L491.0 194.4 L491.3 195.3 L491.2 195.6 Z"><title>Estonia</title></path>
              <path class="map-region" d="M501.4 107.4 L499.4 104.3 L496.3 102.7 L495.7 101.9 L495.3 100.4 L495.7 99.2 L497.7 98.0 L498.1 96.4 L499.3 95.2 L498.7 94.3 L496.4 92.8 L494.9 91.3 L494.7 90.0 L496.4 89.1 L496.1 87.7 L493.6 87.4 L492.6 87.3 L492.7 86.6 L493.6 85.7 L493.1 84.4 L493.2 82.2 L494.9 81.3 L491.3 79.6 L489.2 79.0 L486.5 76.9 L484.1 75.9 L476.7 74.9 L472.4 73.7 L469.5 72.8 L467.0 71.9 L464.0 70.6 L460.6 69.3 L460.4 68.8 L457.6 67.7 L462.5 68.0 L463.3 67.6 L462.5 65.9 L465.1 65.2 L469.2 65.2 L472.0 66.7 L475.3 68.6 L479.1 71.3 L480.6 71.9 L487.8 72.5 L490.9 72.8 L495.7 72.0 L497.6 70.9 L501.4 71.5 L505.6 72.3 L509.5 73.3 L513.1 72.9 L515.1 70.7 L518.0 70.0 L520.1 69.5 L521.7 67.6 L521.6 65.1 L524.1 61.4 L525.5 60.1 L528.4 59.0 L531.9 57.3 L536.3 57.3 L538.7 57.5 L541.5 56.9 L546.5 55.6 L550.3 56.7 L554.9 58.5 L564.1 60.4 L565.3 63.8 L562.6 65.0 L560.2 67.1 L561.9 68.3 L558.4 69.0 L554.9 69.7 L558.6 70.2 L559.4 70.5 L559.2 71.3 L555.6 74.8 L558.3 78.4 L566.6 79.9 L572.6 83.7 L574.7 84.7 L571.7 87.7 L567.2 90.4 L563.4 93.2 L563.1 94.2 L566.0 96.6 L568.1 98.5 L569.7 100.7 L571.3 102.2 L573.6 103.9 L576.0 107.6 L576.1 108.9 L573.4 109.1 L571.3 109.6 L571.4 111.4 L570.0 113.9 L570.0 114.3 L572.5 114.7 L572.7 115.4 L571.3 116.2 L569.8 117.1 L570.3 118.2 L572.1 119.5 L576.2 120.4 L576.4 121.5 L574.7 123.0 L576.2 124.9 L581.0 126.4 L581.5 127.6 L581.2 129.1 L577.5 131.7 L574.8 132.5 L580.1 135.4 L587.1 137.8 L590.5 139.8 L592.9 141.4 L594.2 142.4 L592.9 144.2 L591.0 146.7 L586.6 149.7 L580.9 152.8 L575.0 156.6 L571.0 159.2 L568.5 160.4 L562.2 163.7 L558.0 165.8 L555.4 166.8 L551.6 168.9 L546.7 171.5 L543.7 172.0 L540.2 171.4 L538.1 171.6 L533.6 172.4 L531.3 172.9 L531.5 171.3 L532.2 170.3 L530.8 171.2 L529.3 172.8 L525.0 172.2 L524.6 172.8 L525.0 173.8 L522.6 174.1 L521.0 174.7 L518.9 174.3 L515.4 174.9 L511.5 176.0 L507.0 176.6 L505.0 177.7 L499.7 177.8 L494.3 178.3 L491.0 178.9 L487.1 180.2 L487.0 179.5 L489.2 178.3 L488.7 177.4 L486.8 176.8 L485.2 175.3 L484.6 176.7 L483.7 177.3 L482.4 177.6 L479.8 177.1 L480.2 176.2 L480.2 175.5 L481.4 175.4 L481.7 174.8 L480.7 174.5 L481.6 173.3 L480.8 173.4 L473.5 171.9 L471.8 170.7 L469.4 171.5 L467.2 170.7 L466.9 169.5 L466.5 167.6 L466.5 165.1 L467.7 163.7 L468.3 160.8 L468.1 159.9 L468.7 159.6 L468.0 159.1 L469.2 158.9 L469.3 158.6 L468.6 157.2 L466.6 154.7 L465.5 152.3 L466.0 150.3 L463.8 148.6 L463.0 146.1 L463.5 144.6 L467.5 142.1 L469.9 141.0 L468.6 139.6 L471.8 138.6 L475.8 138.5 L478.3 137.3 L477.3 136.2 L478.6 136.1 L478.3 135.3 L480.9 134.4 L483.8 133.2 L488.5 131.0 L493.1 128.9 L495.1 127.7 L498.5 126.0 L502.9 123.1 L506.1 120.3 L507.7 119.5 L511.3 118.6 L514.7 119.0 L515.5 118.2 L515.4 117.4 L516.6 116.4 L515.2 115.4 L515.9 112.9 L515.0 110.5 L509.0 109.2 L506.7 108.0 L507.3 106.7 L506.1 107.2 L502.4 107.3 L501.4 107.4 Z M474.2 173.9 L473.3 173.9 L472.0 173.3 L471.8 173.1 L472.3 172.9 L472.0 172.5 L472.1 172.2 L473.1 172.6 L473.7 173.1 L473.1 173.2 L474.0 173.6 L474.2 173.9 Z M464.5 138.5 L464.6 138.8 L465.3 138.7 L466.3 138.3 L467.0 138.5 L466.9 139.1 L466.5 139.1 L466.3 139.0 L465.7 139.3 L465.6 139.5 L464.9 139.6 L463.6 139.1 L462.8 138.1 L464.7 138.1 L464.5 138.3 L464.5 138.5 Z M476.5 173.4 L478.1 173.7 L478.7 173.6 L479.5 174.3 L478.2 174.7 L478.1 175.2 L478.6 175.5 L478.8 175.9 L477.5 175.9 L476.9 175.6 L476.7 175.1 L476.1 174.7 L475.3 174.5 L475.6 174.1 L475.9 173.6 L476.5 173.4 Z M467.4 171.5 L467.2 172.1 L466.4 172.0 L465.5 172.1 L464.8 171.6 L464.4 170.6 L464.5 170.4 L465.1 170.2 L465.5 170.7 L467.4 171.5 Z M472.2 176.2 L470.9 176.7 L470.5 176.6 L470.6 175.9 L471.3 175.5 L472.6 175.5 L472.2 176.2 Z M469.6 176.6 L468.5 176.8 L467.8 176.4 L468.1 176.1 L468.9 175.9 L469.7 175.9 L469.9 176.2 L469.6 176.6 Z M510.1 117.3 L508.2 117.7 L506.7 117.4 L506.7 116.6 L507.6 116.3 L509.3 116.1 L511.6 116.5 L512.0 116.7 L510.6 116.8 L510.1 117.3 Z"><title>Finland</title></path>
              <path class="map-country" data-country="DE" d="M317.4 329.6 L313.2 327.8 L309.4 328.0 L308.7 327.4 L308.0 327.3 L307.4 327.5 L305.5 326.5 L303.8 327.1 L303.5 327.9 L305.2 328.0 L305.5 328.2 L304.3 328.5 L303.7 328.8 L302.4 328.6 L299.5 329.0 L294.5 329.0 L292.8 328.6 L292.5 326.6 L293.4 323.8 L293.5 321.9 L295.3 318.8 L296.2 316.1 L299.8 313.2 L300.0 312.0 L298.3 311.5 L293.4 310.9 L291.4 309.8 L289.7 310.1 L287.2 310.1 L286.2 310.3 L285.7 309.5 L284.3 309.1 L283.5 309.5 L282.4 309.7 L280.4 307.8 L279.9 306.9 L277.9 306.1 L277.5 305.4 L278.3 303.8 L279.2 303.1 L279.3 302.0 L277.2 301.5 L275.7 300.5 L274.5 299.1 L274.6 298.0 L275.3 296.7 L277.5 294.6 L276.9 293.6 L275.4 293.2 L276.1 292.3 L274.6 291.2 L273.1 290.4 L273.2 288.0 L271.8 287.5 L271.4 287.0 L272.4 286.9 L274.8 285.6 L274.6 285.2 L274.1 284.9 L275.2 283.0 L275.6 281.9 L274.9 280.7 L274.3 279.6 L272.5 278.1 L273.2 277.2 L274.6 276.8 L276.9 277.0 L277.8 277.3 L279.6 277.0 L282.9 275.9 L283.2 275.4 L282.1 274.5 L282.6 274.0 L283.9 273.5 L286.0 272.0 L286.2 270.6 L285.3 269.8 L283.6 269.8 L282.0 269.1 L282.1 268.5 L282.0 267.9 L282.6 267.5 L286.1 267.3 L287.2 264.4 L288.1 263.0 L288.2 259.6 L286.4 258.5 L287.1 256.3 L289.3 254.8 L298.4 254.6 L299.6 257.4 L301.4 257.6 L302.1 255.9 L304.0 256.3 L304.5 258.2 L304.7 254.9 L305.5 252.8 L309.6 252.9 L314.9 253.2 L319.3 256.2 L318.8 255.7 L313.6 252.2 L310.6 251.8 L309.6 250.9 L309.0 247.2 L307.5 247.3 L306.2 246.6 L308.7 245.7 L310.3 244.3 L308.2 242.4 L306.7 239.9 L309.1 239.9 L313.2 240.6 L315.2 241.1 L318.6 240.5 L320.0 240.8 L320.2 241.1 L322.8 241.9 L323.8 243.8 L321.8 245.1 L325.6 245.4 L328.0 245.6 L335.4 246.3 L336.8 247.5 L333.6 250.0 L335.0 250.9 L341.0 251.6 L344.8 249.5 L350.0 248.8 L352.3 247.4 L355.8 245.2 L359.9 245.7 L363.0 247.4 L370.2 249.0 L372.0 252.7 L374.0 253.7 L377.0 254.2 L377.2 255.4 L378.9 259.6 L378.9 260.6 L377.4 262.7 L375.5 263.9 L376.9 265.7 L381.5 268.8 L380.7 270.8 L381.5 271.8 L382.6 272.7 L382.6 273.9 L383.1 274.3 L382.4 275.7 L381.3 277.2 L382.3 278.9 L383.0 279.7 L382.8 281.0 L385.5 282.1 L386.5 284.3 L385.2 287.2 L383.9 289.1 L383.4 289.6 L382.0 289.4 L381.6 288.4 L380.8 287.9 L380.1 287.2 L377.7 286.9 L376.9 287.3 L377.5 287.9 L378.4 288.6 L374.9 289.5 L372.4 290.3 L368.1 290.9 L367.1 292.0 L366.2 292.1 L365.4 292.1 L364.5 292.5 L363.4 293.3 L361.1 294.0 L360.4 294.6 L358.2 294.3 L356.6 294.7 L354.3 295.3 L352.4 297.0 L351.5 296.5 L350.3 295.7 L349.7 295.8 L350.2 296.9 L350.9 297.7 L352.0 299.0 L354.3 300.0 L355.0 301.0 L354.5 301.6 L353.5 302.7 L354.3 303.4 L355.6 304.7 L357.1 306.6 L358.8 307.7 L361.4 308.5 L364.0 310.3 L365.4 310.9 L366.2 311.9 L368.0 312.2 L370.8 313.9 L371.2 314.7 L371.2 316.3 L370.2 317.2 L369.6 317.5 L367.1 316.9 L366.3 319.0 L365.2 319.8 L362.9 320.3 L359.9 321.3 L358.1 322.5 L359.3 324.0 L360.6 326.2 L359.9 327.2 L361.0 327.4 L361.8 328.0 L361.5 329.8 L360.7 330.2 L358.7 329.4 L358.4 328.8 L358.3 328.2 L356.0 328.0 L354.6 328.2 L353.1 327.6 L351.2 327.2 L351.1 328.1 L345.0 328.9 L341.9 329.8 L340.7 330.4 L338.7 330.9 L337.7 331.0 L335.8 331.1 L334.7 330.3 L334.4 329.7 L331.7 329.3 L329.0 329.3 L328.5 330.9 L327.4 332.2 L325.7 332.6 L325.9 331.6 L324.6 331.4 L324.4 330.8 L323.9 330.2 L321.4 329.3 L319.8 329.3 L317.8 329.5 L317.4 329.6 Z M370.1 246.2 L370.4 247.0 L370.0 247.5 L368.6 246.8 L367.2 246.8 L366.4 247.8 L365.7 247.9 L363.5 246.9 L363.2 246.5 L363.1 246.1 L363.4 244.7 L363.4 244.3 L364.1 243.8 L364.2 243.1 L365.4 242.4 L366.5 242.4 L366.8 243.0 L367.3 243.4 L369.1 243.9 L369.4 244.1 L369.6 244.4 L368.7 244.9 L368.4 245.2 L368.7 245.7 L370.1 246.2 Z M376.4 251.5 L376.2 251.9 L376.4 252.5 L375.9 252.4 L374.3 252.5 L372.8 252.4 L372.5 251.6 L372.7 250.9 L372.1 250.4 L371.5 250.2 L371.5 249.8 L371.5 249.3 L374.2 250.5 L376.4 251.5 Z M339.6 245.8 L337.6 245.8 L336.9 245.3 L336.1 245.2 L336.5 244.6 L337.1 244.4 L338.9 244.8 L339.5 245.6 L339.6 245.8 Z M302.2 241.3 L301.9 241.6 L302.0 239.8 L303.4 238.0 L304.0 238.1 L303.4 238.5 L303.2 238.9 L303.0 239.6 L303.1 239.9 L306.2 240.0 L305.8 240.4 L302.7 240.6 L302.2 241.3 Z M305.7 242.2 L305.2 242.5 L304.0 242.5 L303.3 242.2 L303.5 241.9 L304.2 241.7 L304.7 241.6 L305.5 241.8 L305.7 242.2 Z"><title>Germany</title></path>
              <path class="map-region" d="M548.0 463.0 L547.7 463.1 L547.1 462.6 L547.0 462.3 L547.7 462.0 L548.0 461.9 L548.1 462.1 L548.1 462.6 L548.0 463.0 Z M456.8 440.7 L457.0 442.1 L457.9 442.4 L459.1 443.6 L459.0 444.3 L458.7 444.5 L456.8 443.9 L456.3 444.2 L455.7 444.1 L455.4 443.4 L455.4 443.1 L455.1 442.7 L454.8 442.5 L454.1 443.1 L453.6 443.2 L453.6 442.7 L454.3 441.3 L454.6 441.0 L455.2 441.5 L455.7 441.3 L456.0 440.6 L456.1 439.8 L456.2 439.6 L456.8 440.7 Z M460.3 447.7 L461.6 448.9 L460.6 448.6 L459.4 449.5 L458.0 448.5 L457.1 447.5 L456.9 447.1 L457.8 446.2 L458.7 447.2 L459.7 447.3 L460.3 447.7 Z M457.8 438.0 L457.3 438.1 L456.9 438.0 L456.5 438.1 L456.1 438.3 L456.2 437.3 L456.6 436.1 L457.1 435.4 L457.9 435.1 L458.2 435.7 L458.1 437.6 L457.8 438.0 Z M458.7 441.4 L458.1 441.5 L457.3 440.3 L457.0 439.5 L457.3 439.5 L457.6 439.6 L458.0 439.9 L458.0 440.2 L458.1 440.5 L458.4 440.9 L458.7 441.4 Z M450.1 428.0 L450.4 428.6 L448.8 428.2 L447.7 427.6 L446.7 426.1 L444.7 424.4 L444.7 423.9 L445.5 423.5 L447.1 423.3 L447.8 423.5 L448.2 423.8 L448.3 424.1 L447.4 424.8 L447.2 425.1 L447.9 425.7 L447.9 425.9 L448.2 427.1 L448.6 427.5 L449.5 427.8 L450.1 428.0 Z M492.1 433.7 L492.8 435.0 L493.5 435.5 L494.9 436.0 L495.5 436.1 L497.9 437.0 L500.7 437.2 L501.0 437.5 L501.4 438.2 L501.9 438.8 L502.1 439.2 L501.8 439.7 L502.2 441.3 L502.9 442.7 L504.0 443.4 L505.3 443.6 L506.5 443.6 L506.8 443.9 L506.7 445.1 L506.2 445.6 L505.7 445.7 L505.4 445.6 L505.0 445.3 L504.7 445.2 L503.9 445.2 L503.4 444.6 L502.1 443.9 L501.8 443.5 L501.8 442.9 L501.2 442.4 L500.7 441.5 L500.2 441.3 L500.0 440.8 L499.9 440.6 L498.0 440.5 L496.4 440.5 L495.0 440.0 L494.6 438.7 L493.8 438.3 L493.2 437.9 L492.7 437.4 L491.4 436.4 L490.0 435.6 L488.7 435.1 L487.2 434.8 L486.0 435.2 L485.4 435.1 L485.2 434.8 L486.7 434.2 L488.7 433.2 L490.1 432.8 L490.8 432.8 L492.1 433.7 Z M496.7 431.8 L496.1 432.2 L495.2 432.1 L494.3 430.7 L496.7 431.8 Z M498.0 431.3 L497.4 431.4 L498.0 430.5 L499.1 430.0 L498.7 430.8 L498.0 431.3 Z M507.9 435.5 L506.6 435.8 L506.2 435.8 L506.5 435.4 L506.5 435.3 L505.2 434.6 L505.4 433.7 L505.5 433.5 L506.5 433.9 L506.7 434.7 L507.9 435.5 Z M509.2 413.6 L507.5 414.0 L505.9 413.2 L505.9 412.7 L506.8 411.7 L507.3 411.4 L508.5 411.5 L509.2 412.2 L509.3 412.5 L509.1 413.1 L509.2 413.6 Z M493.8 446.3 L493.3 446.6 L492.7 446.6 L492.3 446.5 L492.1 446.2 L492.4 446.1 L492.7 445.6 L492.9 445.5 L493.3 445.5 L493.6 445.7 L493.8 446.3 Z M487.5 467.4 L487.4 467.9 L486.1 467.5 L485.7 467.0 L485.7 465.8 L486.0 465.2 L486.2 465.0 L486.8 465.7 L488.1 466.7 L487.5 467.4 Z M539.4 476.2 L538.9 476.9 L538.4 476.3 L538.6 475.6 L538.0 474.6 L539.1 473.0 L539.1 472.3 L539.9 471.9 L539.7 473.2 L539.1 474.2 L539.8 475.0 L540.1 476.0 L539.4 476.2 Z M537.4 458.0 L536.1 458.2 L536.4 457.2 L535.7 456.5 L536.7 456.9 L537.3 457.4 L537.6 457.5 L537.6 457.8 L537.4 458.0 Z M536.5 460.8 L536.1 460.9 L536.6 460.3 L537.9 459.5 L539.8 458.8 L540.5 458.7 L541.6 459.1 L539.6 459.9 L539.0 460.2 L537.6 460.3 L536.5 460.8 Z M518.9 457.9 L517.7 458.4 L517.0 457.7 L516.5 456.7 L518.6 455.1 L519.1 455.3 L519.4 455.7 L519.3 457.1 L518.9 457.9 Z M515.5 456.7 L514.5 457.6 L513.7 457.5 L513.3 457.1 L513.8 456.2 L515.0 455.7 L515.5 455.9 L515.4 456.5 L515.5 456.7 Z M518.1 464.9 L517.5 465.6 L516.7 465.3 L517.0 465.1 L517.2 464.8 L517.2 464.3 L517.0 464.0 L517.1 463.9 L517.9 464.4 L518.1 464.9 Z M516.8 461.5 L516.6 461.7 L515.6 460.9 L515.3 460.5 L515.7 460.1 L517.1 461.0 L516.8 461.5 Z M534.9 447.7 L536.5 448.1 L536.9 448.0 L537.6 448.2 L537.8 448.9 L536.9 449.0 L535.2 449.7 L534.5 449.5 L533.6 449.0 L532.3 448.9 L531.9 448.7 L532.6 448.0 L533.9 447.7 L534.9 447.7 Z M524.9 451.1 L524.4 451.1 L524.5 450.7 L525.7 449.8 L527.2 449.8 L528.7 449.4 L529.0 449.3 L528.3 450.0 L527.1 450.6 L524.9 451.1 Z M522.8 460.1 L521.7 460.2 L521.3 460.1 L522.0 459.9 L522.5 459.7 L522.7 459.4 L523.8 458.9 L524.6 458.3 L525.4 458.7 L524.4 459.0 L522.8 460.1 Z M530.4 462.6 L529.4 462.9 L528.7 463.5 L528.0 463.0 L528.0 462.5 L528.8 462.6 L529.4 462.3 L529.2 461.9 L529.9 462.1 L530.4 462.6 Z M503.9 450.5 L503.1 451.1 L502.9 450.2 L503.5 449.3 L504.2 449.2 L504.5 449.6 L503.9 450.5 Z M504.9 453.3 L504.2 453.7 L504.4 452.9 L504.1 452.4 L504.4 452.1 L504.9 451.8 L505.1 452.1 L505.5 452.6 L504.9 453.3 Z M506.2 460.4 L506.2 461.1 L506.1 461.4 L503.5 461.7 L503.8 460.9 L503.9 460.6 L504.8 461.0 L505.1 460.8 L505.2 460.6 L506.2 460.4 Z M511.3 451.5 L511.2 452.8 L510.9 452.8 L510.7 452.6 L510.7 452.1 L510.8 451.3 L511.3 451.5 Z M511.9 448.3 L511.5 449.1 L510.5 448.2 L509.5 447.5 L509.1 446.9 L508.4 446.6 L508.2 445.8 L509.0 445.5 L509.4 445.5 L510.2 446.4 L511.5 446.5 L511.4 447.1 L511.8 447.8 L511.9 448.3 Z M515.2 450.2 L514.8 451.0 L514.0 450.9 L512.7 450.1 L512.2 449.7 L512.0 449.3 L512.5 449.3 L513.2 449.7 L514.8 449.9 L515.2 450.2 Z M508.5 458.5 L508.3 458.5 L507.9 458.0 L507.9 457.5 L508.0 457.3 L508.4 457.2 L509.0 458.1 L508.5 458.5 Z M525.8 442.7 L524.6 443.4 L523.2 442.4 L523.0 442.1 L524.0 441.7 L524.5 441.1 L524.1 440.3 L522.7 439.2 L522.6 438.4 L524.7 438.1 L526.0 438.8 L526.6 438.8 L526.3 439.5 L526.5 439.7 L526.5 441.7 L526.0 442.0 L525.9 442.5 L525.8 442.7 Z M529.7 429.2 L529.5 429.9 L531.2 431.1 L531.8 431.9 L532.1 432.6 L531.9 432.8 L531.3 432.4 L530.7 432.3 L530.9 432.8 L531.5 433.3 L530.5 433.6 L529.5 433.5 L526.6 432.9 L525.9 432.2 L527.7 431.2 L528.0 430.8 L526.8 430.9 L525.5 432.1 L523.4 431.5 L522.8 431.0 L522.6 430.8 L523.4 429.7 L524.9 429.8 L525.7 429.5 L526.6 429.2 L526.7 428.7 L528.9 428.6 L529.7 429.2 Z M520.6 415.9 L519.2 416.2 L517.6 415.2 L519.1 414.8 L519.8 415.1 L520.4 415.4 L520.6 415.9 Z M517.5 421.3 L517.0 421.7 L516.7 422.4 L516.5 423.4 L515.8 423.4 L515.3 423.2 L515.2 422.8 L515.1 422.4 L514.8 422.4 L514.6 422.9 L514.3 423.1 L513.6 423.2 L512.8 422.9 L512.8 422.2 L512.7 421.4 L512.7 421.1 L514.9 421.0 L515.6 421.6 L516.4 421.3 L516.7 420.9 L517.6 420.6 L517.5 421.3 Z M517.1 452.4 L515.9 452.5 L515.9 451.6 L516.4 451.3 L517.8 451.8 L517.8 452.1 L517.1 452.4 Z M506.0 456.0 L505.5 456.2 L504.8 455.9 L505.0 455.3 L505.5 455.0 L506.1 455.2 L506.2 455.5 L506.0 456.0 Z M547.7 470.5 L546.8 470.8 L546.5 470.8 L546.1 470.2 L546.7 468.8 L546.2 468.0 L546.1 467.6 L546.9 467.1 L547.4 466.3 L548.6 465.5 L551.9 464.5 L552.6 464.4 L552.6 465.2 L551.5 467.1 L550.6 468.1 L550.8 468.9 L549.3 469.1 L547.7 470.5 Z M497.6 475.3 L498.4 475.4 L499.6 475.4 L499.9 475.3 L500.6 474.6 L501.5 474.6 L501.9 475.3 L501.0 475.6 L500.8 475.8 L501.0 476.0 L501.7 476.3 L502.6 476.1 L502.7 476.7 L502.9 477.2 L503.4 477.4 L503.9 477.5 L505.0 477.4 L506.1 477.2 L507.3 476.9 L508.5 476.7 L512.0 476.9 L513.3 477.6 L515.7 477.7 L518.0 478.1 L519.2 477.9 L521.2 477.6 L521.5 477.9 L521.2 479.6 L521.4 480.1 L521.9 480.4 L522.5 480.2 L523.2 479.7 L524.9 479.2 L526.7 479.2 L528.2 478.1 L528.6 478.0 L528.3 478.6 L528.1 479.9 L527.8 480.7 L527.6 481.3 L526.7 481.6 L525.2 481.7 L522.4 481.5 L519.7 481.8 L514.6 482.3 L509.5 482.6 L508.8 482.4 L508.8 481.7 L508.7 481.1 L508.3 480.8 L506.8 480.4 L505.3 479.9 L499.4 479.1 L498.0 478.9 L495.7 479.0 L494.9 479.0 L494.3 478.7 L493.9 478.3 L493.7 476.8 L494.0 475.3 L494.5 475.0 L494.7 475.4 L495.3 475.6 L495.9 475.2 L495.8 474.5 L496.1 473.9 L496.5 474.1 L496.8 475.1 L497.6 475.3 Z M528.6 400.2 L530.4 400.8 L531.4 401.5 L532.2 402.7 L532.1 404.6 L528.7 406.0 L528.7 407.7 L529.0 408.5 L528.7 409.5 L526.8 411.0 L525.4 412.1 L524.7 411.7 L518.2 410.3 L515.1 409.7 L512.1 409.3 L508.0 410.5 L505.4 409.5 L502.4 411.5 L498.8 412.0 L496.2 412.8 L497.9 414.4 L497.8 416.0 L499.8 416.1 L503.1 418.1 L502.4 418.4 L500.1 417.4 L497.2 416.6 L495.9 417.6 L498.4 419.2 L499.4 420.8 L498.8 421.5 L495.2 418.3 L491.7 418.4 L492.7 420.2 L495.1 421.9 L491.8 421.2 L490.8 418.4 L485.6 416.2 L485.5 414.7 L484.5 414.0 L482.2 415.0 L482.4 416.6 L481.4 419.6 L484.8 423.5 L486.6 426.4 L489.8 428.9 L491.0 431.1 L488.8 432.0 L489.0 430.7 L486.8 429.2 L484.8 430.1 L486.1 431.9 L487.7 432.8 L484.4 434.4 L481.8 434.6 L482.3 435.0 L484.0 435.6 L488.6 437.3 L491.5 439.0 L495.5 441.1 L499.0 442.0 L499.7 443.7 L500.2 447.6 L500.1 448.9 L499.1 449.3 L496.1 446.8 L493.6 445.0 L492.1 445.5 L488.0 446.4 L487.3 446.9 L488.7 447.9 L489.3 450.0 L491.2 450.3 L492.0 450.9 L493.0 451.9 L490.0 452.9 L488.9 453.5 L488.1 452.2 L486.1 451.2 L484.0 450.4 L483.9 452.8 L486.8 457.3 L487.8 460.3 L488.3 463.0 L488.2 464.2 L486.6 463.3 L484.1 460.1 L481.9 460.2 L480.4 464.3 L479.0 463.4 L479.0 461.2 L476.4 458.7 L475.3 457.2 L473.7 457.7 L473.5 459.9 L471.0 459.2 L469.0 455.1 L470.2 452.8 L466.9 449.8 L465.3 448.1 L463.4 447.1 L463.5 446.4 L466.8 443.0 L468.6 443.4 L471.1 442.0 L473.7 441.5 L481.3 444.0 L484.3 445.6 L485.9 445.9 L485.5 444.8 L488.4 444.5 L489.2 443.8 L488.0 443.0 L486.8 442.8 L484.8 442.5 L483.8 441.9 L479.6 440.0 L478.3 441.0 L473.8 440.4 L470.7 441.1 L468.9 441.3 L466.6 440.4 L465.9 439.5 L465.5 440.8 L463.1 440.7 L461.6 437.4 L458.9 435.6 L458.9 434.1 L462.6 434.6 L463.6 434.2 L463.2 432.9 L462.1 432.9 L458.9 433.1 L457.8 432.4 L455.0 430.1 L451.5 426.6 L449.2 424.6 L449.9 424.7 L451.7 425.3 L452.6 424.7 L452.8 423.7 L453.7 423.6 L453.9 423.0 L453.1 421.7 L453.4 421.2 L454.3 420.5 L455.8 420.2 L457.4 419.6 L457.9 418.1 L458.6 417.0 L459.3 415.7 L461.1 415.1 L462.1 413.5 L461.6 412.3 L461.3 410.7 L463.6 410.6 L466.8 410.0 L469.0 410.5 L471.5 409.5 L474.2 407.3 L476.6 407.0 L479.3 407.4 L481.9 407.2 L483.8 405.1 L485.1 404.8 L487.2 405.0 L489.9 404.2 L492.3 404.1 L494.8 404.2 L497.9 403.4 L499.6 403.3 L500.1 402.5 L503.1 402.5 L505.6 402.2 L506.6 403.2 L507.6 403.8 L509.4 404.4 L511.9 404.5 L515.2 405.9 L518.6 405.3 L521.1 405.1 L523.6 405.1 L526.3 404.2 L526.4 402.6 L525.5 401.1 L525.6 400.3 L527.1 399.9 L528.6 400.2 Z"><title>Greece</title></path>
              <path class="map-region" d="M475.9 318.9 L477.2 318.8 L477.7 319.4 L478.0 319.8 L478.7 320.7 L480.8 321.3 L482.8 322.5 L483.1 322.5 L484.1 322.7 L485.1 323.5 L485.0 324.3 L485.0 324.8 L481.9 326.7 L480.5 326.6 L478.7 327.0 L477.4 327.5 L475.7 329.0 L474.3 329.8 L473.7 331.5 L472.6 332.3 L470.8 334.9 L469.9 335.9 L469.1 337.5 L467.7 339.0 L466.9 340.3 L465.7 340.7 L464.9 342.2 L465.0 343.1 L463.9 343.8 L463.2 344.7 L459.7 345.0 L458.4 345.5 L458.0 346.0 L456.9 346.5 L452.7 346.5 L451.8 346.6 L448.3 346.2 L445.7 346.3 L443.2 346.2 L441.9 347.3 L440.7 347.8 L439.2 348.3 L437.7 347.9 L437.2 348.3 L435.7 349.0 L435.3 349.0 L433.1 349.4 L431.1 350.4 L429.5 351.0 L427.7 351.0 L423.5 350.9 L420.3 350.2 L419.1 349.2 L416.5 348.7 L414.5 347.2 L411.8 345.9 L409.8 344.0 L406.0 342.2 L405.2 341.8 L403.6 340.4 L403.5 339.6 L402.9 338.6 L402.4 337.7 L402.0 336.3 L404.2 336.0 L404.7 335.7 L405.0 334.9 L404.9 334.3 L404.1 333.3 L404.7 332.7 L404.4 331.1 L406.1 330.8 L406.9 330.2 L406.9 328.6 L404.2 327.8 L405.4 327.2 L406.3 326.9 L408.3 327.6 L409.2 327.5 L411.1 327.5 L412.0 326.7 L411.8 325.8 L412.4 325.0 L413.3 323.7 L414.9 323.8 L415.4 323.9 L419.4 326.1 L423.3 326.7 L430.0 326.5 L433.3 326.2 L433.4 325.1 L434.0 323.8 L439.9 322.9 L442.8 321.8 L444.4 321.1 L446.8 321.9 L448.5 322.0 L453.3 320.2 L455.3 317.4 L460.0 317.2 L462.6 317.7 L466.5 317.1 L468.1 317.5 L469.3 318.2 L469.9 318.9 L470.8 319.6 L475.7 319.0 L475.9 318.9 Z"><title>Hungary</title></path>
              <path class="map-region" d="M72.7 251.9 L72.6 252.3 L71.7 251.8 L71.2 251.4 L68.7 251.2 L69.7 250.7 L70.2 250.8 L72.0 250.8 L72.6 251.0 L72.7 251.9 Z M107.0 237.6 L104.7 238.7 L104.0 240.2 L102.8 241.5 L101.0 242.0 L99.7 242.1 L98.3 242.4 L98.6 242.8 L100.3 243.4 L99.7 243.9 L95.6 245.1 L95.7 245.8 L98.6 247.4 L101.2 248.6 L102.9 249.3 L105.2 249.4 L105.9 249.0 L107.8 248.0 L107.2 247.2 L109.1 245.9 L110.5 246.3 L111.4 247.3 L112.2 248.3 L113.9 248.6 L113.9 249.9 L115.4 250.2 L117.2 250.1 L118.5 249.7 L120.1 250.2 L119.4 250.8 L117.9 251.0 L118.2 252.3 L119.4 254.0 L120.5 256.0 L120.5 257.4 L120.4 258.6 L121.4 261.0 L121.9 263.9 L120.6 265.4 L119.8 267.1 L117.9 270.3 L116.5 271.0 L116.8 272.7 L113.5 272.6 L111.5 273.0 L110.8 273.1 L109.7 273.2 L107.0 273.4 L103.1 274.0 L102.3 275.0 L101.4 275.4 L98.7 276.0 L96.4 277.3 L94.3 277.0 L93.5 276.5 L92.5 276.7 L92.9 277.7 L92.0 278.7 L89.7 279.4 L86.9 280.2 L80.5 281.3 L78.8 280.9 L75.3 281.6 L75.6 280.0 L78.0 279.1 L73.3 279.5 L70.5 280.0 L72.9 278.5 L74.5 277.9 L77.0 276.7 L69.3 277.8 L67.7 277.6 L69.1 275.5 L71.4 274.7 L73.1 273.7 L68.9 273.7 L67.2 273.1 L69.3 271.9 L71.2 271.8 L72.8 272.3 L74.0 271.7 L73.2 270.3 L75.0 269.5 L77.2 268.4 L83.9 267.6 L85.5 266.5 L83.3 267.1 L79.6 267.7 L77.5 267.2 L76.8 267.6 L73.0 268.3 L78.1 265.7 L79.6 264.3 L78.8 263.7 L81.5 261.5 L83.8 261.2 L84.6 261.1 L84.1 260.2 L78.7 260.2 L77.6 260.0 L77.0 259.1 L75.8 259.0 L74.2 259.1 L74.6 258.2 L72.0 258.2 L70.8 257.6 L70.7 256.8 L71.2 256.1 L73.5 255.9 L73.8 255.3 L73.1 254.6 L75.2 253.5 L77.1 252.8 L75.2 252.2 L73.3 251.6 L73.9 250.3 L72.8 250.0 L72.3 248.6 L70.9 248.3 L72.1 247.5 L74.2 247.6 L77.5 247.1 L82.7 248.3 L84.1 247.5 L87.8 247.7 L90.3 248.0 L89.3 246.7 L91.2 245.5 L93.5 245.0 L94.7 243.8 L91.4 243.5 L88.2 242.0 L90.4 241.4 L91.2 240.8 L92.0 239.2 L93.0 238.0 L93.7 236.9 L97.1 236.4 L99.6 236.3 L100.1 235.7 L101.8 235.8 L102.5 236.6 L102.4 237.7 L102.3 238.4 L102.4 238.8 L103.6 237.6 L103.0 236.4 L104.0 235.3 L105.1 234.3 L106.6 234.4 L109.0 235.5 L109.0 236.6 L107.0 237.6 L107.0 237.6 Z"><title>Ireland</title></path>
              <path class="map-region" d="M286.0 349.0 L287.3 349.6 L291.4 348.8 L293.2 348.5 L296.4 348.8 L298.5 347.5 L299.9 345.8 L299.5 344.8 L302.0 343.2 L303.6 342.7 L303.9 343.2 L304.0 345.1 L306.4 346.8 L308.7 347.4 L309.4 349.1 L310.3 350.2 L311.4 349.6 L310.8 348.3 L311.1 347.5 L313.4 345.5 L314.1 343.4 L314.7 342.1 L316.2 342.3 L316.9 343.9 L318.1 344.5 L320.8 343.9 L322.7 343.7 L323.9 345.2 L325.0 345.2 L325.1 344.6 L324.5 343.0 L323.9 342.3 L324.5 340.8 L325.9 340.6 L328.0 341.5 L329.0 341.0 L328.4 340.0 L329.1 337.6 L330.7 337.8 L333.0 338.5 L335.1 338.8 L336.3 338.4 L337.7 336.7 L341.4 336.2 L343.9 336.0 L345.8 336.1 L350.7 335.0 L351.1 335.2 L350.2 336.2 L351.9 338.0 L353.5 339.6 L356.1 340.2 L358.7 340.5 L365.6 341.3 L369.9 341.8 L369.2 342.7 L367.2 343.6 L365.9 344.9 L366.4 345.5 L367.3 345.5 L369.1 346.0 L368.9 346.5 L367.3 347.6 L367.3 348.3 L368.7 348.4 L368.3 350.1 L369.5 350.7 L371.6 352.0 L371.8 353.1 L370.2 353.1 L369.0 350.9 L367.0 351.7 L363.1 351.2 L361.5 352.5 L358.1 353.7 L354.8 354.7 L355.3 353.7 L353.0 354.3 L351.7 355.8 L352.2 357.8 L355.2 360.7 L354.4 362.2 L352.6 362.3 L351.7 363.7 L353.6 369.7 L357.3 372.5 L364.9 376.3 L368.2 377.7 L371.3 382.4 L373.8 388.4 L380.5 393.8 L388.4 397.6 L398.4 397.5 L400.9 398.0 L400.8 399.7 L397.8 401.4 L399.0 403.6 L412.7 408.2 L417.4 410.8 L424.5 414.2 L429.8 418.4 L429.3 421.2 L428.3 423.2 L425.0 421.8 L417.4 417.2 L414.7 416.2 L414.1 415.2 L411.8 414.8 L409.0 417.1 L405.5 422.8 L406.4 425.5 L411.4 427.4 L413.0 431.6 L412.7 434.2 L408.4 434.6 L405.9 436.7 L405.7 440.4 L400.7 444.3 L399.6 446.1 L394.4 445.0 L395.1 442.2 L397.7 439.5 L397.9 437.2 L399.7 436.4 L401.5 433.9 L399.8 431.5 L397.0 425.6 L395.0 421.2 L391.2 420.4 L385.7 418.2 L385.4 417.3 L385.6 415.4 L384.3 413.4 L381.4 413.2 L379.5 413.4 L378.0 413.8 L379.1 411.8 L375.6 411.1 L374.7 411.4 L374.3 410.5 L370.4 406.0 L368.1 406.1 L364.2 405.4 L362.3 405.9 L361.4 405.3 L356.5 403.2 L349.5 397.5 L344.0 393.3 L339.7 391.6 L338.4 392.0 L337.3 391.7 L338.3 391.2 L335.2 387.8 L333.0 386.5 L332.3 385.4 L330.8 385.2 L329.9 383.8 L330.0 382.1 L327.5 378.4 L325.8 373.1 L320.0 371.2 L313.3 368.5 L307.9 367.3 L302.0 370.8 L298.3 373.9 L291.9 375.3 L291.8 374.1 L293.1 372.9 L294.2 371.4 L293.7 370.4 L290.4 370.9 L287.6 370.0 L284.5 368.4 L284.4 367.2 L283.7 366.2 L284.9 364.8 L285.8 364.1 L285.6 362.4 L285.0 362.0 L283.2 361.7 L282.3 360.6 L281.1 359.5 L281.8 358.5 L283.7 358.6 L286.1 357.6 L287.2 356.0 L287.6 355.4 L285.9 354.2 L284.2 352.1 L283.1 351.3 L283.3 350.4 L286.0 349.0 L286.0 349.0 Z M328.4 386.3 L328.8 386.8 L328.9 387.1 L328.6 387.4 L328.7 388.1 L327.6 387.5 L326.1 387.8 L325.1 387.7 L324.8 387.2 L325.0 386.9 L326.5 386.8 L327.0 386.7 L327.9 386.8 L328.4 386.3 Z M372.9 412.5 L372.4 412.6 L372.1 412.4 L371.9 412.3 L372.1 411.8 L373.2 412.1 L373.2 412.3 L372.9 412.5 Z M349.2 460.5 L348.6 460.6 L347.8 460.2 L347.8 459.6 L347.9 459.4 L348.9 459.7 L349.2 460.3 L349.2 460.5 Z M393.5 442.7 L392.7 444.1 L392.3 444.6 L389.2 448.0 L388.9 448.8 L388.7 449.6 L388.4 450.4 L387.9 451.1 L387.5 452.0 L387.6 453.0 L387.8 453.5 L388.1 453.8 L388.7 454.1 L389.2 454.6 L388.5 455.0 L389.3 455.8 L389.9 456.4 L390.0 456.9 L390.0 457.4 L388.6 458.3 L388.1 458.9 L387.7 459.5 L387.6 460.1 L387.7 460.7 L387.7 461.3 L386.3 461.3 L384.9 460.9 L383.5 461.1 L381.4 460.4 L380.7 460.2 L380.0 460.0 L378.3 457.9 L377.0 457.0 L375.5 456.3 L374.0 456.2 L372.5 456.3 L371.2 455.9 L368.5 454.4 L365.7 453.3 L364.5 452.5 L363.9 452.0 L363.3 451.7 L361.6 451.4 L360.2 450.6 L359.5 450.5 L358.1 450.6 L357.4 450.6 L356.6 450.3 L355.2 449.4 L354.3 448.1 L354.0 447.6 L354.7 446.1 L355.5 444.7 L356.1 444.3 L356.9 444.1 L357.4 443.7 L357.8 443.2 L359.3 444.6 L359.9 445.0 L360.6 444.9 L361.8 444.4 L361.9 443.8 L363.2 443.1 L364.8 443.0 L365.6 443.2 L366.0 443.8 L366.6 444.0 L367.3 444.1 L369.7 445.4 L370.4 445.6 L371.1 445.6 L372.9 445.1 L374.3 444.9 L377.3 445.2 L378.9 444.9 L380.1 444.8 L381.7 444.3 L383.0 443.5 L383.6 443.3 L384.3 443.3 L386.1 443.3 L387.8 443.5 L388.5 443.3 L389.1 442.8 L389.8 442.6 L390.6 442.7 L392.6 441.8 L393.4 441.8 L394.3 442.1 L393.5 442.7 Z M318.8 410.3 L319.4 411.1 L320.8 414.3 L321.0 415.0 L320.7 415.7 L320.3 416.2 L318.9 417.8 L319.1 419.1 L319.7 419.9 L319.7 420.9 L319.5 422.0 L318.6 428.9 L318.2 430.1 L317.9 431.2 L317.0 431.5 L315.7 431.2 L314.2 430.6 L313.5 430.6 L312.7 430.8 L312.1 430.7 L311.6 430.3 L311.1 432.7 L310.4 433.7 L309.4 434.3 L308.4 434.3 L307.3 434.1 L306.4 434.1 L305.8 433.7 L305.2 432.9 L304.4 431.9 L303.5 430.7 L303.4 429.7 L303.3 427.4 L303.5 426.9 L303.9 426.4 L304.1 425.3 L304.0 424.4 L304.2 424.1 L304.7 424.4 L305.1 424.3 L305.1 423.9 L305.2 423.0 L304.5 422.3 L303.4 422.1 L303.3 421.3 L303.4 420.6 L304.0 420.1 L304.2 419.5 L304.2 417.5 L303.4 416.8 L303.1 415.7 L302.7 415.0 L302.0 414.3 L301.2 413.7 L300.7 413.1 L300.6 411.7 L300.8 410.5 L301.1 410.0 L301.4 410.0 L302.2 410.6 L302.9 410.8 L304.2 410.9 L305.5 410.7 L307.1 410.2 L308.6 409.5 L310.8 407.6 L312.2 407.2 L312.9 406.7 L313.1 406.0 L313.7 405.8 L314.4 406.5 L315.3 406.5 L316.6 407.1 L317.1 407.6 L317.6 408.3 L318.1 408.5 L318.6 408.7 L318.7 408.8 L318.3 409.0 L317.8 409.7 L318.1 409.9 L318.8 410.3 Z M304.3 432.4 L303.6 433.6 L302.8 432.8 L302.8 432.0 L302.9 431.8 L303.8 432.1 L304.3 432.4 Z M301.9 408.4 L301.5 409.0 L300.9 408.9 L301.1 408.5 L301.6 407.7 L302.3 407.4 L302.6 407.7 L302.3 408.1 L301.9 408.4 Z"><title>Italy</title></path>
              <path class="map-region" d="M532.0 230.6 L529.6 230.2 L527.2 228.9 L524.6 227.3 L520.3 225.3 L514.6 224.4 L511.3 222.6 L510.0 221.6 L508.2 221.9 L505.4 223.1 L500.9 223.4 L497.1 222.6 L494.6 222.5 L488.4 222.6 L486.5 221.9 L484.0 222.0 L478.9 221.8 L474.8 221.7 L469.9 222.7 L462.3 225.7 L462.1 218.8 L465.0 215.2 L466.8 212.8 L467.5 210.5 L473.6 207.1 L481.3 205.6 L482.4 207.2 L488.6 210.5 L495.0 214.8 L500.1 213.6 L504.2 211.4 L504.0 206.6 L503.5 203.8 L505.2 203.4 L510.0 202.4 L513.4 201.5 L514.9 202.3 L515.4 202.1 L515.6 201.7 L519.2 203.0 L521.1 203.3 L524.5 204.2 L525.0 204.9 L528.3 207.1 L531.3 208.0 L535.9 207.0 L537.6 207.4 L541.2 208.0 L543.0 208.0 L543.9 209.2 L547.2 210.6 L547.7 211.4 L547.4 212.4 L546.2 213.8 L545.2 216.3 L547.3 216.0 L548.2 216.6 L549.0 218.0 L549.8 219.3 L551.1 220.4 L552.1 222.7 L551.9 224.3 L551.2 224.8 L548.4 225.6 L545.2 227.6 L544.4 229.0 L542.5 228.9 L537.8 228.6 L534.9 230.1 L532.4 230.5 L532.0 230.6 Z"><title>Latvia</title></path>
              <path class="map-region" d="M461.2 235.3 L460.5 235.2 L461.9 233.8 L462.4 232.9 L462.8 231.6 L463.2 231.2 L463.2 231.8 L463.0 232.8 L462.1 234.5 L461.2 235.3 Z M483.9 246.5 L482.8 244.9 L483.2 243.2 L484.7 240.3 L482.2 239.1 L478.6 237.9 L475.2 238.0 L470.3 236.8 L467.3 235.9 L465.5 235.5 L464.7 235.4 L464.7 233.2 L462.5 228.8 L462.3 225.7 L469.9 222.7 L474.8 221.7 L478.9 221.8 L484.0 222.0 L486.5 221.9 L488.4 222.6 L494.6 222.5 L497.1 222.6 L500.9 223.4 L505.4 223.1 L508.2 221.9 L510.0 221.6 L511.3 222.6 L514.6 224.4 L520.3 225.3 L524.6 227.3 L527.2 228.9 L529.6 230.2 L532.0 230.6 L531.7 232.1 L530.5 234.2 L530.8 234.9 L534.1 235.2 L533.8 235.7 L532.7 236.2 L528.2 237.0 L527.5 237.6 L526.8 238.7 L524.1 239.4 L521.8 240.8 L521.1 243.2 L521.1 244.0 L519.8 245.3 L518.9 246.8 L519.8 247.1 L521.4 247.7 L521.6 248.7 L520.6 249.2 L518.4 248.9 L518.6 248.3 L517.8 247.3 L515.6 247.8 L513.4 249.0 L510.4 249.1 L509.4 250.9 L507.2 251.1 L503.4 252.2 L501.8 251.5 L499.5 251.7 L497.8 251.7 L493.9 251.9 L492.9 251.4 L492.9 249.9 L491.5 248.4 L489.0 247.5 L487.4 247.2 L487.1 246.6 L485.5 246.1 L483.9 246.5 L483.9 246.5 Z"><title>Lithuania</title></path>
              <path class="map-region" d="M274.6 298.0 L274.5 298.4 L274.5 299.1 L274.9 299.8 L275.7 300.5 L276.4 301.1 L277.2 301.5 L278.7 301.9 L279.3 302.0 L279.3 302.5 L279.2 303.1 L278.7 303.4 L278.3 303.8 L277.9 304.4 L277.5 305.4 L277.5 306.2 L276.6 305.9 L276.2 305.7 L275.4 305.6 L274.7 305.8 L274.1 306.1 L273.3 306.2 L272.6 306.1 L272.2 305.9 L271.9 305.7 L270.9 305.5 L270.5 305.1 L270.8 304.9 L271.1 304.6 L271.3 304.2 L271.6 303.8 L270.7 302.8 L270.5 302.4 L269.7 301.8 L269.7 301.5 L269.9 301.2 L269.8 301.0 L269.9 300.5 L270.5 300.0 L270.8 299.4 L271.5 298.5 L272.8 297.5 L273.8 297.6 L274.3 297.6 L274.5 298.0 L274.6 298.0 Z"><title>Luxembourg</title></path>
              <path class="map-region" d="M380.8 471.5 L380.4 471.9 L379.2 471.9 L378.1 471.2 L378.1 470.0 L379.4 470.2 L380.5 471.1 L380.8 471.5 Z M377.7 469.4 L376.9 469.5 L376.2 469.2 L376.0 469.0 L377.0 468.8 L377.5 468.9 L377.7 469.2 L377.7 469.4 Z"><title>Malta</title></path>
              <path class="map-region" d="M532.4 320.7 L535.2 319.1 L537.2 319.3 L541.4 318.6 L542.9 318.4 L544.2 318.1 L546.1 318.4 L548.3 319.4 L550.2 319.9 L550.8 320.7 L553.4 320.9 L553.8 321.9 L554.6 321.8 L555.3 322.5 L556.4 322.0 L559.4 322.4 L561.3 324.4 L562.7 324.4 L563.9 324.2 L564.9 326.6 L564.6 328.0 L563.8 329.5 L564.3 330.4 L566.5 331.4 L568.0 332.4 L569.1 332.7 L569.1 333.7 L568.8 334.9 L569.4 336.0 L569.8 336.7 L573.3 338.1 L574.1 339.3 L573.9 341.6 L576.2 343.2 L573.3 343.8 L571.7 342.8 L570.6 343.1 L569.3 343.2 L568.1 342.6 L567.2 342.8 L566.1 342.5 L565.1 343.5 L564.8 342.0 L564.1 341.7 L561.8 342.6 L561.4 343.7 L562.4 346.0 L561.6 347.5 L559.0 348.9 L558.1 350.6 L555.9 352.2 L556.2 353.3 L556.0 354.0 L553.6 354.2 L552.4 354.8 L551.1 353.4 L550.8 352.8 L551.7 352.4 L551.4 350.7 L551.1 349.6 L551.2 346.4 L552.8 342.6 L552.7 340.3 L551.6 338.5 L549.4 335.4 L547.2 333.9 L545.9 332.5 L543.6 330.2 L542.8 329.3 L540.6 327.2 L540.0 325.7 L538.2 323.2 L536.9 321.9 L534.5 320.7 L532.4 320.7 L532.4 320.7 Z"><title>Moldova</title></path>
              <path class="map-region" d="M439.0 378.1 L439.0 378.7 L440.3 379.6 L443.5 382.0 L445.0 382.6 L447.4 383.4 L451.3 385.0 L453.4 385.9 L453.5 386.7 L451.6 387.6 L449.8 387.5 L450.0 388.4 L450.0 390.0 L449.7 390.1 L447.4 390.8 L446.1 390.7 L445.9 389.4 L445.4 388.9 L444.1 389.9 L442.4 391.7 L440.7 393.7 L440.7 395.2 L441.0 396.5 L440.9 397.7 L438.9 397.4 L435.2 393.7 L431.8 391.9 L432.1 391.4 L431.0 391.5 L430.0 390.9 L429.5 389.9 L430.0 389.7 L430.9 389.0 L429.9 387.3 L429.6 385.0 L430.1 384.4 L431.8 383.1 L432.3 382.2 L433.4 381.2 L435.3 380.4 L436.3 381.1 L437.0 380.3 L435.8 378.6 L436.2 378.0 L437.6 378.3 L438.6 378.1 L439.0 378.1 Z"><title>Montenegro</title></path>
              <path class="map-region" d="M273.1 290.4 L270.6 290.3 L269.3 290.1 L269.0 289.7 L268.7 289.0 L270.0 288.0 L270.0 287.5 L271.0 285.8 L270.0 285.3 L267.4 284.4 L266.6 283.9 L264.5 284.2 L261.8 283.1 L261.3 281.8 L260.5 281.9 L258.7 282.4 L258.3 282.1 L257.9 281.5 L256.0 282.2 L254.7 281.9 L253.5 281.8 L253.1 282.9 L251.8 283.0 L249.7 282.5 L245.8 282.4 L242.8 281.8 L241.1 280.8 L242.3 280.2 L246.6 280.4 L250.6 281.8 L251.0 281.2 L249.0 280.7 L250.3 279.9 L249.7 279.2 L247.7 277.0 L249.1 275.3 L250.6 274.5 L254.1 271.4 L256.5 265.4 L257.7 263.8 L259.2 264.2 L265.1 261.9 L267.3 259.8 L273.9 258.1 L280.2 257.8 L284.6 258.5 L286.4 259.4 L288.1 260.8 L288.0 263.4 L286.4 266.1 L285.9 267.5 L282.1 267.7 L282.2 268.2 L281.8 268.8 L282.6 269.6 L284.7 269.8 L285.7 270.1 L286.1 271.2 L285.4 272.7 L283.2 273.8 L282.3 274.2 L282.1 274.8 L283.2 275.6 L282.5 276.3 L278.5 276.9 L277.6 277.3 L275.2 276.6 L274.3 277.0 L272.5 277.6 L273.8 279.3 L274.3 280.1 L275.6 281.4 L275.6 282.4 L274.1 284.6 L274.2 285.2 L274.9 285.3 L272.7 286.7 L271.5 286.8 L271.5 287.3 L272.6 287.7 L273.8 288.5 L273.1 290.4 Z M250.8 282.7 L250.7 283.1 L250.2 283.6 L248.5 284.3 L246.8 284.8 L245.9 284.8 L245.3 284.5 L244.9 284.3 L244.0 284.0 L242.7 283.9 L241.9 284.1 L241.4 284.4 L240.9 284.4 L240.5 284.1 L240.2 283.8 L239.8 282.8 L240.8 282.6 L242.8 282.5 L244.4 282.9 L246.5 283.0 L248.1 282.5 L249.4 283.0 L250.8 282.7 Z M277.3 256.8 L275.6 257.2 L275.1 257.2 L275.3 257.0 L276.8 256.8 L277.3 256.8 Z M272.3 257.5 L269.8 257.7 L268.9 257.5 L268.8 257.4 L269.5 257.3 L271.6 257.3 L272.2 257.4 L272.3 257.5 Z M261.9 259.3 L259.6 260.2 L259.4 260.0 L260.9 259.3 L261.9 259.3 Z M264.7 258.3 L263.5 258.4 L263.0 258.3 L265.8 257.8 L267.6 257.6 L267.9 257.7 L264.7 258.3 Z M259.1 262.2 L257.9 263.0 L257.1 262.8 L256.9 262.6 L257.3 261.9 L259.1 260.8 L259.1 262.2 Z M247.4 278.4 L248.6 279.0 L248.8 279.2 L248.9 279.5 L247.4 279.7 L245.7 278.9 L244.6 279.1 L244.2 278.7 L244.2 278.5 L245.3 278.3 L247.4 278.4 Z M282.4 256.0 L281.2 256.0 L281.5 255.7 L282.6 255.4 L283.2 255.4 L282.4 256.0 Z"><title>Netherlands</title></path>
              <path class="map-region" d="M468.8 393.7 L469.5 393.8 L471.0 393.5 L472.0 393.1 L472.4 393.0 L473.1 392.8 L474.0 392.9 L474.9 393.1 L476.1 392.8 L477.3 392.4 L477.8 392.5 L478.3 392.8 L478.6 392.9 L480.5 394.7 L481.6 395.5 L482.9 396.0 L484.3 396.4 L484.8 396.8 L485.7 398.8 L486.2 399.5 L486.8 399.7 L486.9 399.9 L486.9 400.2 L486.2 401.5 L486.0 404.6 L485.8 404.8 L485.1 404.8 L484.1 404.9 L483.8 405.1 L483.4 406.7 L481.9 407.2 L480.5 407.5 L479.3 407.4 L477.3 407.0 L476.6 407.0 L476.0 407.2 L474.2 407.3 L473.4 407.6 L471.5 409.5 L469.6 410.2 L469.0 410.5 L467.5 410.1 L466.8 410.0 L465.8 410.5 L463.6 410.6 L463.0 410.7 L461.3 410.7 L461.2 410.5 L460.9 410.1 L460.1 409.9 L458.5 410.1 L458.1 409.8 L457.4 408.2 L456.9 407.9 L456.3 407.4 L455.3 405.6 L455.3 404.8 L455.3 404.2 L454.8 402.6 L455.1 402.2 L455.6 401.9 L455.6 401.3 L455.5 400.3 L456.1 398.4 L456.3 398.3 L456.4 398.4 L457.9 398.5 L458.3 398.3 L458.5 397.9 L458.6 396.5 L458.9 395.9 L462.5 394.7 L463.5 394.6 L464.3 395.2 L464.9 395.5 L465.3 395.5 L465.5 395.2 L465.9 394.5 L466.6 394.1 L468.8 393.7 L468.8 393.7 Z"><title>North Macedonia</title></path>
              <path class="map-country" data-country="PL" d="M494.5 281.1 L495.4 282.6 L495.2 283.6 L497.7 285.8 L499.2 288.1 L500.8 289.2 L499.8 289.6 L499.2 290.0 L500.0 290.7 L500.6 293.1 L499.5 294.0 L495.8 294.9 L493.2 296.7 L490.2 298.6 L486.3 301.6 L483.2 304.3 L482.6 305.8 L483.5 308.1 L483.1 309.3 L483.8 310.0 L485.0 310.9 L484.5 311.4 L481.6 310.7 L480.2 310.7 L474.5 309.1 L473.9 308.0 L470.7 307.0 L466.1 306.5 L463.4 306.6 L461.7 307.5 L460.1 307.8 L458.3 307.2 L455.9 307.0 L454.5 306.9 L453.7 307.0 L452.1 307.6 L450.5 308.4 L448.1 309.0 L446.7 309.3 L446.2 308.8 L446.5 307.8 L445.7 306.9 L444.5 306.7 L444.0 306.2 L442.6 304.7 L441.4 304.8 L439.7 305.4 L436.2 306.8 L435.8 305.6 L434.4 305.1 L431.5 302.5 L431.3 301.4 L430.5 300.7 L427.8 300.6 L426.6 299.9 L425.1 299.4 L424.4 299.1 L423.8 299.5 L421.9 299.7 L420.8 298.8 L419.3 298.1 L418.8 297.6 L420.7 296.7 L420.3 295.8 L418.4 296.3 L416.6 296.4 L411.2 294.4 L409.8 294.5 L411.3 296.3 L410.1 297.1 L408.6 297.6 L407.4 298.3 L406.4 298.0 L403.3 295.3 L402.5 295.0 L401.5 294.4 L402.4 293.6 L403.6 293.2 L404.1 292.5 L403.4 292.0 L399.7 291.8 L398.5 291.8 L397.5 291.3 L395.5 290.5 L392.1 289.9 L390.7 289.6 L389.8 288.8 L387.9 287.4 L386.1 287.3 L386.1 288.7 L383.9 289.1 L385.2 287.2 L386.5 284.3 L385.5 282.1 L382.8 281.0 L383.0 279.7 L382.3 278.9 L381.3 277.2 L382.4 275.7 L383.1 274.3 L382.6 273.9 L382.6 272.7 L381.5 271.8 L380.7 270.8 L381.5 268.8 L376.9 265.7 L375.5 263.9 L377.4 262.7 L378.9 260.6 L378.9 259.6 L377.2 255.4 L377.0 254.2 L381.0 255.3 L380.7 254.4 L380.7 253.0 L376.4 252.5 L376.4 251.5 L378.5 251.8 L389.9 249.2 L399.4 247.6 L401.9 246.8 L403.6 245.6 L410.0 243.6 L414.7 242.0 L425.1 240.7 L430.7 241.5 L434.1 243.2 L430.3 241.9 L431.4 244.6 L434.5 246.4 L441.7 246.2 L444.2 245.3 L448.2 245.6 L457.5 245.9 L469.7 246.3 L483.5 246.6 L484.6 246.1 L486.6 246.4 L487.3 246.9 L488.0 247.2 L490.4 248.0 L492.6 249.1 L492.9 250.8 L493.0 251.6 L496.8 259.7 L498.0 262.7 L498.4 265.2 L498.2 266.6 L492.9 268.5 L490.7 270.0 L489.1 271.5 L489.3 272.1 L492.6 273.1 L494.4 273.9 L495.1 274.7 L494.5 276.7 L494.2 278.1 L493.6 279.8 L494.5 281.1 Z"><title>Poland</title></path>
              <path class="map-country" data-country="PT" d="M87.4 397.5 L89.7 396.1 L93.1 395.4 L94.5 395.1 L95.0 395.9 L95.5 396.5 L94.3 398.0 L95.0 398.9 L96.0 399.0 L98.1 398.2 L101.0 398.1 L102.0 398.5 L104.6 398.8 L107.1 398.0 L107.3 397.3 L107.9 397.0 L109.3 397.4 L111.8 397.2 L113.4 397.5 L115.1 397.8 L115.3 399.3 L115.5 400.7 L117.4 400.8 L119.2 401.6 L119.6 402.4 L118.6 403.4 L115.2 405.2 L112.5 407.6 L110.8 408.4 L111.5 410.4 L112.0 413.1 L111.8 415.2 L111.6 416.1 L112.1 416.9 L110.4 418.0 L109.3 419.0 L110.8 420.4 L110.8 421.8 L109.3 424.5 L108.2 424.9 L103.0 425.2 L104.1 426.7 L105.5 427.6 L107.5 431.6 L109.7 432.5 L109.1 434.4 L106.9 436.0 L106.1 437.5 L105.5 439.3 L108.4 443.2 L110.2 443.1 L109.4 444.8 L107.4 445.3 L105.0 448.0 L103.4 450.4 L103.8 452.3 L103.5 455.5 L97.9 457.5 L91.1 456.3 L87.9 456.6 L85.4 457.3 L85.5 455.5 L86.9 450.3 L86.8 446.9 L87.1 443.1 L86.1 439.9 L87.9 439.5 L86.3 439.2 L83.4 439.8 L81.9 439.9 L81.4 437.4 L83.4 436.9 L84.9 435.6 L85.3 433.2 L86.2 432.4 L83.4 435.2 L81.4 436.7 L79.4 436.8 L78.5 435.7 L79.1 433.7 L80.1 430.2 L79.9 429.1 L81.4 428.0 L84.5 423.2 L86.4 419.2 L86.2 417.9 L87.9 413.2 L88.7 409.9 L88.8 407.9 L87.9 405.4 L86.9 401.0 L86.5 400.3 L86.1 398.8 L87.4 397.5 Z"><title>Portugal</title></path>
              <path class="map-region" d="M552.4 354.8 L555.4 356.7 L559.6 357.4 L559.4 357.0 L559.5 356.5 L561.0 356.8 L565.1 355.4 L569.4 355.8 L571.2 357.1 L570.8 358.4 L569.9 361.3 L562.9 363.2 L563.2 361.9 L563.5 360.6 L561.4 360.7 L561.4 362.6 L560.4 363.7 L559.9 365.1 L560.9 365.5 L558.5 367.9 L558.0 372.6 L557.1 375.6 L554.4 375.5 L550.3 374.6 L548.3 372.6 L546.1 372.9 L544.2 372.2 L538.7 370.7 L535.2 370.7 L527.3 372.4 L522.3 375.3 L518.2 376.4 L509.6 375.6 L502.3 375.3 L493.6 374.2 L485.8 374.5 L485.1 373.7 L485.7 372.6 L487.2 371.9 L486.2 370.9 L483.1 369.6 L482.9 369.0 L481.6 368.3 L480.5 367.1 L481.3 365.9 L483.1 365.7 L483.3 365.1 L480.5 363.9 L476.8 365.6 L474.6 364.9 L471.0 364.2 L469.2 363.3 L466.2 362.4 L466.5 361.9 L468.3 361.7 L468.4 361.3 L466.9 360.8 L466.2 360.4 L466.4 360.0 L467.0 359.9 L467.6 359.0 L467.9 358.5 L467.1 357.9 L464.6 357.4 L463.0 356.7 L461.0 355.8 L459.1 354.6 L458.9 354.2 L459.0 353.8 L458.9 352.2 L458.9 351.2 L458.5 351.2 L458.1 351.3 L456.4 349.7 L454.6 348.8 L452.9 347.5 L452.7 346.5 L456.9 346.5 L458.0 346.0 L458.4 345.5 L459.7 345.0 L463.2 344.7 L463.9 343.8 L465.0 343.1 L464.9 342.2 L465.7 340.7 L466.9 340.3 L467.7 339.0 L469.1 337.5 L469.9 335.9 L470.8 334.9 L472.6 332.3 L473.7 331.5 L474.3 329.8 L475.7 329.0 L477.4 327.5 L478.7 327.0 L480.5 326.6 L481.9 326.7 L485.0 324.8 L485.8 324.3 L488.0 323.2 L489.4 322.8 L494.8 323.9 L495.4 323.9 L499.5 324.6 L500.2 324.5 L503.0 324.9 L505.5 324.5 L507.6 325.3 L510.7 327.2 L512.9 326.9 L517.8 324.9 L523.4 324.2 L527.5 323.0 L528.4 321.3 L531.8 320.8 L533.5 320.6 L535.9 321.3 L537.3 322.5 L539.1 324.3 L540.3 326.5 L541.4 328.2 L543.0 329.5 L544.9 331.8 L546.8 333.2 L547.9 334.6 L550.6 336.2 L552.3 339.5 L552.5 342.0 L552.2 343.9 L551.0 348.5 L551.2 350.3 L551.7 351.6 L551.4 352.6 L550.7 353.0 L551.8 354.0 L552.4 354.8 Z"><title>Romania</title></path>
              <path class="map-region" d="M466.2 362.4 L469.2 363.3 L471.0 364.2 L474.6 364.9 L476.8 365.6 L480.5 363.9 L483.3 365.1 L483.1 365.7 L481.3 365.9 L480.5 367.1 L481.6 368.3 L482.9 369.0 L483.1 369.6 L482.2 370.1 L481.8 371.5 L479.6 372.4 L478.9 374.1 L479.1 375.6 L479.8 376.5 L480.6 378.3 L483.0 379.8 L484.6 380.9 L486.6 382.3 L486.1 383.4 L485.1 384.4 L483.2 386.0 L480.9 386.2 L479.8 387.1 L480.1 388.1 L480.2 390.1 L481.0 390.9 L479.9 392.4 L478.6 392.9 L477.8 392.5 L476.1 392.8 L474.0 392.9 L472.4 393.0 L471.0 393.5 L468.8 393.7 L468.2 392.8 L469.4 392.0 L470.9 389.5 L471.2 388.6 L470.0 388.5 L466.8 386.6 L464.7 385.7 L463.3 384.1 L461.3 383.2 L459.8 382.5 L459.5 381.7 L458.7 381.5 L457.0 382.2 L457.2 383.0 L457.3 383.7 L455.1 385.2 L455.3 386.1 L453.5 386.7 L453.4 385.9 L451.3 385.0 L447.4 383.4 L445.0 382.6 L443.5 382.0 L440.3 379.6 L439.0 378.7 L439.0 378.1 L440.4 377.4 L441.6 377.7 L442.6 377.4 L442.7 376.0 L439.8 373.1 L439.9 372.6 L440.9 372.6 L443.5 372.6 L443.9 371.9 L442.0 370.6 L439.5 369.0 L438.2 368.4 L438.2 367.4 L438.5 366.0 L440.2 364.0 L441.1 362.0 L440.5 361.5 L438.2 361.5 L436.7 361.9 L436.7 361.3 L437.3 361.4 L437.8 360.6 L438.2 358.4 L438.3 357.9 L440.4 358.3 L441.6 358.0 L441.4 357.5 L440.7 357.0 L437.7 356.2 L436.7 354.6 L437.4 354.0 L436.0 353.5 L435.9 352.3 L434.5 350.1 L435.3 349.3 L435.7 349.0 L437.2 348.3 L437.7 347.9 L439.2 348.3 L440.7 347.8 L441.9 347.3 L443.2 346.2 L445.7 346.3 L448.3 346.2 L451.8 346.6 L452.9 347.5 L454.6 348.8 L456.4 349.7 L458.1 351.3 L458.5 351.2 L458.9 351.2 L458.9 352.2 L459.0 353.8 L458.9 354.2 L459.1 354.6 L461.0 355.8 L463.0 356.7 L464.6 357.4 L467.1 357.9 L467.9 358.5 L467.6 359.0 L467.0 359.9 L466.4 360.0 L466.2 360.4 L466.9 360.8 L468.4 361.3 L468.3 361.7 L466.5 361.9 L466.2 362.4 L466.2 362.4 Z"><title>Serbia</title></path>
              <path class="map-region" d="M481.1 310.8 L480.4 311.9 L479.2 313.2 L478.0 315.5 L475.9 318.9 L471.4 319.7 L470.2 319.2 L469.7 318.7 L468.8 317.8 L467.4 317.1 L464.2 317.6 L461.5 317.5 L457.2 317.1 L455.1 317.8 L450.8 321.1 L447.9 322.2 L445.5 321.4 L443.7 321.2 L442.4 322.5 L435.5 323.2 L433.4 324.6 L433.8 325.6 L433.1 326.4 L425.8 326.7 L421.0 326.6 L417.5 325.2 L415.2 323.9 L413.6 323.7 L412.5 323.3 L411.1 321.4 L409.7 318.5 L410.7 317.1 L410.8 316.5 L412.2 314.3 L413.8 313.4 L417.5 313.8 L421.0 313.0 L422.7 312.0 L423.3 311.5 L425.1 310.9 L425.4 309.5 L426.0 308.5 L428.8 307.2 L430.0 306.5 L431.5 305.7 L433.4 305.7 L434.5 305.5 L436.0 306.2 L438.4 306.8 L440.4 305.3 L442.1 304.4 L443.3 305.5 L444.4 306.5 L444.9 306.8 L446.3 307.1 L446.5 308.4 L446.1 309.2 L447.5 309.2 L449.9 309.5 L451.2 307.8 L452.9 307.2 L454.2 307.0 L455.1 306.9 L456.9 306.9 L459.2 307.7 L461.1 307.8 L462.7 306.6 L464.5 306.4 L469.8 306.7 L472.9 307.5 L474.3 308.7 L476.8 309.8 L481.1 310.8 L481.1 310.8 Z"><title>Slovakia</title></path>
              <path class="map-region" d="M405.3 342.1 L402.9 341.6 L402.1 342.0 L402.0 343.4 L400.2 343.5 L398.9 344.4 L396.9 345.0 L395.1 345.5 L393.9 346.0 L393.8 346.8 L394.8 348.3 L394.5 349.8 L392.0 350.6 L389.7 351.6 L390.8 352.4 L389.9 353.2 L390.4 354.2 L389.3 354.9 L385.7 354.2 L384.4 354.6 L382.9 354.1 L381.4 352.9 L380.9 352.3 L380.1 353.1 L378.4 354.4 L375.7 354.4 L373.6 354.1 L373.3 354.4 L372.2 355.1 L368.4 354.0 L370.2 353.1 L371.8 353.1 L371.6 352.0 L369.5 350.7 L368.3 350.1 L368.7 348.4 L367.3 348.3 L367.3 347.6 L368.9 346.5 L369.1 346.0 L367.3 345.5 L366.4 345.5 L365.9 344.9 L367.2 343.6 L369.2 342.7 L369.9 341.8 L371.6 341.9 L374.0 342.3 L377.1 342.8 L379.6 343.1 L380.6 343.3 L381.2 342.8 L383.2 342.1 L384.3 341.1 L385.6 340.7 L389.0 340.3 L393.1 340.2 L395.8 339.5 L398.3 339.9 L398.6 339.5 L399.3 337.9 L402.4 337.7 L402.9 338.6 L403.5 339.6 L403.6 340.4 L405.2 341.8 L405.3 342.1 Z"><title>Slovenia</title></path>
              <path class="map-country" data-country="ES" d="M217.8 437.2 L217.5 437.4 L216.6 437.2 L215.4 437.2 L215.3 436.7 L215.5 436.4 L215.8 436.0 L216.5 436.7 L217.7 436.8 L217.8 437.2 Z M237.3 423.6 L238.5 424.0 L239.7 423.7 L240.4 423.8 L241.1 424.0 L241.2 424.7 L240.6 425.6 L239.8 426.5 L239.1 427.4 L238.5 428.5 L237.4 429.2 L236.3 429.6 L234.2 428.7 L232.9 428.5 L232.5 428.2 L232.2 427.0 L231.7 426.6 L230.8 426.5 L230.1 426.8 L229.1 427.4 L228.6 426.8 L227.8 426.7 L227.5 426.3 L227.5 425.8 L232.7 422.8 L234.2 422.2 L237.4 421.4 L237.9 421.5 L237.5 422.0 L237.5 422.2 L237.9 422.4 L237.8 422.8 L237.4 423.1 L237.3 423.6 Z M251.7 423.0 L251.5 423.1 L247.6 421.7 L246.3 421.6 L246.0 421.4 L246.1 420.6 L246.2 420.3 L248.7 420.2 L250.8 420.7 L252.0 422.1 L252.0 422.3 L251.7 423.0 Z M215.9 434.2 L215.4 435.0 L213.5 434.7 L213.1 434.4 L213.5 433.5 L214.1 433.4 L214.1 432.8 L214.7 432.2 L217.4 431.7 L218.0 432.2 L218.1 432.7 L216.5 434.0 L215.9 434.2 Z M175.2 379.6 L175.7 380.7 L177.3 381.2 L179.2 381.3 L180.0 382.2 L179.4 383.3 L179.3 384.0 L180.2 384.2 L180.7 383.8 L181.4 383.4 L181.6 383.9 L186.0 385.2 L188.1 385.3 L190.3 387.0 L191.7 387.0 L193.5 386.7 L194.5 387.0 L196.0 387.6 L197.2 388.4 L200.9 388.3 L202.5 388.2 L205.7 388.4 L205.9 387.0 L206.5 386.5 L210.4 387.3 L212.9 388.1 L214.7 388.4 L215.5 390.1 L215.7 390.7 L215.9 391.4 L217.0 391.4 L218.8 390.7 L221.1 391.2 L222.2 392.0 L223.3 392.5 L225.4 391.6 L230.0 392.5 L231.1 392.4 L231.7 391.8 L233.1 391.5 L235.1 391.1 L237.3 391.5 L238.4 392.3 L239.3 393.2 L237.5 393.6 L237.6 395.1 L238.4 395.8 L237.3 398.4 L226.8 403.2 L223.9 405.4 L212.9 407.7 L208.0 410.2 L207.7 411.3 L208.5 412.7 L206.0 413.6 L205.2 413.6 L199.7 419.8 L196.8 422.6 L193.6 428.2 L196.0 433.6 L199.7 435.4 L199.4 436.9 L192.9 440.1 L190.8 442.9 L189.1 445.5 L188.3 447.2 L187.4 448.9 L188.0 450.3 L185.9 450.6 L177.1 452.8 L173.3 458.2 L170.2 460.6 L166.9 459.6 L164.1 460.6 L161.2 460.7 L156.7 460.5 L152.7 460.7 L142.8 461.0 L141.1 462.0 L135.7 463.6 L132.0 465.1 L130.3 468.0 L129.7 467.8 L129.0 468.8 L127.0 469.4 L122.8 467.5 L120.1 465.6 L118.9 463.3 L118.9 462.4 L117.1 460.8 L119.0 458.8 L118.3 458.6 L116.1 458.1 L111.5 454.5 L110.6 454.9 L107.5 455.0 L103.8 452.3 L103.4 450.4 L105.0 448.0 L107.4 445.3 L109.4 444.8 L110.2 443.1 L108.4 443.2 L105.5 439.3 L106.1 437.5 L106.9 436.0 L109.1 434.4 L109.7 432.5 L107.5 431.6 L105.5 427.6 L104.1 426.7 L103.0 425.2 L108.2 424.9 L109.3 424.5 L110.8 421.8 L110.8 420.4 L109.3 419.0 L110.4 418.0 L112.1 416.9 L111.6 416.1 L111.8 415.2 L112.0 413.1 L111.5 410.4 L110.8 408.4 L112.5 407.6 L115.2 405.2 L118.6 403.4 L119.6 402.4 L119.2 401.6 L117.4 400.8 L115.5 400.7 L115.3 399.3 L115.1 397.8 L113.4 397.5 L111.8 397.2 L109.3 397.4 L107.9 397.0 L107.3 397.3 L107.1 398.0 L104.6 398.8 L102.0 398.5 L101.0 398.1 L98.1 398.2 L96.0 399.0 L95.0 398.9 L94.3 398.0 L95.5 396.5 L95.0 395.9 L94.5 395.1 L93.1 395.4 L89.7 396.1 L87.4 397.5 L86.1 397.4 L87.4 394.2 L88.0 393.3 L87.0 392.7 L88.0 391.7 L86.9 391.0 L87.1 389.5 L84.7 389.6 L84.1 388.7 L85.5 387.0 L83.0 386.2 L81.6 384.9 L82.3 382.5 L84.3 381.7 L88.8 380.7 L91.8 379.9 L94.0 379.3 L93.5 378.0 L95.4 377.0 L99.0 376.0 L102.2 375.8 L104.7 376.1 L108.9 377.9 L114.5 377.4 L119.5 377.3 L124.2 376.8 L130.9 377.9 L140.9 379.5 L147.2 379.0 L150.3 378.8 L153.4 378.4 L159.4 380.1 L161.6 379.1 L168.3 380.6 L172.7 380.4 L175.2 379.6 L175.2 379.6 Z"><title>Spain</title></path>
              <path class="map-region" d="M437.5 204.3 L436.5 204.5 L435.9 205.4 L435.0 205.5 L434.2 205.8 L433.9 208.5 L435.4 209.6 L434.6 209.7 L433.9 210.0 L433.3 210.5 L432.8 211.5 L430.8 212.0 L430.0 212.4 L428.9 213.4 L428.3 214.7 L427.1 215.2 L425.8 215.4 L426.6 214.3 L427.6 213.4 L426.6 212.8 L426.1 211.8 L425.3 211.1 L425.9 210.3 L425.6 209.0 L425.7 207.6 L426.6 207.0 L427.6 206.5 L429.1 205.2 L430.8 204.3 L433.1 203.9 L434.1 204.3 L434.6 203.5 L435.3 203.3 L436.0 203.5 L437.5 204.3 Z M405.5 223.0 L404.9 223.7 L404.3 223.6 L403.9 222.8 L403.8 220.7 L404.0 219.7 L406.8 215.9 L408.0 215.6 L409.7 213.3 L410.2 212.3 L410.9 211.4 L411.4 210.6 L411.7 210.2 L412.6 210.4 L412.9 210.5 L412.1 211.0 L412.2 211.6 L412.1 211.9 L410.0 214.6 L409.4 216.4 L408.6 216.8 L405.5 223.0 Z M340.9 189.7 L342.8 191.4 L345.0 189.9 L346.0 186.6 L344.6 183.3 L346.5 181.6 L347.7 179.6 L349.5 179.2 L352.2 178.3 L354.7 176.6 L355.1 174.2 L356.0 172.5 L354.2 169.6 L352.3 165.8 L354.4 165.3 L357.4 165.1 L358.3 163.7 L359.4 162.3 L358.1 160.4 L354.7 158.8 L350.5 157.0 L352.2 151.6 L352.4 150.2 L350.1 145.6 L350.1 143.6 L350.3 142.1 L350.4 140.5 L348.6 137.9 L350.8 134.2 L355.3 131.2 L357.2 129.8 L361.0 128.7 L364.9 128.4 L373.2 129.2 L374.5 128.2 L375.6 126.2 L374.7 123.7 L369.3 122.3 L375.2 117.8 L379.1 114.0 L380.6 109.3 L381.7 107.5 L381.4 105.8 L385.3 103.1 L388.2 102.7 L392.4 101.3 L393.3 98.3 L401.8 93.1 L404.1 91.7 L403.4 89.8 L400.5 87.7 L402.7 86.5 L406.1 85.3 L408.7 82.0 L415.5 79.4 L423.0 81.1 L425.6 79.1 L426.0 76.8 L426.0 74.3 L428.8 73.9 L434.9 74.6 L439.8 75.0 L447.5 76.3 L449.8 76.0 L448.8 74.1 L452.2 72.5 L453.5 70.4 L452.7 69.3 L455.3 68.1 L460.4 68.8 L460.6 69.3 L464.0 70.6 L467.0 71.9 L469.5 72.8 L472.4 73.7 L476.7 74.9 L484.1 75.9 L486.5 76.9 L489.2 79.0 L491.3 79.6 L494.9 81.3 L493.2 82.2 L493.1 84.4 L493.6 85.7 L492.7 86.6 L492.6 87.3 L493.6 87.4 L496.1 87.7 L496.4 89.1 L494.7 90.0 L494.9 91.3 L496.4 92.8 L498.7 94.3 L499.3 95.2 L498.1 96.4 L497.7 98.0 L495.7 99.2 L495.3 100.4 L495.7 101.9 L496.3 102.7 L499.4 104.3 L501.4 107.4 L495.5 107.1 L492.1 107.4 L488.8 108.1 L485.8 107.6 L482.1 107.4 L480.1 106.8 L478.9 106.9 L477.9 108.0 L477.6 109.6 L475.4 109.7 L476.0 110.2 L475.4 110.7 L473.1 111.0 L473.2 111.9 L470.3 112.3 L468.4 112.5 L468.6 113.1 L469.4 113.5 L468.8 114.1 L466.9 113.3 L468.1 114.2 L469.0 115.2 L467.1 117.0 L464.2 118.7 L464.3 119.9 L465.9 121.7 L468.2 123.7 L467.6 124.7 L461.9 127.2 L457.7 131.4 L453.8 132.7 L448.1 134.1 L445.6 135.8 L444.0 135.6 L442.7 135.9 L441.0 135.7 L439.5 137.3 L434.3 138.4 L434.7 138.8 L434.3 139.1 L432.4 139.3 L431.3 139.9 L429.1 141.0 L427.9 141.5 L430.1 142.0 L429.8 142.7 L426.7 143.8 L424.9 144.0 L425.2 143.5 L422.8 142.9 L422.7 143.5 L423.7 144.9 L422.8 145.6 L424.1 146.0 L423.3 146.6 L420.5 147.5 L418.6 148.2 L416.6 147.5 L416.1 148.5 L418.2 150.4 L418.5 151.1 L417.0 153.4 L416.1 155.3 L416.7 156.8 L415.6 157.4 L414.1 157.8 L413.3 159.7 L413.2 161.2 L413.9 162.0 L413.7 162.8 L414.1 166.0 L414.9 168.1 L414.6 169.4 L417.2 170.1 L418.9 170.3 L419.7 171.4 L422.4 170.9 L424.1 171.7 L427.1 173.6 L431.0 174.9 L431.6 176.5 L434.7 177.6 L435.7 178.6 L436.2 180.9 L433.0 182.1 L431.3 183.2 L428.3 184.3 L426.7 185.0 L423.6 185.7 L425.7 186.3 L427.4 185.6 L429.0 185.6 L430.4 185.1 L431.8 186.1 L429.2 186.6 L428.0 188.5 L425.2 189.3 L421.9 190.7 L419.8 191.1 L415.8 192.8 L411.2 194.3 L402.8 194.2 L402.9 194.6 L404.9 194.8 L408.8 195.1 L409.2 196.7 L407.9 198.6 L407.7 200.3 L406.4 203.3 L406.2 205.2 L406.5 207.5 L406.8 209.2 L404.9 212.1 L405.5 213.6 L404.0 216.7 L401.6 219.4 L398.8 223.9 L396.7 225.1 L394.2 224.3 L390.4 224.7 L383.5 224.6 L383.2 226.2 L380.7 226.0 L378.8 226.9 L376.4 228.6 L377.2 231.0 L375.9 233.9 L371.3 233.5 L359.7 233.7 L360.4 232.2 L360.9 230.3 L360.4 228.9 L356.0 224.9 L354.5 223.0 L357.5 223.7 L358.6 223.4 L357.3 221.9 L358.3 221.0 L360.1 220.3 L358.5 218.7 L355.8 216.6 L350.5 211.7 L348.1 209.2 L347.1 207.0 L345.2 205.7 L344.8 202.6 L341.6 200.8 L340.1 197.6 L339.2 197.1 L338.8 194.0 L338.1 191.0 L338.1 189.6 L339.7 189.0 L340.9 189.7 Z M438.5 203.2 L438.3 204.0 L437.7 203.9 L437.1 203.3 L438.3 202.5 L440.1 202.5 L440.7 202.7 L438.5 203.2 Z M429.2 189.8 L428.7 189.9 L428.4 189.8 L428.7 189.3 L429.0 189.0 L429.8 188.8 L430.1 188.8 L429.2 189.8 Z M431.5 184.4 L431.2 184.8 L430.9 184.3 L431.0 184.2 L431.2 183.7 L431.8 183.4 L432.8 183.6 L432.8 183.7 L431.8 184.1 L431.5 184.4 Z"><title>Sweden</title></path>
              <path class="map-region" d="M317.4 329.6 L318.7 330.3 L317.5 332.7 L316.9 334.8 L317.2 335.2 L318.7 335.3 L321.5 335.9 L321.9 336.7 L325.1 337.8 L327.8 336.2 L329.1 337.2 L328.5 339.2 L328.9 340.6 L328.8 341.4 L326.9 341.3 L325.2 340.7 L324.2 341.5 L324.0 342.7 L324.8 343.7 L325.3 345.0 L324.4 345.4 L323.1 344.1 L322.0 343.7 L318.9 344.5 L317.5 344.4 L316.4 342.9 L315.9 342.3 L314.1 342.4 L314.0 344.6 L311.7 346.9 L310.9 347.9 L311.1 349.0 L311.2 350.0 L309.7 349.8 L308.1 348.2 L308.6 347.2 L305.4 346.2 L303.8 344.7 L303.8 342.9 L302.9 342.7 L301.2 344.0 L299.3 345.0 L299.9 346.2 L298.2 347.9 L295.6 349.1 L292.5 348.4 L289.8 349.2 L286.4 349.3 L285.8 348.6 L284.4 347.5 L283.3 346.5 L283.4 344.8 L282.8 343.6 L282.7 343.1 L278.5 342.9 L276.1 344.1 L276.0 344.4 L275.6 345.8 L273.2 346.4 L272.8 345.5 L274.3 344.7 L274.7 343.5 L274.0 342.6 L274.8 341.2 L276.7 339.8 L278.5 338.0 L278.9 336.6 L281.5 335.7 L283.5 334.0 L285.4 332.3 L285.7 331.8 L284.7 331.6 L285.3 330.5 L287.4 330.0 L287.8 330.5 L289.1 330.8 L291.0 330.4 L291.9 329.3 L294.5 329.0 L299.5 329.0 L302.4 328.6 L303.7 328.8 L304.3 328.5 L305.5 328.2 L305.2 328.0 L303.5 327.9 L303.8 327.1 L305.5 326.5 L307.4 327.5 L308.0 327.3 L308.7 327.4 L309.4 328.0 L313.2 327.8 L317.4 329.6 L317.4 329.6 Z"><title>Switzerland</title></path>
              <path class="map-region" d="M524.2 419.4 L521.3 419.8 L520.4 419.4 L521.3 418.7 L523.0 418.2 L523.5 418.2 L524.3 418.9 L524.2 419.4 Z M719.6 402.6 L722.0 403.2 L723.5 403.7 L726.7 402.9 L729.2 403.1 L731.6 403.6 L732.8 402.1 L733.3 401.9 L735.2 401.9 L736.0 402.9 L739.0 404.6 L740.4 405.4 L740.2 406.0 L741.8 406.7 L743.3 406.8 L743.8 407.4 L744.0 408.1 L745.7 409.3 L747.0 411.4 L747.2 413.2 L745.4 415.2 L746.0 416.3 L746.8 418.2 L746.9 419.2 L748.2 420.2 L750.9 420.9 L754.5 420.6 L757.9 422.4 L760.5 424.7 L761.1 425.3 L760.0 424.9 L757.4 424.3 L755.8 428.1 L753.9 428.4 L751.4 428.4 L751.3 429.0 L751.8 430.1 L752.4 431.0 L753.1 431.9 L752.9 433.0 L753.0 434.0 L754.3 435.2 L754.4 437.6 L754.5 440.3 L754.9 440.8 L756.3 441.0 L756.5 441.5 L755.5 442.8 L755.0 444.0 L753.7 445.8 L753.7 446.8 L755.9 447.5 L758.3 448.9 L757.7 449.8 L758.1 450.7 L758.1 452.2 L759.8 453.2 L760.9 454.3 L760.5 455.6 L760.0 455.5 L758.5 455.4 L757.1 456.2 L755.0 457.4 L753.9 457.7 L753.4 456.9 L753.3 454.5 L752.3 453.9 L751.0 453.7 L748.8 454.8 L745.4 454.7 L742.1 453.7 L740.6 453.3 L737.5 453.6 L735.5 453.0 L733.7 454.5 L730.2 456.2 L729.1 454.2 L728.3 453.9 L726.5 455.0 L722.5 456.0 L717.4 456.7 L714.4 456.5 L710.8 456.2 L706.2 457.4 L696.6 460.7 L692.5 461.4 L686.8 461.2 L684.1 461.0 L681.0 459.2 L679.3 458.8 L674.3 460.0 L671.9 460.6 L668.3 461.9 L665.2 461.7 L662.7 461.2 L660.0 460.1 L658.2 460.2 L657.2 463.5 L658.3 466.5 L657.4 467.0 L655.6 467.2 L654.7 469.6 L652.8 470.4 L651.9 471.7 L648.9 470.7 L648.9 467.8 L648.8 464.7 L652.7 461.7 L652.5 459.9 L650.9 458.6 L647.8 460.2 L646.0 460.9 L644.5 462.4 L639.9 462.0 L635.3 460.0 L632.7 460.2 L625.4 465.5 L621.3 467.5 L618.1 467.8 L611.7 468.5 L606.7 468.5 L603.6 466.4 L600.3 463.2 L591.9 460.0 L586.8 459.4 L582.2 460.0 L581.2 464.2 L580.5 466.4 L578.6 466.2 L575.9 466.7 L570.9 467.8 L565.1 465.7 L563.7 463.4 L563.0 461.9 L561.9 461.0 L560.0 461.5 L555.8 459.9 L552.2 461.3 L550.0 462.0 L550.8 460.6 L545.4 461.5 L542.8 461.0 L544.1 460.5 L548.9 459.9 L550.8 458.5 L552.8 457.2 L545.5 457.4 L541.1 457.8 L540.3 456.6 L541.8 456.0 L543.7 454.5 L541.9 453.4 L539.9 452.8 L539.0 450.2 L538.1 449.2 L540.3 446.8 L539.1 445.5 L535.6 444.7 L533.2 443.0 L531.9 443.6 L530.0 442.8 L528.2 442.0 L529.8 440.9 L529.3 438.5 L530.1 437.6 L531.9 438.6 L532.1 440.3 L533.0 441.3 L533.7 440.3 L535.4 440.8 L539.0 439.9 L536.0 439.5 L534.6 437.8 L534.2 436.8 L536.0 435.9 L536.8 434.2 L535.5 434.2 L534.7 433.1 L535.3 431.8 L533.1 429.7 L534.8 428.1 L535.9 426.5 L530.7 426.9 L526.0 427.5 L525.8 426.3 L526.5 422.6 L528.5 420.8 L533.9 416.2 L538.7 415.6 L541.1 416.0 L543.1 417.2 L547.1 416.8 L546.3 415.2 L548.1 414.8 L549.6 415.4 L548.8 416.4 L553.3 416.2 L559.0 416.3 L563.0 415.9 L561.0 415.2 L559.6 414.6 L563.0 413.2 L572.9 412.1 L572.4 411.8 L565.6 410.8 L563.3 409.4 L563.1 407.7 L564.1 406.2 L573.8 407.1 L585.0 407.9 L591.8 407.0 L601.1 401.7 L606.8 399.1 L616.2 396.7 L627.6 397.2 L637.8 396.0 L639.5 396.9 L639.2 398.1 L641.5 400.1 L649.3 400.2 L650.9 400.6 L653.8 404.8 L656.7 405.7 L658.4 404.6 L662.8 405.6 L668.3 407.5 L674.3 408.9 L682.4 409.7 L693.4 407.6 L699.5 409.3 L702.2 409.6 L709.2 407.6 L712.6 406.3 L718.4 403.8 L719.6 402.6 Z M549.9 397.1 L549.6 398.5 L550.3 400.0 L552.2 402.2 L554.1 403.2 L561.6 405.9 L563.0 406.1 L562.7 407.2 L562.2 408.2 L561.7 408.8 L559.5 409.2 L553.4 408.0 L551.9 407.9 L550.8 408.2 L548.8 409.0 L546.5 408.7 L543.4 409.2 L542.6 410.9 L540.4 412.7 L536.8 414.2 L534.3 415.0 L530.5 417.9 L528.7 419.6 L528.0 419.9 L527.1 420.1 L527.4 419.3 L527.8 418.6 L527.7 418.0 L527.8 417.2 L529.0 416.3 L530.2 415.7 L533.6 414.4 L534.5 413.4 L531.8 413.5 L529.1 413.7 L527.4 413.6 L525.9 413.6 L525.4 412.8 L525.1 412.2 L525.4 412.1 L525.9 412.0 L526.8 411.0 L527.6 410.3 L528.7 409.5 L529.0 408.9 L529.0 408.5 L528.8 408.1 L528.7 407.7 L528.7 407.2 L528.7 406.0 L531.3 404.7 L532.1 404.6 L532.4 404.0 L532.2 402.7 L531.9 401.6 L531.4 401.5 L530.8 401.2 L530.4 400.8 L529.7 400.4 L528.6 400.2 L528.6 399.9 L528.7 399.5 L529.1 399.2 L531.0 398.9 L531.2 398.6 L531.5 398.0 L531.9 397.4 L532.3 397.2 L533.1 397.2 L534.6 397.1 L535.7 396.9 L536.8 396.4 L537.3 396.0 L539.6 395.8 L540.2 395.6 L540.9 395.8 L541.7 396.4 L543.1 397.4 L543.9 397.7 L544.4 397.6 L545.5 397.2 L546.4 397.2 L547.2 397.3 L547.6 397.0 L548.2 396.9 L549.9 397.1 Z"><title>Turkey</title></path>
              <path class="map-country" data-country="UA" d="M678.1 334.9 L673.3 334.8 L669.7 335.1 L665.6 337.0 L662.0 338.1 L658.9 338.8 L655.7 339.2 L652.7 340.3 L648.1 340.5 L640.9 345.7 L639.4 346.6 L637.9 346.8 L641.2 344.7 L641.4 343.6 L638.5 344.9 L635.8 345.8 L635.9 348.3 L637.7 351.4 L635.2 350.7 L633.8 348.4 L630.8 348.5 L628.0 346.9 L625.5 346.8 L620.9 345.5 L620.0 347.0 L618.0 347.4 L615.1 346.0 L610.0 346.5 L604.1 346.5 L599.1 344.6 L597.2 344.2 L598.9 343.9 L600.2 343.4 L598.2 342.5 L595.3 341.9 L596.4 341.4 L601.7 341.9 L605.3 341.8 L607.3 340.6 L601.6 340.9 L599.7 339.5 L599.5 337.7 L598.3 334.8 L597.0 333.4 L598.3 335.9 L598.8 339.4 L597.2 340.5 L594.1 340.0 L593.7 339.2 L591.5 340.7 L584.9 341.4 L583.9 343.7 L583.1 344.9 L581.1 347.0 L577.2 350.0 L573.6 351.1 L570.9 351.1 L569.8 352.0 L570.7 353.7 L571.2 357.1 L569.4 355.8 L565.1 355.4 L561.0 356.8 L559.5 356.5 L559.4 357.0 L559.6 357.4 L555.4 356.7 L552.4 354.8 L553.6 354.2 L556.0 354.0 L556.2 353.3 L555.9 352.2 L558.1 350.6 L559.0 348.9 L561.6 347.5 L562.4 346.0 L561.4 343.7 L561.8 342.6 L564.1 341.7 L564.8 342.0 L565.1 343.5 L566.1 342.5 L567.2 342.8 L568.1 342.6 L569.3 343.2 L570.6 343.1 L571.7 342.8 L573.3 343.8 L576.2 343.2 L573.9 341.6 L574.1 339.3 L573.3 338.1 L569.8 336.7 L569.4 336.0 L568.8 334.9 L569.1 333.7 L569.1 332.7 L568.0 332.4 L566.5 331.4 L564.3 330.4 L563.8 329.5 L564.6 328.0 L564.9 326.6 L563.9 324.2 L562.7 324.4 L561.3 324.4 L559.4 322.4 L556.4 322.0 L555.3 322.5 L554.6 321.8 L553.8 321.9 L553.4 320.9 L550.8 320.7 L550.2 319.9 L548.3 319.4 L546.1 318.4 L544.2 318.1 L542.9 318.4 L541.4 318.6 L537.2 319.3 L535.2 319.1 L532.4 320.7 L530.1 321.0 L528.1 322.4 L526.6 323.9 L520.7 324.6 L514.1 326.0 L511.7 327.2 L510.0 326.7 L506.7 324.7 L504.2 324.6 L501.7 325.0 L500.0 324.5 L495.8 324.0 L495.3 323.9 L492.0 323.9 L488.6 322.8 L487.5 323.7 L485.3 324.5 L484.9 323.9 L484.8 323.1 L484.0 322.5 L482.9 322.6 L481.6 322.2 L479.6 320.9 L478.3 320.3 L477.7 319.5 L477.5 318.9 L477.1 318.8 L476.1 316.9 L478.5 314.8 L479.7 312.5 L480.9 311.3 L481.6 310.7 L484.5 311.4 L485.0 310.9 L483.8 310.0 L483.1 309.3 L483.5 308.1 L482.6 305.8 L483.2 304.3 L486.3 301.6 L490.2 298.6 L493.2 296.7 L495.8 294.9 L499.5 294.0 L500.6 293.1 L500.0 290.7 L499.2 290.0 L499.8 289.6 L500.8 289.2 L499.2 288.1 L497.7 285.8 L495.2 283.6 L495.4 282.6 L494.5 281.1 L494.5 279.9 L495.7 279.6 L497.7 279.8 L499.2 280.2 L502.9 277.9 L504.0 276.8 L507.1 276.5 L510.3 276.4 L512.8 276.0 L519.3 276.1 L523.6 276.2 L529.5 277.1 L531.7 277.6 L536.5 278.2 L538.9 278.2 L540.9 280.1 L542.8 280.0 L545.8 280.4 L545.9 281.5 L547.1 280.9 L547.9 280.1 L550.7 280.5 L552.0 280.0 L555.1 280.5 L557.2 280.8 L558.4 282.0 L559.7 281.1 L561.4 280.5 L562.5 280.1 L563.6 279.7 L564.5 280.3 L566.0 282.3 L568.2 282.4 L571.2 282.0 L575.7 281.5 L577.6 281.9 L579.0 283.4 L581.7 284.1 L582.8 283.0 L582.4 281.6 L581.6 280.1 L582.9 278.0 L584.4 276.5 L587.2 274.6 L589.5 274.4 L591.8 273.9 L597.0 274.0 L598.4 274.3 L600.5 274.6 L602.7 274.2 L604.6 271.9 L605.5 271.5 L608.1 271.8 L611.3 272.1 L616.2 270.9 L620.3 271.2 L622.9 271.4 L625.3 273.3 L630.1 277.9 L629.9 278.6 L626.7 279.1 L627.0 280.0 L627.8 281.5 L628.0 282.9 L628.7 283.6 L627.8 284.2 L631.3 284.5 L634.1 285.3 L636.1 285.1 L638.5 284.9 L639.2 285.9 L640.2 286.8 L641.6 286.8 L641.6 287.5 L642.1 288.5 L643.0 290.2 L643.2 291.2 L642.6 292.1 L643.9 293.9 L645.1 295.0 L647.7 294.6 L650.4 294.4 L652.7 295.0 L654.1 296.1 L656.6 296.1 L658.1 297.0 L659.8 296.0 L664.5 295.2 L666.1 294.7 L668.2 294.5 L670.2 296.0 L671.7 298.2 L676.0 300.5 L677.3 300.2 L677.7 299.2 L678.7 298.9 L682.4 300.1 L685.2 300.9 L688.3 301.7 L690.2 301.3 L691.1 302.2 L692.6 302.8 L695.9 303.8 L699.0 304.8 L701.0 304.4 L701.8 305.1 L701.3 306.4 L702.2 307.9 L701.5 309.2 L699.2 310.9 L696.6 311.6 L697.5 312.7 L700.4 313.5 L700.4 314.0 L698.0 314.0 L696.9 314.8 L696.1 316.6 L698.5 317.2 L699.1 318.7 L698.7 319.8 L698.9 320.3 L700.0 320.5 L699.1 321.8 L697.8 324.3 L697.3 325.7 L692.9 325.8 L688.7 325.7 L685.8 325.8 L683.5 327.9 L680.1 328.6 L678.7 330.1 L678.5 331.4 L678.0 332.1 L678.5 332.5 L679.0 332.8 L678.2 333.4 L678.0 334.3 L678.1 334.9 Z M600.2 345.7 L601.9 346.2 L600.1 346.1 L596.2 345.5 L594.5 345.0 L594.1 344.4 L593.8 343.6 L594.8 344.4 L595.5 344.8 L600.2 345.7 Z"><title>Ukraine</title></path>
              <path class="map-country" data-country="UA" d="M606.0 355.9 L609.1 354.2 L613.5 353.6 L618.0 354.9 L622.4 355.8 L626.4 354.3 L629.9 355.7 L632.9 358.1 L638.0 359.6 L642.7 358.6 L647.5 356.9 L652.3 356.4 L657.2 357.7 L658.0 359.8 L654.4 361.7 L649.7 362.8 L644.9 364.4 L640.0 366.2 L634.9 367.5 L630.4 367.7 L626.1 366.6 L622.1 365.0 L618.1 363.6 L613.6 362.4 L609.8 360.5 L606.7 358.1 L606.0 355.9 Z"><title>Crimea, Ukraine</title></path>
              <path class="map-region" d="M164.2 279.8 L160.3 280.8 L156.7 282.5 L152.9 282.3 L148.8 280.2 L147.4 280.3 L144.5 280.4 L146.3 279.3 L143.3 278.8 L140.7 278.3 L138.4 279.0 L133.3 278.8 L132.8 277.5 L131.6 276.7 L133.7 275.2 L140.4 273.4 L144.7 271.8 L146.2 270.4 L147.7 268.6 L146.4 267.8 L146.9 266.6 L146.0 265.2 L146.2 264.1 L142.9 264.3 L140.1 265.3 L138.9 264.9 L140.8 263.5 L142.9 262.4 L144.1 261.3 L149.8 259.4 L151.9 259.4 L154.6 258.9 L158.8 259.9 L159.2 257.9 L161.7 259.5 L162.6 259.0 L161.1 258.8 L159.2 256.8 L160.1 255.0 L160.2 254.0 L159.4 252.8 L161.3 251.4 L161.9 249.2 L160.1 248.8 L158.6 249.3 L156.0 248.1 L152.8 245.2 L154.2 241.5 L159.5 239.3 L154.5 239.2 L151.7 240.0 L150.2 240.3 L148.7 241.1 L146.5 241.3 L145.2 241.1 L144.2 240.6 L142.3 241.3 L139.3 241.3 L136.7 240.9 L136.0 242.5 L133.2 240.5 L132.7 238.9 L134.2 238.9 L137.6 234.4 L138.9 232.6 L138.3 231.5 L136.2 229.2 L137.0 227.4 L140.1 227.3 L136.8 225.9 L137.4 224.6 L136.7 225.2 L135.2 226.5 L133.4 227.2 L132.4 227.4 L132.0 228.0 L131.7 226.6 L132.6 225.1 L133.8 224.2 L130.0 226.3 L129.6 226.9 L130.2 228.7 L127.9 234.0 L127.1 234.7 L125.7 234.7 L125.2 233.9 L126.3 231.1 L127.3 230.0 L128.5 228.9 L127.3 229.0 L127.2 225.9 L128.1 223.5 L129.4 221.4 L130.7 219.8 L131.8 218.2 L132.1 217.4 L126.7 220.1 L124.0 219.7 L122.7 218.2 L120.6 218.0 L121.8 217.3 L125.7 216.2 L124.2 215.4 L127.4 213.2 L126.9 210.8 L124.9 209.8 L124.8 208.7 L126.2 208.1 L126.3 207.5 L125.5 206.6 L126.1 205.0 L127.2 203.7 L130.8 203.4 L132.9 203.7 L129.9 201.7 L130.4 200.5 L130.4 199.7 L131.5 199.2 L134.8 199.1 L133.8 198.1 L133.9 197.2 L134.0 195.9 L135.2 195.2 L137.3 195.3 L138.4 196.1 L140.7 195.4 L142.0 196.0 L149.2 195.2 L154.3 194.8 L159.3 194.5 L159.3 195.1 L158.7 197.0 L158.3 197.7 L154.8 199.3 L147.6 202.8 L147.0 204.1 L149.2 204.5 L146.4 206.2 L147.6 207.4 L152.1 206.4 L156.3 205.8 L159.5 206.2 L161.8 206.0 L171.6 205.9 L174.2 207.0 L175.3 208.7 L173.4 210.1 L172.0 211.9 L171.4 213.2 L167.2 217.7 L165.1 219.7 L162.8 220.7 L158.4 221.4 L156.1 222.2 L158.9 221.8 L164.4 222.7 L162.9 224.1 L157.8 225.6 L155.4 226.2 L151.3 225.8 L151.1 226.0 L159.4 227.2 L162.1 226.3 L170.7 227.8 L174.7 230.6 L176.9 231.8 L178.6 235.6 L181.5 241.5 L183.2 242.9 L189.3 244.8 L193.1 247.5 L196.7 249.4 L195.1 250.6 L196.4 252.5 L199.2 255.6 L198.2 255.3 L196.8 255.2 L194.3 254.1 L190.6 254.2 L191.6 254.6 L199.3 257.3 L202.2 261.1 L200.3 262.7 L198.3 264.2 L201.9 265.3 L203.1 264.8 L204.7 263.4 L208.1 263.4 L211.0 263.5 L215.1 264.3 L219.3 267.0 L219.7 269.5 L218.4 271.8 L217.7 273.7 L215.5 275.3 L213.8 275.5 L213.1 275.8 L213.7 277.1 L211.6 277.8 L207.2 278.5 L209.4 279.5 L207.8 280.8 L205.2 281.0 L203.1 281.7 L205.3 281.7 L206.3 282.7 L210.5 283.0 L215.0 282.8 L215.5 283.6 L214.9 285.5 L210.0 287.7 L207.4 288.2 L204.4 289.1 L201.5 290.1 L195.2 289.6 L187.8 290.2 L185.1 289.6 L181.6 289.1 L180.9 289.5 L177.6 290.6 L174.3 290.8 L172.5 291.3 L172.6 292.1 L168.2 291.8 L167.1 292.2 L164.3 291.4 L161.2 290.7 L154.9 291.8 L153.4 294.3 L151.5 296.6 L148.7 296.0 L145.3 294.8 L144.7 294.9 L142.7 295.2 L138.3 296.0 L134.7 297.6 L133.4 299.0 L130.8 298.5 L127.9 298.5 L126.6 298.6 L127.7 297.1 L133.1 295.0 L134.8 293.5 L136.2 293.0 L140.1 290.1 L140.6 288.6 L143.7 287.0 L145.4 284.9 L152.4 284.6 L156.8 285.0 L159.5 284.3 L162.6 281.6 L165.2 280.0 L165.8 278.9 L164.2 279.8 Z M145.0 259.1 L145.5 259.4 L146.8 259.3 L146.4 259.8 L144.9 260.4 L143.9 260.9 L142.7 261.4 L142.2 260.9 L141.5 260.9 L140.5 259.9 L140.3 258.3 L141.6 257.9 L143.5 258.0 L145.0 259.1 Z M165.7 187.3 L164.2 187.3 L165.0 186.6 L165.8 186.4 L167.5 186.5 L167.2 186.8 L165.7 187.3 Z M184.6 171.7 L184.3 171.8 L183.1 170.6 L184.0 169.2 L185.1 169.2 L185.2 169.6 L185.1 169.9 L184.6 170.0 L184.5 170.1 L184.7 170.7 L184.7 171.5 L184.6 171.7 Z M181.3 171.4 L181.5 172.3 L182.2 172.0 L183.2 172.9 L183.7 172.9 L184.5 172.5 L184.3 173.3 L183.5 175.4 L183.2 175.8 L183.1 176.4 L182.9 176.6 L182.6 177.9 L182.1 178.3 L181.6 179.3 L181.4 179.4 L180.7 179.0 L181.4 177.5 L181.7 176.6 L181.5 176.1 L181.1 175.7 L180.0 175.6 L179.1 175.8 L178.9 175.6 L178.9 175.3 L178.6 175.1 L177.4 175.2 L177.1 175.1 L176.8 174.8 L176.8 174.5 L177.9 174.3 L178.9 174.4 L180.4 173.9 L179.5 172.3 L178.2 172.1 L178.0 171.9 L178.2 171.7 L178.9 171.5 L179.9 170.7 L180.6 170.5 L181.3 170.6 L181.3 171.4 Z M188.0 168.1 L188.0 168.2 L187.3 169.2 L187.3 169.6 L186.3 169.6 L186.1 169.5 L185.9 168.9 L186.1 168.3 L186.2 168.1 L186.5 168.0 L186.8 168.2 L187.4 167.8 L187.6 167.8 L188.0 168.1 Z M157.9 192.6 L157.2 192.8 L156.5 192.8 L155.4 192.1 L155.0 191.5 L155.0 191.2 L155.5 191.1 L156.6 191.3 L157.1 191.8 L157.2 192.2 L157.3 192.4 L158.0 192.5 L157.9 192.6 Z M160.9 193.2 L160.8 193.3 L160.3 193.1 L159.6 192.3 L160.7 192.1 L161.3 192.2 L161.1 192.5 L160.9 193.2 Z M159.3 189.7 L159.1 190.0 L160.1 190.0 L161.5 190.3 L162.3 190.3 L163.0 190.6 L162.6 191.2 L162.2 191.4 L161.7 191.4 L160.1 190.8 L157.9 191.1 L157.5 191.0 L157.2 190.8 L157.1 190.6 L157.1 190.2 L157.0 190.1 L156.2 190.5 L155.8 190.5 L155.6 190.3 L155.6 189.9 L155.6 189.3 L156.1 188.5 L156.9 188.4 L158.0 188.4 L159.4 188.9 L159.8 189.2 L159.7 189.4 L159.3 189.7 Z M163.4 187.8 L162.3 188.1 L161.9 187.9 L161.7 187.1 L160.5 186.8 L159.8 186.6 L159.3 186.2 L159.5 186.0 L160.3 185.9 L161.7 186.6 L162.3 187.2 L163.4 187.3 L163.5 187.4 L163.4 187.8 Z M114.6 219.5 L113.9 219.5 L113.9 219.4 L115.1 218.5 L115.9 218.4 L116.2 218.5 L115.6 219.0 L114.6 219.5 Z M133.5 233.3 L131.9 233.3 L131.4 233.2 L130.7 232.9 L129.9 231.2 L130.2 230.6 L130.5 230.3 L130.9 230.1 L131.7 230.0 L132.5 230.3 L132.8 230.6 L133.5 231.8 L133.7 232.7 L133.5 233.3 Z M125.1 222.4 L120.1 223.1 L118.3 223.0 L118.2 222.7 L118.5 222.4 L120.0 222.2 L120.5 220.6 L118.4 219.9 L118.3 219.6 L118.4 219.3 L118.7 219.1 L120.0 218.8 L120.5 218.7 L121.0 218.7 L121.9 219.2 L123.0 220.1 L124.3 220.2 L125.3 220.6 L125.1 222.4 Z M120.7 227.4 L121.1 229.0 L121.6 229.9 L121.6 230.3 L121.2 230.7 L119.1 231.3 L118.5 231.3 L118.4 231.2 L118.9 230.6 L118.5 229.9 L118.7 229.3 L118.5 229.2 L118.1 229.3 L116.6 230.2 L116.1 230.3 L116.1 230.1 L116.4 229.4 L116.5 228.9 L116.7 228.6 L117.1 228.3 L117.6 228.1 L118.0 228.1 L118.4 228.3 L119.6 227.7 L120.7 227.4 Z M122.7 228.8 L122.4 229.0 L121.8 228.9 L121.5 228.7 L121.4 228.4 L121.4 227.9 L121.8 227.5 L123.4 226.9 L122.7 226.7 L122.6 226.5 L123.1 226.0 L124.8 225.2 L125.3 225.1 L125.7 225.1 L124.8 226.5 L122.7 228.8 Z M119.8 197.8 L118.2 200.0 L117.6 200.0 L117.0 200.5 L115.3 201.1 L116.8 201.1 L117.2 201.3 L117.2 201.8 L116.9 202.0 L115.0 203.0 L113.7 203.3 L112.3 204.4 L111.6 204.4 L110.8 205.0 L110.3 205.3 L109.9 205.3 L109.5 205.2 L108.7 204.5 L110.3 203.9 L110.4 203.6 L111.5 203.2 L111.4 203.1 L109.7 202.6 L109.0 202.2 L109.1 202.0 L109.9 201.6 L109.5 201.6 L109.2 201.4 L108.7 201.3 L108.6 201.1 L108.5 200.6 L108.6 200.0 L109.1 199.8 L109.4 199.6 L109.6 199.5 L110.3 199.6 L111.1 200.0 L112.1 199.9 L113.2 200.0 L113.2 199.9 L112.4 198.8 L112.5 198.6 L113.0 198.4 L115.4 197.6 L118.5 196.3 L119.3 196.1 L119.5 196.3 L119.8 197.0 L119.8 197.8 Z M118.8 214.8 L118.4 215.0 L117.9 215.0 L117.5 214.8 L116.8 214.2 L118.2 213.8 L118.8 214.0 L119.0 214.3 L119.0 214.6 L118.8 214.8 Z M120.5 208.3 L120.4 208.8 L120.2 209.4 L120.5 210.1 L120.6 210.6 L121.1 210.7 L121.4 211.0 L123.8 211.2 L126.0 211.1 L126.4 211.3 L126.5 211.7 L126.1 212.0 L124.9 212.6 L123.4 213.7 L122.9 213.9 L122.4 213.9 L122.1 213.8 L121.9 212.0 L120.2 212.2 L118.9 212.2 L118.2 212.0 L117.7 211.5 L116.7 210.4 L113.8 210.0 L113.0 209.4 L112.7 209.0 L112.8 208.8 L113.4 208.4 L114.2 208.5 L114.7 208.5 L115.0 208.3 L115.0 208.1 L114.6 207.7 L114.5 207.6 L117.5 207.1 L117.8 206.3 L118.4 206.2 L119.2 206.5 L120.2 207.3 L120.5 208.3 Z M107.1 206.1 L108.5 206.8 L107.4 207.9 L105.7 207.9 L103.2 207.1 L103.2 206.9 L103.4 206.7 L103.8 206.5 L104.2 206.4 L104.8 206.6 L105.6 206.4 L106.3 206.4 L107.1 206.1 Z M106.6 213.0 L106.0 213.1 L105.3 213.0 L104.9 212.8 L104.5 212.1 L104.4 211.6 L104.6 210.8 L104.6 209.8 L106.0 209.8 L106.4 209.9 L106.6 212.9 L106.6 213.0 Z M104.5 214.8 L103.4 215.0 L103.0 214.9 L102.9 214.8 L103.1 214.3 L104.0 214.2 L104.6 214.4 L104.7 214.6 L104.5 214.8 Z M119.5 249.8 L117.7 249.9 L116.8 250.1 L114.1 250.2 L114.2 248.9 L112.6 248.5 L111.5 247.6 L111.3 246.9 L109.6 245.9 L108.0 246.6 L107.5 247.5 L107.3 248.3 L105.6 249.3 L104.6 249.2 L102.1 249.1 L99.0 248.3 L98.2 247.3 L95.3 245.4 L96.6 244.7 L100.2 243.7 L99.4 243.1 L98.3 242.6 L98.7 242.2 L100.4 242.2 L102.1 241.8 L103.4 240.8 L104.1 239.9 L105.0 238.4 L107.5 238.0 L109.3 237.7 L111.1 236.4 L113.5 236.4 L117.6 235.8 L120.7 236.1 L122.5 238.4 L125.8 240.9 L125.2 242.1 L123.8 243.1 L125.6 242.7 L128.2 243.4 L128.9 244.8 L128.2 245.3 L127.1 244.4 L126.7 245.1 L126.9 246.4 L127.2 247.6 L124.5 248.0 L123.8 249.0 L122.0 250.3 L119.5 249.8 L119.5 249.8 Z M184.3 291.1 L183.3 291.5 L182.9 292.0 L182.7 292.2 L182.0 292.3 L181.3 292.4 L178.7 291.4 L178.1 291.4 L178.7 291.0 L180.3 290.6 L181.2 290.1 L183.3 290.6 L184.3 291.1 Z"><title>United Kingdom</title></path>
              <path class="map-route" d="M110 390 C214 288 342 230 476 206 C580 188 660 205 714 252"></path>
              <circle class="map-city" cx="377" cy="258" r="4.5"></circle>
              <circle class="map-city" cx="502" cy="230" r="4.5"></circle>
              <circle class="map-city" cx="213" cy="380" r="4.5"></circle>
              <circle class="map-city" cx="121" cy="383" r="4.5"></circle>
              <circle class="map-city" cx="636" cy="273" r="4.5"></circle>
              <text class="map-label" x="373" y="264">DE</text>
              <text class="map-label" x="499" y="235">PL</text>
              <text class="map-label" x="214" y="386">ES</text>
              <text class="map-label" x="122" y="389">PT</text>
              <text class="map-label" x="631" y="278">UA</text>
            </svg>
          </div>
          <aside class="country-panel fade-up">
            <div>
              <strong data-i18n="landing.presence_title">Країни присутності</strong>
              <p class="neutral-note" id="map-note" data-i18n="landing.map_loading">Завантажую реальні дані з бекенда…</p>
            </div>
            <div class="country-list" id="country-list"></div>
          </aside>
        </div>
      </section>

      <section class="light-section" id="how">
        <div class="section-head fade-up">
          <h2 data-i18n="landing.how_title">Як працює</h2>
          <p data-i18n="landing.how_subtitle">Короткий шлях від першого контакту до роботи: без зайвих екранів, з AI-перевіркою і людським координатором там, де це важливо.</p>
        </div>
        <div class="steps-grid">
          <article class="step-card fade-up"><div class="step-icon">1</div><h3 data-i18n="landing.step_photo_title">Фото</h3><p data-i18n="landing.step_photo_text">Кандидат створює живий профіль і додає базові дані.</p></article>
          <article class="step-card fade-up"><div class="step-icon">2</div><h3 data-i18n="landing.step_docs_title">Документи</h3><p data-i18n="landing.step_docs_text">ATLAS структурує документи та підсвічує прогалини.</p></article>
          <article class="step-card fade-up"><div class="step-icon">3</div><h3>AI</h3><p data-i18n="landing.step_ai_text">Система аналізує досвід, ризики, країну та відповідність вакансіям.</p></article>
          <article class="step-card fade-up"><div class="step-icon">4</div><h3 data-i18n="landing.step_work_title">Робота</h3><p data-i18n="landing.step_work_text">Кандидат отримує наступний крок і контакт координатора.</p></article>
        </div>
      </section>

      <section class="light-section" id="support">
        <div class="section-head fade-up">
          <h2 data-i18n="landing.support_title">Супровід після підбору</h2>
          <p data-i18n="landing.support_subtitle">ATLAS допомагає закрити практичні питання, які вирішують, чи зможе людина реально вийти на роботу: легалізація, навчання та житло.</p>
        </div>
        <div class="support-grid">
          <article class="support-card fade-up">
            <div class="support-icon">LG</div>
            <h3 data-i18n="landing.support_legal_title">Легалізація</h3>
            <p data-i18n="landing.support_legal_text">Координатор фіксує країну, статус документів і передає складні випадки на ручну перевірку.</p>
            <ul>
              <li data-i18n="landing.support_legal_item_1">Аналіз наявних документів</li>
              <li data-i18n="landing.support_legal_item_2">Підказки щодо наступного кроку</li>
              <li data-i18n="landing.support_legal_item_3">Без фінальних юридичних рішень від AI</li>
            </ul>
          </article>
          <article class="support-card fade-up">
            <div class="support-icon">CR</div>
            <h3 data-i18n="landing.support_courses_title">Курси</h3>
            <p data-i18n="landing.support_courses_text">ATLAS бачить прогалини в профілі та може рекомендувати навчання або сертифікацію перед підбором.</p>
            <ul>
              <li data-i18n="landing.support_courses_item_1">Мовні та професійні курси</li>
              <li data-i18n="landing.support_courses_item_2">Підготовка до вакансій з вимогами</li>
              <li data-i18n="landing.support_courses_item_3">Підвищення довіри до профілю</li>
            </ul>
          </article>
          <article class="support-card fade-up">
            <div class="support-icon">HM</div>
            <h3 data-i18n="landing.support_housing_title">Допомога з житлом</h3>
            <p data-i18n="landing.support_housing_text">Платформа відмічає потребу в житлі та показує роботодавцю, чи потрібні умови проживання для кандидата.</p>
            <ul>
              <li data-i18n="landing.support_housing_item_1">Потреба в житлі в профілі</li>
              <li data-i18n="landing.support_housing_item_2">Умови житла у вакансії</li>
              <li data-i18n="landing.support_housing_item_3">Контроль координатора перед стартом</li>
            </ul>
          </article>
          <article class="support-card fade-up">
            <div class="support-icon">IN</div>
            <h3 data-i18n="landing.support_insurance_title">Страхування</h3>
            <p data-i18n="landing.support_insurance_text">ATLAS може фіксувати потребу в страховому супроводі та передавати її координатору перед виїздом або стартом.</p>
            <ul>
              <li data-i18n="landing.support_insurance_item_1">Потреба в медичному покритті</li>
              <li data-i18n="landing.support_insurance_item_2">Страхування для країни роботи</li>
              <li data-i18n="landing.support_insurance_item_3">Контроль готовності до виїзду</li>
            </ul>
          </article>
        </div>
      </section>

      <section class="light-section" id="trust">
        <div class="section-head fade-up">
          <h2 data-i18n="landing.trust_title">Чому довіряють ATLAS</h2>
          <p data-i18n="landing.trust_subtitle">Платформа поєднує автоматизацію, перевірку документів і людську відповідальність координатора.</p>
        </div>
        <div class="trust-grid">
          <article class="trust-card fade-up"><div class="trust-icon">AI</div><h3 data-i18n="landing.trust_ai_title">AI Verification</h3><p data-i18n="landing.trust_ai_text">Профіль оцінюється за структурованими сигналами, а не за здогадками.</p></article>
          <article class="trust-card fade-up"><div class="trust-icon">DV</div><h3 data-i18n="landing.trust_docs_title">Document Validation</h3><p data-i18n="landing.trust_docs_text">Документи проходять перевірку повноти і ризиків.</p></article>
          <article class="trust-card fade-up"><div class="trust-icon">HC</div><h3 data-i18n="landing.trust_human_title">Human Coordinator</h3><p data-i18n="landing.trust_human_text">Координатор підключається там, де потрібне людське рішення.</p></article>
          <article class="trust-card fade-up"><div class="trust-icon">SS</div><h3 data-i18n="landing.trust_storage_title">Secure Storage</h3><p data-i18n="landing.trust_storage_text">Дані зберігаються для підбору, перевірки та контакту.</p></article>
          <article class="trust-card fade-up"><div class="trust-icon">SM</div><h3 data-i18n="landing.trust_matching_title">Smart Matching</h3><p data-i18n="landing.trust_matching_text">ATLAS порівнює профіль із вакансіями та вимогами роботодавців.</p></article>
        </div>
      </section>

      <section class="ai-section" id="atlas-ai">
        <div class="ai-block fade-up">
          <div>
            <div class="eyebrow">Atlas AI</div>
            <h2 data-i18n="landing.ai_title">AI, який говорить людською мовою</h2>
            <p data-i18n="landing.ai_subtitle">Для працівника ATLAS поводиться як товариш: спокійно пояснює, що робити далі. Для роботодавця звучить як бізнес-партнер: структурно, коротко і по суті.</p>
          </div>
          <div class="ai-capabilities">
            <div class="ai-capability"><strong data-i18n="landing.cap_profile_title">Profile Intelligence</strong><span data-i18n="landing.cap_profile_text">Перетворює діалог у CV-мапу і робочий профіль.</span></div>
            <div class="ai-capability"><strong data-i18n="landing.cap_docs_title">Document Signals</strong><span data-i18n="landing.cap_docs_text">Бачить, яких документів бракує для країни та вакансії.</span></div>
            <div class="ai-capability"><strong data-i18n="landing.cap_matching_title">Employer Matching</strong><span data-i18n="landing.cap_matching_text">Підбирає релевантні вакансії без вигаданої статистики.</span></div>
            <div class="ai-capability"><strong data-i18n="landing.cap_handoff_title">Coordinator Handoff</strong><span data-i18n="landing.cap_handoff_text">Передає координатору контекст без втрати деталей.</span></div>
          </div>
        </div>
      </section>
    </main>

    <footer>
      <span>ATLAS by EWU</span>
      <span data-i18n="landing.footer_tagline">AI workforce platform for Europe</span>
    </footer>
  </div>

  <script>
    window.ATLAS_DISABLE_AUTO_I18N = true;
  </script>
  {observability_body_html("landing")}
  <script src="/static/i18n.js?v=20260711-langfix2"></script>
  <script type="module">
    let motionAnimate = null;
    try {{
      const motion = await import("https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm");
      motionAnimate = motion.animate;
    }} catch (error) {{
      document.documentElement.classList.add("motion-fallback");
    }}

    const menuToggle = document.getElementById("menu-toggle");
    const nav = document.getElementById("main-nav");
    const landingI18n = {{
      languages: [],
      translations: {{}},
      currentLanguage: "uk",
      supported: ["pl", "uk", "ru", "en", "de", "es", "pt"]
    }};

    function normalizeLandingLanguage(value) {{
      const code = String(value || "").trim().toLowerCase().split("-")[0].split("_")[0];
      return landingI18n.supported.includes(code) ? code : "";
    }}

    function landingUrlLanguage() {{
      const pathCode = normalizeLandingLanguage(location.pathname.replace(/^\/+/, "").split("/")[0]);
      return pathCode || normalizeLandingLanguage(new URLSearchParams(location.search).get("lang"));
    }}

    function applyLandingTranslations() {{
      document.documentElement.lang = landingI18n.currentLanguage;
      document.querySelectorAll("[data-i18n]").forEach((element) => {{
        const key = element.getAttribute("data-i18n");
        element.textContent = tr(key, element.textContent);
      }});
      document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {{
        const key = element.getAttribute("data-i18n-aria-label");
        element.setAttribute("aria-label", tr(key, element.getAttribute("aria-label") || key));
      }});
      document.querySelectorAll("[data-language-current]").forEach((element) => {{
        element.textContent = landingI18n.currentLanguage.toUpperCase();
      }});
    }}

    function renderLandingLanguageMenu() {{
      document.querySelectorAll("[data-language-selector]").forEach((selector) => {{
        const button = selector.querySelector("[data-language-button]");
        const menu = selector.querySelector("[data-language-menu]");
        if (!button || !menu) return;
        menu.innerHTML = landingI18n.languages.map((language) => `
          <button class="language-option ${{language.code === landingI18n.currentLanguage ? "active" : ""}}" type="button" data-language-code="${{language.code}}" role="menuitem">
            <span>${{language.flag || ""}}</span>
            <span>${{language.native_name || language.name || language.code}}</span>
          </button>
        `).join("");
        if (!button.dataset.landingI18nBound) {{
          button.dataset.landingI18nBound = "true";
          button.addEventListener("click", () => {{
            const isOpen = menu.classList.toggle("open");
            button.setAttribute("aria-expanded", String(isOpen));
          }});
        }}
        menu.querySelectorAll("[data-language-code]").forEach((option) => {{
          option.addEventListener("click", async () => {{
            await loadLandingLanguage(option.getAttribute("data-language-code"));
            menu.classList.remove("open");
            button.setAttribute("aria-expanded", "false");
          }});
        }});
      }});
    }}

    async function loadLandingLanguage(language) {{
      const selected = normalizeLandingLanguage(language) || landingUrlLanguage() || localStorage.getItem("atlas_language") || "uk";
      const params = new URLSearchParams({{ selected_language: selected, browser_language: navigator.language || "" }});
      const response = await fetch(`/api/i18n/bootstrap?${{params.toString()}}`, {{ cache: "no-store" }});
      const data = await response.json();
      landingI18n.languages = data.languages || [];
      landingI18n.translations = data.translations || {{}};
      landingI18n.currentLanguage = normalizeLandingLanguage(data.current_language) || selected;
      localStorage.setItem("atlas_language", landingI18n.currentLanguage);
      applyLandingTranslations();
      renderLandingLanguageMenu();
      renderMarketMap(marketMapData);
    }}
    window.loadLandingLanguage = loadLandingLanguage;

    menuToggle.addEventListener("click", () => {{
      const isOpen = nav.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", String(isOpen));
    }});

    const steps = Array.from(document.querySelectorAll(".analysis-step"));
    let activeStep = 0;
    setInterval(() => {{
      steps.forEach((step, index) => step.classList.toggle("active", index <= activeStep));
      activeStep = (activeStep + 1) % steps.length;
    }}, 1050);

    function runMotion() {{
      document.querySelectorAll(".fade-up").forEach((element) => {{
        element.classList.add("motion-visible");
      }});
      if (motionAnimate) {{
        motionAnimate(".ai-coordinator-card", {{ boxShadow: ["0 24px 58px rgba(0,0,0,0.32)", "0 24px 68px rgba(212,175,55,0.16)", "0 24px 58px rgba(0,0,0,0.32)"] }}, {{ duration: 3.8, repeat: Infinity }});
      }}
    }}

    let marketMapData = null;
    function tr(key, fallback) {{
      if (landingI18n.translations[key]) return landingI18n.translations[key];
      return window.AtlasI18n ? window.AtlasI18n.t(key, fallback) : (fallback || key);
    }}

    function countryName(country) {{
      return tr(`country.${{country.code}}`, country.name);
    }}

    function countryLabel(country, hasLiveMetrics) {{
      if (!hasLiveMetrics) return tr("landing.map_neutral", "Neutral state");
      const template = tr("landing.open_vacancies", "{{count}} open vacancies");
      return template.replace("{{count}}", country.open_vacancies);
    }}

    function renderMarketMap(data) {{
      const list = document.getElementById("country-list");
      const note = document.getElementById("map-note");
      if (!data) {{
        note.textContent = tr("landing.map_loading", "Loading live backend data...");
        list.innerHTML = "";
        return;
      }}
      const countries = data.countries || [];
      const activeCodes = new Set(countries.map((country) => country.code));
      document.querySelectorAll(".map-country").forEach((shape) => {{
        shape.classList.toggle("active", activeCodes.has(shape.dataset.country));
      }});
      note.textContent = data.has_live_metrics
        ? tr("landing.map_live_note", "The metrics below are loaded from ATLAS backend.")
        : tr("landing.map_neutral_note", "Metrics are not synchronized yet. Countries are shown without invented statistics.");
      list.innerHTML = countries.map((country) => `
        <div class="country-item">
          <span class="country-dot"></span>
          <div><strong>${{countryName(country)}}</strong><br><span>${{country.code}} · ${{country.currency}}</span></div>
          <span>${{countryLabel(country, data.has_live_metrics)}}</span>
        </div>
      `).join("");
    }}

    async function loadMarketMap() {{
      const note = document.getElementById("map-note");
      try {{
        const response = await fetch("/api/public/market-map", {{ cache: "no-store" }});
        marketMapData = await response.json();
        renderMarketMap(marketMapData);
      }} catch (error) {{
        note.textContent = tr("landing.map_unavailable", "Map data is temporarily unavailable. Statistics are hidden.");
        document.getElementById("country-list").innerHTML = "";
      }}
    }}

    runMotion();
    await loadLandingLanguage();
    await loadMarketMap();
    document.addEventListener("atlas:i18n", () => renderMarketMap(marketMapData));
  </script>
</body>
</html>
"""
