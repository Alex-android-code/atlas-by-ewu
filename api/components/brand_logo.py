"""ATLAS by EWU brand logo component."""

BRAND_ASSET_VERSION = "20260718-brand-system"
BRAND_LOGO_PRIMARY = f"/static/brand/atlas-logo-primary.png?v={BRAND_ASSET_VERSION}"
BRAND_LOGO_PRIMARY_WEBP = f"/static/brand/atlas-logo-primary.webp?v={BRAND_ASSET_VERSION}"
BRAND_LOGO_COMPACT = f"/static/brand/atlas-logo-compact.png?v={BRAND_ASSET_VERSION}"
BRAND_LOGO_COMPACT_WEBP = f"/static/brand/atlas-logo-compact.webp?v={BRAND_ASSET_VERSION}"


BRAND_LOGO_CSS = """
.brand-logo {
  display: inline-grid;
  align-items: center;
  justify-items: center;
  gap: 2px;
  color: var(--atlas-white);
  text-decoration: none;
  line-height: 1;
}
.brand-logo-image {
  display: block;
  width: auto;
  height: 147px;
  max-width: min(396px, calc(100vw - 96px));
  max-height: 147px;
  object-fit: contain;
}
.brand-logo-picture {
  display: block;
}
.brand-logo-caption {
  display: block;
  color: rgba(245, 217, 138, 0.88);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  text-shadow: 0 0 16px rgba(212, 175, 55, 0.38);
  white-space: nowrap;
}
"""


BRAND_LOGO_HTML = f"""
<a class="brand-logo" href="/" aria-label="ATLAS by EWU">
  <picture class="brand-logo-picture">
    <source srcset="{BRAND_LOGO_PRIMARY_WEBP}" type="image/webp" />
    <img class="brand-logo-image" src="{BRAND_LOGO_PRIMARY}" alt="ATLAS by EWU" />
  </picture>
  <span class="brand-logo-caption" data-i18n="brand.caption">Connecting talent. Building futures.</span>
</a>
"""


BRAND_MARK_HTML = f"""
<a class="brand-mark" href="/" aria-label="ATLAS by EWU">
  <picture>
    <source srcset="{BRAND_LOGO_COMPACT_WEBP}" type="image/webp" />
    <img class="brand-mark-image" src="{BRAND_LOGO_COMPACT}" alt="ATLAS by EWU" />
  </picture>
  <span class="brand-mark-text">
    <span class="brand-mark-name">ATLAS</span>
    <span class="brand-mark-subtitle">Workforce OS</span>
  </span>
</a>
"""
