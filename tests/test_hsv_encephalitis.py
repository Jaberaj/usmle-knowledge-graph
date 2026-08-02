"""Focused regression coverage for the HSV encephalitis repair."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from usmle_kb.pipeline import load

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "phase4b_acceptance", ROOT / "scripts/neurology_phase4b2_acceptance.py"
)
assert SPEC and SPEC.loader
ACCEPTANCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ACCEPTANCE)

HSV = "DIS-NEUR-067"
DIAGNOSTIC = "DIA-NEUR-FC9D9ABE1F22"
TREATMENT = "TRT-NEUR-CB1D18701F10"
DIAGNOSTIC_RELATIONSHIP = "DDG-NEUR-2BCA185E49F3"
TREATMENT_RELATIONSHIP = "DTR-NEUR-3B31EC941CD0"


def _tables():
    return load()


def _ownership_errors(tables):
    diseases = {row["disease_id"]: row for row in tables["diseases"]}
    return ACCEPTANCE.compute_hsv_ownership_errors(
        tables["disease_diagnostics"], tables["disease_treatments"], diseases
    )


def _views():
    base = ROOT / "data/curation/neurology"
    infection = {entry["disease_id"]: entry for entry in yaml.safe_load((base / "infection.yaml").read_text())}
    mapping = yaml.safe_load((base / "infection_view_mapping.yaml").read_text())
    views = {
        view: yaml.safe_load((base / f"infection_{view}.yaml").read_text()) or []
        for view in ("meningitis", "encephalitis", "focal_opportunistic", "other")
    }
    return infection, mapping, views


def test_hsv_identity_relationships_and_foreign_keys_are_unique() -> None:
    tables = _tables()
    assert len([row for row in tables["diseases"] if row["disease_id"] == HSV]) == 1
    assert len([row for row in tables["diagnostics"] if row["diagnostic_id"] == DIAGNOSTIC]) == 1
    assert len([row for row in tables["treatments"] if row["treatment_id"] == TREATMENT]) == 1
    diagnostic = [row for row in tables["disease_diagnostics"] if row["disease_diagnostic_id"] == DIAGNOSTIC_RELATIONSHIP]
    treatment = [row for row in tables["disease_treatments"] if row["disease_treatment_id"] == TREATMENT_RELATIONSHIP]
    assert len(diagnostic) == len(treatment) == 1
    assert diagnostic[0]["disease_id"] == treatment[0]["disease_id"] == HSV
    assert diagnostic[0]["diagnostic_id"] == DIAGNOSTIC
    assert treatment[0]["treatment_id"] == TREATMENT
    assert not any(
        row["disease_id"] == HSV and row["diagnostic_id"] == DIAGNOSTIC and row["disease_diagnostic_id"] != DIAGNOSTIC_RELATIONSHIP
        for row in tables["disease_diagnostics"]
    )
    assert not any(
        row["disease_id"] == HSV and row["treatment_id"] == TREATMENT and row["disease_treatment_id"] != TREATMENT_RELATIONSHIP
        for row in tables["disease_treatments"]
    )


def test_hsv_provenance_and_statuses_are_final_without_wip() -> None:
    tables = _tables()
    references = {row["reference_id"]: row for row in tables["references"]}
    assert {"REF-NEUR-COV-007", "REF-NEUR-COV-008", "REF-NEUR-COV-009"} <= set(references)
    assert "archived" in references["REF-NEUR-COV-007"]["notes"].lower()
    assert references["REF-NEUR-COV-007"]["publication_year"] == "2008"
    links = [row for row in tables["entity_references"] if row["entity_reference_id"].startswith("ER-NEUR-HSV-")]
    assert {row["entity_reference_id"] for row in links} == {f"ER-NEUR-HSV-00{n}" for n in range(1, 6)}
    assert {row["entity_id"] for row in links} == {DIAGNOSTIC, TREATMENT, DIAGNOSTIC_RELATIONSHIP, TREATMENT_RELATIONSHIP}
    assert {row["reference_id"] for row in links} == {
        "REF-NEUR-COV-007",
        "REF-NEUR-COV-008",
        "REF-NEUR-COV-009",
    }
    assert all(row["reference_id"] in references for row in links)
    diagnostic = next(row for row in tables["diagnostics"] if row["diagnostic_id"] == DIAGNOSTIC)
    treatment = next(row for row in tables["treatments"] if row["treatment_id"] == TREATMENT)
    relationships = [
        next(row for row in tables["disease_diagnostics"] if row["disease_diagnostic_id"] == DIAGNOSTIC_RELATIONSHIP),
        next(row for row in tables["disease_treatments"] if row["disease_treatment_id"] == TREATMENT_RELATIONSHIP),
    ]
    for row in (diagnostic, treatment, *relationships):
        assert row["source_review_status"] == "source_checked"
        assert row["medical_review_status"] == "needs_medical_review"
        assert row["source_status"] == "partially_source_supported"
        assert row.get("human_review_status", "not_requested") == "not_requested"
        assert "wip" not in json.dumps(row).lower()
    infection, _, views = _views()
    assert "wip" not in json.dumps(infection[HSV]).lower()
    assert "wip" not in json.dumps(next(row for row in views["encephalitis"] if row["disease_id"] == HSV)).lower()


def test_hsv_relationships_have_required_semantics() -> None:
    tables = _tables()
    diagnostic = next(row for row in tables["disease_diagnostics"] if row["disease_diagnostic_id"] == DIAGNOSTIC_RELATIONSHIP)
    treatment = next(row for row in tables["disease_treatments"] if row["disease_treatment_id"] == TREATMENT_RELATIONSHIP)
    diagnostic_text = ACCEPTANCE.norm(" ".join(diagnostic.values()))
    treatment_text = ACCEPTANCE.norm(" ".join(treatment.values()))
    assert all(term in diagnostic_text for term in ("suspected encephalitis", "stabilize", "lumbar-puncture safety", "not routine screening", "repeat testing", "continue empiric acyclovir"))
    assert all(term in treatment_text for term in ("empiric acyclovir", "diagnostic studies are pending", "without waiting for pcr confirmation", "negative initial pcr", "renal function hydration", "infusion-related safety", "neurologic toxicity", "patient-specific"))


def test_hsv_acceptance_assertions_pass_for_repository_fixture() -> None:
    assert _ownership_errors(_tables()) == []


@pytest.mark.parametrize(
    ("table", "relationship_id", "field", "value"),
    [
        ("disease_treatments", TREATMENT_RELATIONSHIP, "disease_treatment_id", "removed"),
        ("disease_treatments", TREATMENT_RELATIONSHIP, "treatment_id", "TRT-WRONG"),
        ("disease_treatments", TREATMENT_RELATIONSHIP, "disease_id", "DIS-WRONG"),
        ("disease_treatments", TREATMENT_RELATIONSHIP, "role", "rescue"),
        ("disease_treatments", TREATMENT_RELATIONSHIP, "first_line", "false"),
        ("disease_treatments", TREATMENT_RELATIONSHIP, "clinical_context", "Treat when confirmed."),
        ("disease_treatments", TREATMENT_RELATIONSHIP, "board_exam_pearl", "PCR guides care."),
        ("disease_treatments", TREATMENT_RELATIONSHIP, "monitoring", "Monitor clinical response."),
        ("disease_treatments", TREATMENT_RELATIONSHIP, "source_status", "unverified_ai_generated"),
    ],
)
def test_hsv_empiric_acyclovir_mutations_fail(table: str, relationship_id: str, field: str, value: str) -> None:
    tables = copy.deepcopy(_tables())
    row = next(row for row in tables[table] if row["disease_treatment_id"] == relationship_id)
    row[field] = value
    assert "hsv_empiric_acyclovir" in {error["assertion_id"] for error in _ownership_errors(tables)}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("disease_diagnostic_id", "removed"),
        ("diagnostic_id", "DIA-WRONG"),
        ("disease_id", "DIS-WRONG"),
        ("role", "initial"),
        ("limitations", "Use as routine screening."),
        ("interpretation", "PCR is definitive."),
        ("clinical_context", "Test when convenient."),
        ("interpretation", "Await confirmation before treatment."),
        ("source_status", "unverified_ai_generated"),
    ],
)
def test_hsv_csf_pcr_mutations_fail(field: str, value: str) -> None:
    tables = copy.deepcopy(_tables())
    row = next(row for row in tables["disease_diagnostics"] if row["disease_diagnostic_id"] == DIAGNOSTIC_RELATIONSHIP)
    row[field] = value
    assert "hsv_csf_pcr" in {error["assertion_id"] for error in _ownership_errors(tables)}


def test_hsv_mapping_and_generated_view_match_canonical_entry() -> None:
    infection, mapping, views = _views()
    assert mapping[HSV] == {"view": "encephalitis"}
    assert sum(1 for records in views.values() for row in records if row["disease_id"] == HSV) == 1
    assert next(row for row in views["encephalitis"] if row["disease_id"] == HSV) == infection[HSV]
    assert ACCEPTANCE.compute_infection_view_errors(infection, mapping, views) == []


@pytest.mark.parametrize(
    "mutation", ["missing", "wrong_view", "duplicate", "mismatch", "missing_diagnostic", "missing_treatment"]
)
def test_hsv_view_checker_rejects_invalid_fixtures(mutation: str) -> None:
    infection, mapping, views = _views()
    mapping, views = copy.deepcopy(mapping), copy.deepcopy(views)
    entry = next(row for row in views["encephalitis"] if row["disease_id"] == HSV)
    if mutation == "missing":
        views["encephalitis"].remove(entry)
    elif mutation == "wrong_view":
        mapping[HSV] = {"view": "other"}
    elif mutation == "duplicate":
        views["other"].append(copy.deepcopy(entry))
    elif mutation == "mismatch":
        entry["canonical_name"] = "wrong"
    elif mutation == "missing_diagnostic":
        entry["diagnostics"] = [r for r in entry["diagnostics"] if r["relationship"]["disease_diagnostic_id"] != DIAGNOSTIC_RELATIONSHIP]
    else:
        entry["treatments"] = [r for r in entry["treatments"] if r["relationship"]["disease_treatment_id"] != TREATMENT_RELATIONSHIP]
    assert ACCEPTANCE.compute_infection_view_errors(infection, mapping, views)
