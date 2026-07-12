"""Optional browser observability snippets for public pages."""

from __future__ import annotations

import os


def observability_head_html() -> str:
    ga_id = os.getenv("NEXT_PUBLIC_GA_MEASUREMENT_ID") or os.getenv("GA_MEASUREMENT_ID")
    clarity_id = os.getenv("NEXT_PUBLIC_CLARITY_PROJECT_ID") or os.getenv("CLARITY_PROJECT_ID")
    sentry_dsn = os.getenv("NEXT_PUBLIC_SENTRY_DSN") or os.getenv("SENTRY_DSN")
    parts: list[str] = []
    if ga_id:
        parts.append(
            f"""
  <script async src="https://www.googletagmanager.com/gtag/js?id={_escape_attr(ga_id)}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("js", new Date());
    gtag("config", "{_escape_js(ga_id)}", {{ anonymize_ip: true, send_page_view: false }});
  </script>"""
        )
    if clarity_id:
        parts.append(
            f"""
  <script>
    (function(c,l,a,r,i,t,y){{
      c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window, document, "clarity", "script", "{_escape_js(clarity_id)}");
  </script>"""
        )
    if sentry_dsn:
        parts.append(
            """
  <script src="https://browser.sentry-cdn.com/8.33.1/bundle.tracing.replay.min.js" crossorigin="anonymous"></script>
  <script>
    if (window.Sentry) {
      Sentry.init({
        dsn: "%s",
        tracesSampleRate: 0.05,
        replaysSessionSampleRate: 0,
        replaysOnErrorSampleRate: 0,
        beforeSend(event) {
          if (event.request) {
            delete event.request.cookies;
            delete event.request.headers;
          }
          return event;
        }
      });
    }
  </script>"""
            % _escape_js(sentry_dsn)
        )
    return "\n".join(parts)


def observability_body_html(page_name: str) -> str:
    return f"""
  <script>
    window.AtlasAnalytics = (() => {{
      const piiKeys = new Set(["first_name","last_name","name","email","phone","contact_email","contact_phone","documents","document_files","password","token"]);
      function safeParams(params = {{}}) {{
        const safe = {{}};
        for (const [key, value] of Object.entries(params || {{}})) {{
          const normalized = key.toLowerCase();
          if (piiKeys.has(normalized) || normalized.includes("email") || normalized.includes("phone") || normalized.includes("password") || normalized.includes("token")) continue;
          if (["string", "number", "boolean"].includes(typeof value) || value === null) safe[key] = value;
        }}
        safe.page = safe.page || "{_escape_js(page_name)}";
        safe.language = document.documentElement.lang || new URLSearchParams(location.search).get("lang") || "unknown";
        safe.device_type = matchMedia("(max-width: 760px)").matches ? "mobile" : "desktop";
        safe.traffic_source = document.referrer ? "referral" : "direct";
        return safe;
      }}
      function track(name, params = {{}}) {{
        const eventParams = safeParams(params);
        if (window.gtag) window.gtag("event", name, eventParams);
        if (window.clarity) window.clarity("event", name);
        fetch("/api/analytics/event", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ name, params: eventParams, actor_id: localStorage.getItem("atlas_user_id") || "anonymous" }}),
          keepalive: true
        }}).catch(() => {{}});
      }}
      window.addEventListener("error", () => track("api_error", {{ page: "{_escape_js(page_name)}" }}));
      window.addEventListener("unhandledrejection", () => track("api_error", {{ page: "{_escape_js(page_name)}" }}));
      document.addEventListener("click", (event) => {{
        const target = event.target.closest("[data-analytics-event]");
        if (target) track(target.dataset.analyticsEvent, target.dataset.analyticsParams ? JSON.parse(target.dataset.analyticsParams) : {{}});
      }});
      queueMicrotask(() => track("page_view", {{ page: "{_escape_js(page_name)}" }}));
      return {{ track, safeParams }};
    }})();
  </script>"""


def _escape_attr(value: str) -> str:
    return value.replace('"', "&quot;").replace("<", "").replace(">", "")


def _escape_js(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("<", "")
