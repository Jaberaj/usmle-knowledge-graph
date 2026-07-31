import json
from collections import Counter
from pathlib import Path

import pytest

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


def test_neurology_semantic_relationships() -> None:
    tables = load()
    disease_ids = {row["canonical_name"]: row["disease_id"] for row in tables["diseases"]}
    finding_names = {row["finding_id"]: row["name"] for row in tables["findings"]}
    by_disease: dict[str, set[str]] = {}
    for row in tables["disease_findings"]:
        by_disease.setdefault(row["disease_id"], set()).add(finding_names[row["finding_id"]])
    assert {"Fatigable ptosis", "No sensory loss"} <= by_disease[disease_ids["Myasthenia gravis"]]
    assert "Albuminocytologic dissociation" in by_disease[disease_ids["Guillain-Barre syndrome"]]
    assert "Diffusion restriction" in by_disease[disease_ids["Acute ischemic stroke"]]
    assert any(
        row["reference_id"] == "REF-NEUR-COV-001"
        and row["entity_id"] == disease_ids["Acute ischemic stroke"]
        and row["source_locator"]
        for row in tables["entity_references"]
    )


def _neurology_links() -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    tables = load()
    disease_ids = {row["canonical_name"]: row["disease_id"] for row in tables["diseases"]}
    labels = {
        "finding": {row["finding_id"]: row["name"] for row in tables["findings"]},
        "diagnostic": {row["diagnostic_id"]: row["name"] for row in tables["diagnostics"]},
        "treatment": {row["treatment_id"]: row["name"] for row in tables["treatments"]},
        "keyword": {row["keyword_id"]: row["keyword_text"] for row in tables["keywords"]},
        "presentation": {row["presentation_id"]: row["name"] for row in tables["presentations"]},
    }
    relation = {
        "finding": ("disease_findings", "disease_id", "finding_id"),
        "diagnostic": ("disease_diagnostics", "disease_id", "diagnostic_id"),
        "treatment": ("disease_treatments", "disease_id", "treatment_id"),
        "keyword": ("disease_keywords", "disease_id", "keyword_id"),
        "presentation": ("disease_presentations", "disease_id", "presentation_id"),
    }
    output: dict[str, dict[str, str]] = {}
    for kind, (table, disease_field, linked_field) in relation.items():
        for item in tables[table]:
            output.setdefault(kind + item[disease_field], {})[labels[kind][item[linked_field]]] = (
                item.get("clinical_context")
                or item.get("explanation")
                or item.get("distinguishing_value")
                or item.get("key_positive_clues")
                or ""
            )
    return disease_ids, output


@pytest.mark.parametrize(
    ("disease", "kind", "expected"),
    [
        ("Acute ischemic stroke", "diagnostic", "Point-of-care glucose"),
        ("Large-vessel occlusion stroke", "diagnostic", "CT angiography head and neck"),
        ("Subarachnoid hemorrhage", "diagnostic", "CT angiography head and neck"),
        (
            "Intracerebral hemorrhage",
            "treatment",
            "Stroke-unit stabilization and swallow screening",
        ),
        ("Cerebral venous sinus thrombosis", "keyword", "Diffusion restriction"),
        ("Carotid artery dissection", "presentation", "Acute focal neurologic deficit"),
        ("First unprovoked seizure", "diagnostic", "Electroencephalography"),
        ("Status epilepticus", "treatment", "Benzodiazepine seizure termination"),
        ("Nonconvulsive status epilepticus", "diagnostic", "Electroencephalography"),
        ("Absence seizure", "finding", "Three-hertz spike-and-wave"),
        ("Infantile spasms", "finding", "Hypsarrhythmia"),
        ("Psychogenic nonepileptic seizures", "diagnostic", "Electroencephalography"),
        ("Acute bacterial meningitis", "finding", "Low CSF glucose"),
        (
            "Acute bacterial meningitis",
            "treatment",
            "Immediate empiric antibiotics without unnecessary delay",
        ),
        ("HSV encephalitis", "finding", "Temporal-lobe abnormalities"),
        ("Brain abscess", "treatment", "Avoid routine lumbar puncture with mass lesion"),
        ("Cryptococcal meningitis", "diagnostic", "Lumbar puncture with CSF analysis"),
        ("Multiple sclerosis", "finding", "Dawson fingers"),
        ("Neuromyelitis optica spectrum disorder", "finding", "Aquaporin-4 antibodies"),
        ("Guillain-Barre syndrome", "diagnostic", "Serial respiratory measurements"),
        (
            "Guillain-Barre syndrome",
            "treatment",
            "Avoid corticosteroids because they are ineffective for typical GBS",
        ),
        ("Myasthenia gravis", "finding", "No sensory loss"),
        ("Lambert-Eaton myasthenic syndrome", "keyword", "Facilitation with repeated use"),
        ("Myasthenic crisis", "treatment", "Airway and ventilatory support"),
        ("Parkinson disease", "keyword", "Pill-rolling tremor"),
        ("Dementia with Lewy bodies", "finding", "Lewy bodies"),
        ("Normal-pressure hydrocephalus", "finding", "Ventriculomegaly"),
        ("Middle cerebral artery syndrome", "presentation", "Acute focal neurologic deficit"),
        ("Brown-Sequard syndrome", "keyword", "Brown-Sequard syndrome"),
        (
            "Anterior spinal artery syndrome",
            "presentation",
            "Acute focal neurologic deficit",
        ),
    ],
)
def test_neurology_phase2_semantic_relationships(disease: str, kind: str, expected: str) -> None:
    disease_ids, links = _neurology_links()
    assert disease_ids[disease]
    assert expected in links[kind + disease_ids[disease]]
    assert links[kind + disease_ids[disease]][expected]


