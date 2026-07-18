import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_brand_asset_registry_points_to_existing_aliases():
    registry_path = ROOT / "docs" / "brand" / "BRAND_ASSET_REGISTRY.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    assert registry["brand"] == "ATLAS by EWU"
    assert registry["requested_public_structure_mapping"]["public/brand"] == "api/static/brand"
    assert (ROOT / registry["backup"]["path"]).exists()

    for asset in registry["approved_assets"]:
        assert (ROOT / asset["source"]).exists()
        assert (ROOT / asset["alias"]).exists()


def test_required_brand_aliases_exist():
    brand_dir = ROOT / "api" / "static" / "brand"
    required = {
        "atlas-logo-primary.png",
        "atlas-logo-horizontal.png",
        "atlas-logo-compact.png",
        "atlas-symbol.png",
        "atlas-logo-dark.png",
        "atlas-logo-light.png",
    }

    assert required.issubset({path.name for path in brand_dir.iterdir()})


def test_design_tokens_include_audited_brand_palette():
    css = (ROOT / "api" / "components" / "design_system.py").read_text(encoding="utf-8")

    for token in [
        "--atlas-navy-950",
        "--atlas-navy-900",
        "--atlas-blue-700",
        "--atlas-blue-500",
        "--atlas-gold-600",
        "--atlas-gold-500",
        "--atlas-gold-300",
        "--atlas-silver-500",
        "--atlas-silver-300",
        "--atlas-text-primary",
        "--atlas-text-secondary",
        "--atlas-info",
        "--atlas-ai-glow",
    ]:
        assert token in css


def test_brand_system_locks_core_identity():
    doc = (ROOT / "ATLAS_BRAND_SYSTEM.md").read_text(encoding="utf-8")

    assert "by EWU" in doc
    assert "Do not create a new logo concept" in doc
    assert "Earth" in doc
    assert "orbit" in doc


def test_dashboard_exposes_candidate_photo_workflow():
    dashboard = (ROOT / "api" / "dashboard.py").read_text(encoding="utf-8")

    assert "Фото для карты кандидата" in dashboard
    assert "candidate-photo-preview" in dashboard
    assert "Карты кандидатов" in dashboard
    assert "uploadCandidatePhoto" in dashboard
    assert "/api/candidates/${encodeURIComponent(candidateId)}/photo" in dashboard
