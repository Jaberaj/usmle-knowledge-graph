"""Regression coverage for the cerebral toxoplasmosis vertical slice."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from usmle_kb.pipeline import build_bundles, load

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "phase4b_acceptance", ROOT / "scripts/neurology_phase4b2_acceptance.py"
)
assert SPEC and SPEC.loader
ACCEPTANCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ACCEPTANCE)
compute_infection_view_errors = ACCEPTANCE.compute_infection_view_errors
compute_toxoplasmosis_ownership_errors = ACCEPTANCE.compute_toxoplasmosis_ownership_errors
norm = ACCEPTANCE.norm
TOXO = "DIS-NEUR-163"
RELATIONS = {
    "disease_presentations": "DPR-NEUR-BF769AEA8DE9",
    "disease_findings": "DNF-NEUR-A69D9062E6B0",
    "disease_diagnostics": "DDG-NEUR-BFAFD44E6B7E",
    "disease_treatments": "DTR-NEUR-290D23F11101",
    "disease_differentials": "DFL-NEUR-6B1173D8B724",
}


def _tables():
    return load()


def _views():
    base = ROOT / "data/curation/neurology"
    infection = {e["disease_id"]: e for e in yaml.safe_load((base / "infection.yaml").read_text())}
    mapping = yaml.safe_load((base / "infection_view_mapping.yaml").read_text())
    views = {
        view: yaml.safe_load((base / f"infection_{view}.yaml").read_text()) or []
        for view in ("meningitis", "encephalitis", "focal_opportunistic", "other")
    }
    return infection, mapping, views


def _ownership_errors(tables):
    diseases = {r["disease_id"]: r for r in tables["diseases"]}
    return compute_toxoplasmosis_ownership_errors(
        tables["disease_findings"],
        tables["disease_diagnostics"],
        tables["disease_treatments"],
        tables["disease_differentials"],
        diseases,
    )


def test_source_identity_relationship_ids_and_foreign_keys() -> None:
    tables = _tables()
    disease = [r for r in tables["diseases"] if r["disease_id"] == TOXO]
    assert len(disease) == 1 and disease[0]["canonical_name"] == "Cerebral toxoplasmosis"
    foreign = {
        "disease_presentations": "presentation_id",
        "disease_findings": "finding_id",
        "disease_diagnostics": "diagnostic_id",
        "disease_treatments": "treatment_id",
    }
    catalogs = {
        "presentation_id": "presentations",
        "finding_id": "findings",
        "diagnostic_id": "diagnostics",
        "treatment_id": "treatments",
    }
    for table, relation_id in RELATIONS.items():
        key = next(iter(tables[table][0]))
        rows = [r for r in tables[table] if r[key] == relation_id]
        assert len(rows) == 1
        row = rows[0]
        assert row.get("disease_id", row.get("source_disease_id")) == TOXO
        if table in foreign:
            assert row[foreign[table]] in {
                r[foreign[table]] for r in tables[catalogs[foreign[table]]]
            }


def test_entity_references_resolve_only_to_this_slice() -> None:
    tables = _tables()
    refs = [
        r
        for r in tables["entity_references"]
        if r["entity_reference_id"].startswith("ER-NEUR-TOXO-")
    ]
    assert len(refs) == len({r["entity_reference_id"] for r in refs}) == 8
    assert {r["reference_id"] for r in refs} == {"REF-NEUR-COV-005", "REF-NEUR-COV-006"}
    assert all(r["entity_id"] == TOXO or r["entity_id"] in RELATIONS.values() for r in refs)


@pytest.mark.parametrize(
    ("table", "field", "expected"),
    [
        ("disease_presentations", "relationship_role", "common"),
        ("disease_findings", "presence", "present"),
        ("disease_findings", "relationship_role", "supportive"),
        ("disease_diagnostics", "role", "initial"),
        ("disease_treatments", "role", "disease_directed"),
    ],
)
def test_relationship_enums_and_statuses(table: str, field: str, expected: str) -> None:
    tables = _tables()
    key = next(iter(tables[table][0]))
    row = next(r for r in tables[table] if r[key] == RELATIONS[table])
    assert row[field] == expected
    assert row["source_status"] == "partially_source_supported"
    assert row.get("source_review_status", "source_checked") == "source_checked"
    assert row.get("medical_review_status", "needs_medical_review") == "needs_medical_review"


def test_relationships_exclude_generic_phase4b_skeletons() -> None:
    tables = _tables()
    banned = (
        "timing and phenotype determine sensitivity",
        "interpreted against the disease-specific mimics",
        "linked because its timing and associated examination",
        "absence of expected syndrome features prompts",
        "expected to provide the disease-specific result stated",
        "draft content pending review",
        "use the linked illness script",
    )
    for table, relation_id in RELATIONS.items():
        key = next(iter(tables[table][0]))
        text = " ".join(next(r for r in tables[table] if r[key] == relation_id).values())
        assert not any(term in norm(text) for term in banned)


def test_presentation_and_finding_semantics() -> None:
    tables = _tables()
    p = next(
        r
        for r in tables["disease_presentations"]
        if r["disease_presentation_id"] == RELATIONS["disease_presentations"]
    )
    f = next(
        r
        for r in tables["disease_findings"]
        if r["disease_finding_id"] == RELATIONS["disease_findings"]
    )
    assert all(
        term in norm(" ".join(p.values()))
        for term in (
            "immunocompromised",
            "subacute focal neurologic deficit",
            "headache seizure altered mental status or fever",
            "do not exclude",
            "mass effect",
        )
    )
    assert all(
        term in norm(" ".join(f.values()))
        for term in (
            "multiple",
            "solitary lesion does not exclude",
            "nonspecific",
            "primary cns lymphoma",
            "neither establishes",
        )
    )


def test_diagnostic_and_treatment_semantics() -> None:
    tables = _tables()
    d = next(
        r
        for r in tables["disease_diagnostics"]
        if r["disease_diagnostic_id"] == RELATIONS["disease_diagnostics"]
    )
    t = next(
        r
        for r in tables["disease_treatments"]
        if r["disease_treatment_id"] == RELATIONS["disease_treatments"]
    )
    assert all(
        term in norm(" ".join(d.values()))
        for term in (
            "immunocompromised",
            "stabilize",
            "not independently diagnostic",
            "primary cns lymphoma",
            "reconsideration",
        )
    )
    assert all(
        term in norm(" ".join(t.values()))
        for term in (
            "should not await biopsy",
            "allergy cytopenia risk organ function pregnancy",
            "does not by itself prove",
            "lack of expected improvement",
            "blood counts",
            "radiologic response",
        )
    )


def test_one_way_differential_has_bidirectional_distinction_without_reverse() -> None:
    tables = _tables()
    rows = [
        r
        for r in tables["disease_differentials"]
        if r["source_disease_id"] == TOXO and r["competing_disease_id"] == "DIS-NEUR-135"
    ]
    assert len(rows) == 1 and rows[0]["differential_link_id"] == RELATIONS["disease_differentials"]
    assert all(
        rows[0][field]
        for field in (
            "findings_favoring_target",
            "findings_favoring_competitor",
            "key_negative_findings",
            "next_test_to_distinguish",
        )
    )
    assert not any(
        r["source_disease_id"] == "DIS-NEUR-135" and r["competing_disease_id"] == TOXO
        for r in tables["disease_differentials"]
    )


def test_acceptance_assertions_pass_for_repository_fixture() -> None:
    assert _ownership_errors(_tables()) == []


@pytest.mark.parametrize(
    ("table", "relation_id", "field", "value", "assertion"),
    [
        (
            "disease_findings",
            RELATIONS["disease_findings"],
            "presence",
            "negative",
            "toxoplasmosis_ring_enhancing_lesion_supportive",
        ),
        (
            "disease_diagnostics",
            RELATIONS["disease_diagnostics"],
            "role",
            "confirmatory",
            "toxoplasmosis_mri_brain_with_contrast_initial",
        ),
        (
            "disease_treatments",
            RELATIONS["disease_treatments"],
            "role",
            "rescue",
            "toxoplasmosis_pathogen_directed_therapy",
        ),
        (
            "disease_differentials",
            RELATIONS["disease_differentials"],
            "relative_priority",
            "2",
            "toxoplasmosis_primary_cns_lymphoma_differential",
        ),
        (
            "disease_differentials",
            RELATIONS["disease_differentials"],
            "next_test_to_distinguish",
            "",
            "toxoplasmosis_lymphoma_bidirectional_distinction",
        ),
    ],
)
def test_each_toxoplasmosis_acceptance_assertion_fails_independently(
    table, relation_id, field, value, assertion
) -> None:
    tables = copy.deepcopy(_tables())
    key = next(iter(tables[table][0]))
    next(r for r in tables[table] if r[key] == relation_id)[field] = value
    assert assertion in {e["assertion_id"] for e in _ownership_errors(tables)}


def test_canonical_mapping_and_generated_view_match() -> None:
    infection, mapping, views = _views()
    assert mapping[TOXO] == {"view": "focal_opportunistic"}
    assert sum(1 for records in views.values() for r in records if r["disease_id"] == TOXO) == 1
    assert (
        next(r for r in views["focal_opportunistic"] if r["disease_id"] == TOXO) == infection[TOXO]
    )
    assert compute_infection_view_errors(infection, mapping, views) == []


@pytest.mark.parametrize(
    "mutation", ["wrong_view", "missing", "duplicate", "mismatch", "missing_relationship"]
)
def test_view_checker_rejects_toxoplasmosis_invalid_fixtures(mutation: str) -> None:
    infection, mapping, views = _views()
    mapping, views = copy.deepcopy(mapping), copy.deepcopy(views)
    if mutation == "wrong_view":
        mapping[TOXO] = {"view": "other"}
    elif mutation == "missing":
        views["focal_opportunistic"] = [
            r for r in views["focal_opportunistic"] if r["disease_id"] != TOXO
        ]
    elif mutation == "duplicate":
        views["other"].append(
            copy.deepcopy(next(r for r in views["focal_opportunistic"] if r["disease_id"] == TOXO))
        )
    elif mutation == "mismatch":
        next(r for r in views["focal_opportunistic"] if r["disease_id"] == TOXO)[
            "canonical_name"
        ] = "Wrong"
    else:
        next(r for r in views["focal_opportunistic"] if r["disease_id"] == TOXO)["findings"] = []
    assert compute_infection_view_errors(infection, mapping, views)


def test_built_bundle_exports_toxoplasmosis_relationships_once() -> None:
    files = build_bundles(_tables())
    records = json.loads(files["diseases.json"].read_text())["records"]
    row = next(r for r in records if r["disease_id"] == TOXO)
    assert sum(r["disease_id"] == TOXO for r in records) == 1
    assert (
        "PRS-008" in row["presentation_ids"]
        and "DIA-NEUR-A685E95FF812" in row["diagnostic_ids"]
        and "TRT-NEUR-703266E6D90D" in row["treatment_ids"]
    )
    assert any(r["finding_id"] == "FND-NEUR-A2666BE46052" for r in row["findings"])
    assert any(r["competing_disease_id"] == "DIS-NEUR-135" for r in row["differentials"])


def test_final_provenance_statuses_are_source_supported() -> None:
    tables = _tables()
    disease = next(r for r in tables["diseases"] if r["disease_id"] == TOXO)
    finding = next(r for r in tables["findings"] if r["finding_id"] == "FND-NEUR-A2666BE46052")
    treatment = next(r for r in tables["treatments"] if r["treatment_id"] == "TRT-NEUR-703266E6D90D")
    for row in (disease, treatment):
        assert row["source_review_status"] == "source_checked"
        assert row["medical_review_status"] == "needs_medical_review"
        assert row["source_status"] == "partially_source_supported"
        assert row["human_review_status"] == "not_requested"
    assert finding["source_status"] == "partially_source_supported"
    assert finding["human_review_status"] == "not_requested"


def test_final_toxoplasmosis_slice_and_built_record_have_no_wip_markers() -> None:
    tables = _tables()
    source_rows = [
        next(r for r in tables["diseases"] if r["disease_id"] == TOXO),
        next(r for r in tables["findings"] if r["finding_id"] == "FND-NEUR-A2666BE46052"),
        next(r for r in tables["treatments"] if r["treatment_id"] == "TRT-NEUR-703266E6D90D"),
        *[r for r in tables["references"] if r["reference_id"] in {"REF-NEUR-COV-005", "REF-NEUR-COV-006"}],
        *[r for r in tables["entity_references"] if r["entity_reference_id"].startswith("ER-NEUR-TOXO-")],
    ]
    assert all("wip" not in json.dumps(row).lower() for row in source_rows)
    infection, _, _ = _views()
    assert "wip" not in json.dumps(infection[TOXO]).lower()
    record = next(r for r in json.loads(build_bundles(_tables())["diseases.json"].read_text())["records"] if r["disease_id"] == TOXO)
    assert "wip" not in json.dumps(record).lower()
