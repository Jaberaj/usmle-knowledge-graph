"""Regression coverage for retirement of generic migraine diagnostic links."""

import csv
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
RETIRED = (
    "DDG-NEUR-D94A7BE5C619", "DDG-NEUR-C03160B99307", "DDG-NEUR-93F995CDAB2A",
    "DDG-NEUR-DDC6EF12BD79", "DDG-NEUR-F4338B07A44A", "DDG-NEUR-B26F1CC3CF96",
    "DDG-NEUR-BFCE6B2776A1", "DDG-NEUR-DF048BCE46C5", "DDG-NEUR-298644DED2BE",
    "DDG-NEUR-E507CD4C17EC", "DDG-NEUR-A961E30C9C8C", "DDG-NEUR-094CEAEEFC93",
)
AFFECTED = ("DIS-NEUR-054", "DIS-NEUR-055", "DIS-NEUR-VESTIBULARMIGRAINE", "DIS-NEUR-CHRONICMIGRAINE")


def _source():
    with (ROOT / "data/source/relationships/disease_diagnostics.csv").open() as handle:
        return list(csv.DictReader(handle))


def _curation_ids():
    entries = yaml.safe_load((ROOT / "data/curation/neurology/headache.yaml").read_text())
    return {r["relationship"]["disease_diagnostic_id"] for entry in entries for r in entry.get("diagnostics", [])}


@pytest.mark.parametrize("relationship_id", RETIRED)
def test_retired_migraine_relationship_is_absent_everywhere(relationship_id: str) -> None:
    assert relationship_id not in {row["disease_diagnostic_id"] for row in _source()}
    assert relationship_id not in _curation_ids()


def test_affected_diseases_keep_a_synchronized_diagnostic_pathway() -> None:
    source = _source()
    curation_ids = _curation_ids()
    for disease_id in AFFECTED:
        remaining = {row["disease_diagnostic_id"] for row in source if row["disease_id"] == disease_id}
        assert remaining and remaining <= curation_ids