def test_neurology_relationship_vectors_and_algorithm_shapes_are_not_templated() -> None:
    tables = load()
    neuro_ids = {
        row["disease_id"]
        for row in tables["diseases"]
        if row["organ_system_primary"] == "Neurology"
    }
    relationship_specs = (
        ("disease_presentations", "disease_id"),
        ("disease_findings", "disease_id"),
        ("disease_keywords", "disease_id"),
        ("disease_diagnostics", "disease_id"),
        ("disease_treatments", "disease_id"),
        ("disease_differentials", "source_disease_id"),
        ("disease_complications", "disease_id"),
    )
    vectors: dict[str, list[int]] = {disease_id: [] for disease_id in neuro_ids}
    for table, field in relationship_specs:
        counts = Counter(row[field] for row in tables[table] if row[field] in neuro_ids)
        for disease_id in neuro_ids:
            vectors[disease_id].append(counts[disease_id])
    assert max(Counter(map(tuple, vectors.values())).values()) < 50
    neuro_steps = [
        step for step in tables["algorithm_steps"] if step["algorithm_id"].startswith("ALG-NEUR-")
    ]
    assert not any(
        "explicit contingency" in step["prompt_or_action"].lower() for step in neuro_steps
    )
    assert not any("unsafe branch—" in step["prompt_or_action"].lower() for step in neuro_steps)
    decisions = [step for step in neuro_steps if step["node_type"] == "decision"]
    assert all(
        not step["next_node_if_true"] or step["next_node_if_true"] != step["next_node_if_false"]
        for step in decisions
    )


@pytest.mark.parametrize(
    ("disease", "kind", "expected"),
    [
        ("Acute ischemic stroke", "finding", "Diffusion restriction"),
        ("Subarachnoid hemorrhage", "finding", "Xanthochromia"),
        ("Cerebral venous sinus thrombosis", "diagnostic", "CT venography or MR venography"),
        ("Carotid artery dissection", "keyword", "Diffusion restriction"),
        ("Childhood absence epilepsy", "finding", "Three-hertz spike-and-wave"),
        ("Absence seizure", "finding", "Three-hertz spike-and-wave"),
        ("Infantile spasms", "finding", "Hypsarrhythmia"),
        ("West syndrome", "finding", "Hypsarrhythmia"),
        ("Juvenile myoclonic epilepsy", "keyword", "Morning myoclonus"),
        ("Temporal-lobe epilepsy", "keyword", "Deja vu aura"),
        ("Lennox-Gastaut syndrome", "keyword", "Slow spike-and-wave"),
        ("Dravet syndrome", "keyword", "Prolonged febrile seizures in infancy"),
    ],
)
def test_phase4a_vascular_and_epilepsy_ownership(disease: str, kind: str, expected: str) -> None:
    disease_ids, links = _neurology_links()
    assert expected in links[kind + disease_ids[disease]]
    assert links[kind + disease_ids[disease]][expected]
