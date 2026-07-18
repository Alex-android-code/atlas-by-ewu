# ATLAS Brand System

Created: 2026-07-18  
Scope: ATLAS by EWU product interface, CRM, dashboard, AI workspace, navigation, marketing entry points.

## Non-Negotiable Brand DNA

ATLAS keeps the approved identity: metallic gold 3D letter A, realistic blue Earth behind the A, a luminous orbit around the Earth, silver ATLAS wordmark, gold `by EWU`, and a premium cinematic technology tone built from dark navy, blue, gold, silver and cold white.

This is not a rebrand. Any reconstruction must make ATLAS feel more polished and professional while staying instantly recognizable as the same ATLAS.

## Approved Logo Assets

The project uses `api/static/brand` as the live equivalent of the requested `public/brand` structure.

| Usage | Live alias | Approved source |
| --- | --- | --- |
| Primary logo | `api/static/brand/atlas-logo-primary.png` | `api/static/assets/atlas_brand_primary.png` |
| Primary web image | `api/static/brand/atlas-logo-primary.webp` | `api/static/assets/atlas_brand_header_transparent.webp` |
| Horizontal logo | `api/static/brand/atlas-logo-horizontal.png` | `api/static/assets/atlas_brand_horizontal_transparent.png` |
| Compact mark | `api/static/brand/atlas-logo-compact.png` | `api/static/assets/atlas_brand_mark.png` |
| Compact mark web image | `api/static/brand/atlas-logo-compact.webp` | `api/static/assets/atlas_brand_mark.webp` |
| Symbol | `api/static/brand/atlas-symbol.png` | `api/static/assets/atlas_brand_icon.png` |
| Dark-context logo | `api/static/brand/atlas-logo-dark.png` | `api/static/assets/atlas_brand_header_blend.png` |
| Light-context logo | `api/static/brand/atlas-logo-light.png` | `api/static/assets/atlas_brand_header_transparent.png` |

The original files in `api/static/assets` are preserved and must not be edited in place. A backup archive is stored at `docs/brand/backup/atlas-brand-assets-20260718.zip`.

## Missing Formats

The audit did not find an SVG/vector master, true monochrome dark logo, true monochrome light logo, or `.ico` favicon generated from an approved source. Do not invent these formats by redesigning the logo; create them only from approved source artwork after owner approval.

## Logo Usage

Primary logo: login, presentation screens, landing hero and formal brand surfaces.  
Horizontal logo: desktop navigation and wide headers.  
Compact mark: sidebar, mobile header, loading states and dense product areas.  
Symbol: favicon-style contexts, app badges and square placements.

Minimum size: primary logo should not render below 180px wide; horizontal logo should not render below 122px wide; compact mark and symbol should not render below 32px square.

Clearspace: keep at least the visual width of the gold `by EWU` letter height around the full logo. For compact mark and symbol, keep at least 20 percent of the asset width as empty space.

Placement: prefer dark navy or controlled glass surfaces. Avoid busy backgrounds unless the logo is in a protected header or hero area.

## Forbidden Logo Changes

Do not simplify the logo into a random letter A. Do not replace Earth with an abstract sphere. Do not move the orbit from the Earth to the letter. Do not remove `by EWU`. Do not recolor the gold A, silver ATLAS wordmark or blue Earth. Do not stretch, skew, crop, rotate, blur, flatten, add extra effects, or use an unapproved alternative logo.

## Audited Color Tokens

Colors were audited from approved assets and existing UI styles, then normalized in `api/components/design_system.py`.

| Token | Value | Use |
| --- | --- | --- |
| `--atlas-navy-950` | `#05070d` | primary app background |
| `--atlas-navy-925` | `#001020` | logo-dark audited base |
| `--atlas-navy-900` | `#090d18` | secondary background |
| `--atlas-navy-850` | `#0b1324` | panels and deep sections |
| `--atlas-blue-800` | `#002050` | Earth/technology depth |
| `--atlas-blue-700` | `#003070` | structured blue accents |
| `--atlas-blue-600` | `#004090` | data and AI surface accents |
| `--atlas-blue-500` | `#0060c0` | controlled glow/highlight |
| `--atlas-gold-700` | `#a06010` | dark metallic gold |
| `--atlas-gold-600` | `#b06010` | audited gold shadow |
| `--atlas-gold-500` | `#d6b25e` | product gold accent |
| `--atlas-gold-400` | `#ffc040` | logo/orbit highlight |
| `--atlas-gold-300` | `#f0d58b` | soft gold text/accent |
| `--atlas-silver-600` | `#a0a0a0` | secondary metallic text |
| `--atlas-silver-500` | `#d0d0d0` | silver UI details |
| `--atlas-silver-300` | `#eef1f6` | cold text primary |
| `--atlas-white` | `#ffffff` | high contrast text |
| `--atlas-ai-glow` | `rgba(0,96,192,0.42)` | AI-only glow |

Status colors remain functional and restrained: success `#4ade80`, warning `#f7c66a`, danger `#fb7185`, info `#38bdf8`.

## Contrast

Use `--atlas-text-primary` on dark navy backgrounds. Use `--atlas-text-secondary` for metadata and secondary labels. Gold text should be reserved for important states and short labels, not long paragraphs. Light theme work must keep navy anchors, gold accents and silver neutrals so it still reads as ATLAS.

## Typography

Use the project font token `--atlas-font`: Inter with system UI fallbacks. Product screens should use dense, professional hierarchy. Reserve large display type for true hero surfaces; dashboard, CRM and AI workspace panels should use compact headings and clear labels.

## Iconography

Use clean technical icons with consistent stroke weight. Icons may use silver, cold white or muted blue. Gold icons are reserved for selected states, premium/enterprise actions and critical CTA emphasis.

## Gold Rules

Gold is a premium accent, not a default fill. Use it for key CTA, active premium functions, important metrics, selected states, enterprise indicators and brand elements. Do not apply gold simultaneously to every button, border, icon, card, table and title in the same view.

## AI Glow Rules

AI glow uses controlled blue light, not broad decorative gradients. Use `--atlas-ai-glow` around AI workspace focus states, active model indicators and subtle processing states. Avoid large ornamental glow fields that make operational screens noisy.

## Correct Use

Use the compact mark in dense navigation. Use the primary logo on login and hero surfaces. Keep dark navy product backgrounds. Let gold appear as a selective signal. Keep Earth, orbit, metallic A, silver ATLAS and gold `by EWU` intact.

## Incorrect Use

Do not create a new logo concept. Do not remove `by EWU`. Do not make a flat single-letter A. Do not turn the product into a generic light SaaS interface. Do not flood the UI with gold borders and buttons. Do not use uncontrolled blue glow behind ordinary tables or forms.
