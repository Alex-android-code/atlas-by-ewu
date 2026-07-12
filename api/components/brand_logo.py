"""ATLAS by EWU brand logo component."""


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
  width: 264px;
  height: auto;
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


BRAND_LOGO_HTML = """
<a class="brand-logo" href="/" aria-label="ATLAS by EWU">
  <picture class="brand-logo-picture">
    <source srcset="/static/assets/atlas_brand_header_transparent.webp?v=20260712-header-webp" type="image/webp" />
    <img class="brand-logo-image" src="/static/assets/atlas_brand_header_transparent.png?v=20260712-header-transparent" alt="ATLAS by EWU" />
  </picture>
  <span class="brand-logo-caption" data-i18n="brand.caption">Connecting talent. Building futures.</span>
</a>
"""
