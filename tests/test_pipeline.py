import json

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
