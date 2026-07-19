from types import SimpleNamespace

from fastapi import HTTPException

from api import app as app_module
from api.main_interface import CORPORATE_HTML, EMPLOYEE_HTML, EMPLOYER_HTML, GDPR_HTML, LANDING_HTML


def request(cookies=None, headers=None, host="unit-test", scheme="https"):
    return SimpleNamespace(
        cookies=cookies or {},
        headers=headers or {},
        client=SimpleNamespace(host=host),
        url=SimpleNamespace(scheme=scheme),
    )


def test_landing_uses_central_nervous_system_preloader():
    assert "ATLAS |" in LANDING_HTML
    assert "id=\"atlas-preloader\"" in LANDING_HTML
    assert "id=\"atlas-intro-video\"" in LANDING_HTML
    assert "/static/video/atlas-intro.webm" in LANDING_HTML
    assert "/static/video/atlas-intro.mp4" in LANDING_HTML
    assert "dashboard" in LANDING_HTML
    assert "highlight-green" in LANDING_HTML
    assert "prefers-reduced-motion" in LANDING_HTML


def test_role_pages_contain_expected_workspaces():
    assert "/agent/onboarding" in EMPLOYEE_HTML
    assert "CRM" in EMPLOYER_HTML
    assert "Enterprise Security Center" in CORPORATE_HTML
    assert "API" in CORPORATE_HTML
    assert "GDPR / RODO" in GDPR_HTML


def test_new_routes_are_registered_and_crm_pages_are_protected():
    paths = {route.path for route in app_module.app.routes if hasattr(route, "path")}
    assert "/" in paths
    assert "/employee" in paths
    assert "/employer" in paths
    assert "/corporate" in paths
    assert "/crm/login" in paths
    assert "/gdpr" in paths

    assert "ATLAS Login" in app_module.crm_login()
    assert "ATLAS Login" in app_module.dashboard(request())
    assert "ATLAS Login" in app_module.control_center(request())

    with pytest_raises_403():
        app_module.get_dashboard(request())


class pytest_raises_403:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        assert exc_type is HTTPException
        assert exc.status_code == 403
        return True
