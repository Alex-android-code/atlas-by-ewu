from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_control_center_buttons_have_click_handlers():
    html = (ROOT / "api" / "control_center.py").read_text(encoding="utf-8")

    assert "data-action-code" in html
    assert "runQuickAction" in html
    assert "data-nav-code" in html
    assert "activateNavigation" in html
    assert "runMatchingFromControlCenter" in html


def test_control_center_quick_actions_are_bound_to_real_routes_or_api():
    html = (ROOT / "api" / "control_center.py").read_text(encoding="utf-8")

    assert 'window.location.href = "/dashboard"' in html
    assert 'window.location.href = "/agent/dashboard"' in html
    assert 'window.location.href = "/ai?intent=job"' in html
    assert "/api/vacancies/${encodeURIComponent(vacancy.id)}/match" in html
    assert "No open vacancy found. Create or publish a vacancy first." in html
