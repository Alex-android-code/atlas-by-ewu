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


def test_landing_keeps_atlas_brand_and_three_role_cards():
    assert "/static/brand/atlas-logo-primary.png" in LANDING_HTML
    assert "Ініціалізація AI-системи" in LANDING_HTML
    assert "Завантаження персональних агентів" in LANDING_HTML
    assert "Підготовка захищеного середовища" in LANDING_HTML
    assert "Працівник" in LANDING_HTML
    assert "Роботодавець" in LANDING_HTML
    assert "Корпорація" in LANDING_HTML
    assert "/gdpr" in LANDING_HTML
    assert "/crm/login" in LANDING_HTML
    assert "prefers-reduced-motion" in LANDING_HTML


def test_role_pages_contain_expected_workspaces():
    assert "Створення професійного профілю" in EMPLOYEE_HTML
    assert "Персональний AI-агент" in EMPLOYEE_HTML
    assert "AI-підбір кандидатів" in EMPLOYER_HTML
    assert "Доступ до CRM" in EMPLOYER_HTML
    assert "Enterprise Security Center" in CORPORATE_HTML
    assert "ERP, CRM та API інтеграції" in CORPORATE_HTML
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
