import json
from pathlib import Path

from usmle_kb.pipeline import build_bundles, build_release, build_sqlite, load, validate


def test_seed_data_validates() -> None:
    assert validate(load()) == []


def test_builds_reconcile() -> None:
    tables = load()
    build_sqlite(tables)
    build_bundles(tables)
    manifest = json.loads(build_release(tables).read_text())
    assert manifest["record_counts"]["diseases"] >= 100
    assert manifest["checksums"]


def test_coverage_model_is_independent_of_human_review() -> None:
    tables = load()
    assert {row["human_review_status"] for row in tables["diseases"]} == {"not_requested"}
    assert all(
        row["source_status"] in {"unverified_ai_generated", "partially_source_supported"}
        for row in tables["diseases"]
    )
    build_bundles(tables)
    records = json.loads((Path("dist/json/diseases.json")).read_text())["records"]
    assert all("eligibility" in record for record in records)
