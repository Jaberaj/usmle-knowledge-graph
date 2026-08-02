"""Regression coverage for retirement of generic migraine diagnostic links."""

import copy
import csv
import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("acceptance", ROOT / "scripts/neurology_phase4b2_acceptance.py")
assert SPEC and SPEC.loader
ACCEPTANCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ACCEPTANCE)
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


def _curation():
    entries = yaml.safe_load((ROOT / "data/curation/neurology/headache.yaml").read_text())
    return {entry["disease_id"]: entry for entry in entries}


@pytest.mark.parametrize("relationship_id", RETIRED)
def test_retired_migraine_relationship_is_absent_everywhere(relationship_id: str) -> None:
    assert relationship_id not in {row["disease_diagnostic_id"] for row in _source()}
    assert relationship_id not in {
        r["relationship"]["disease_diagnostic_id"]
        for entry in _curation().values() for r in entry.get("diagnostics", [])
    }


def test_affected_diseases_keep_a_synchronized_diagnostic_pathway() -> None:
    source = _source()
    curation = _curation()
    for disease_id in AFFECTED:
        source_ids = {row["disease_diagnostic_id"] for row in source if row["disease_id"] == disease_id}
        curation_ids = {r["relationship"]["disease_diagnostic_id"] for r in curation[disease_id]["diagnostics"]}
        assert source_ids and source_ids == curation_ids


def test_retired_ids_have_no_reference_links_or_wip_marker() -> None:
    with (ROOT / "data/source/relationships/entity_references.csv").open() as handle:
        links = list(csv.DictReader(handle))
    assert not {row["entity_id"] for row in links} & set(RETIRED)
    payload = str([row for row in _source() if row["disease_id"] in AFFECTED]) + str(_curation())
    assert "wip" not in payload.lower()


@pytest.mark.parametrize(
    ("disease_id", "diagnostic_id", "label"),
    [
        ("DIS-NEUR-054", "DIA-NEUR-BA3198A14E32", "CT angiography"),
        ("DIS-NEUR-054", "DIA-NEUR-D793FB579BDF", "Lumbar puncture"),
        ("DIS-NEUR-CHRONICMIGRAINE", "DIA-NEUR-A685E95FF812", "MRI"),
        ("DIS-NEUR-VESTIBULARMIGRAINE", "DIA-NEUR-BA3198A14E32", "CT angiography"),
        ("DIS-NEUR-054", "DIA-NEUR-A685E95FF812", "MRI"),
    ],
)
def test_production_leak_detector_rejects_seeded_routine_testing(disease_id, diagnostic_id, label) -> None:
    rows = copy.deepcopy(_source())
    rows.append({"disease_diagnostic_id": "DDG-TEST", "disease_id": disease_id, "diagnostic_id": diagnostic_id, "role": "secondary_cause_evaluation" if label == "MRI" else "initial", "clinical_context": f"Routine {label} for migraine."})
    diseases = {d: {"canonical_name": next(e["canonical_name"] for e in _curation().values() if e["disease_id"] == d)} for d in AFFECTED}
    assert ACCEPTANCE.compute_migraine_diagnostic_leaks(rows, diseases)


def test_valid_conditional_secondary_cause_relationship_is_not_a_leak() -> None:
    rows = [{"disease_diagnostic_id": "DDG-TEST", "disease_id": "DIS-NEUR-054", "diagnostic_id": "DIA-NEUR-A685E95FF812", "role": "secondary_cause_evaluation", "clinical_context": "MRI is not routine; obtain only for a first or atypical presentation with a persistent focal neurologic deficit to evaluate a secondary structural or vascular cause."}]
    diseases = {"DIS-NEUR-054": {"canonical_name": "Migraine with aura"}}
    assert ACCEPTANCE.compute_migraine_diagnostic_leaks(rows, diseases) == []
