"""Materialize one explicit, reviewable Neurology manifest entry per disease.

The files are real YAML and make every relationship selection visible in review
rather than inherited at build time.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
OUT = ROOT / "data" / "curation" / "neurology"

MODULES = (
    "vascular",
    "seizures",
    "headache",
    "infection",
    "demyelinating",
    "movement",
    "cognition",
    "neuromuscular",
    "peripheral_nerve",
    "spinal",
    "neuro_oncology",
    "pediatric",
    "toxic_metabolic",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def module(name: str) -> str:
    low = name.lower()
    if any(
        x in low
        for x in (
            "stroke",
            "hemorrhage",
            "vascular",
            "dissection",
            "moyamoya",
            "artery",
            "transient ischemic",
            "venous sinus",
        )
    ):
        return "vascular"
    if any(
        x in low for x in ("seizure", "epilepsy", "spasm", "status", "dravet", "lennox", "west")
    ):
        return "seizures"
    if any(x in low for x in ("headache", "migraine", "neuralgia", "intracranial hypotension")):
        return "headache"
    if any(
        x in low
        for x in (
            "mening",
            "encephal",
            "abscess",
            "syphilis",
            "borreliosis",
            "rabies",
            "leukoencephalopathy",
        )
    ):
        return "infection"
    if any(
        x in low
        for x in ("sclerosis", "demyel", "myelitis", "optic neuritis", "mog", "neuromyelitis")
    ):
        return "demyelinating"
    if any(
        x in low
        for x in (
            "parkinson",
            "tremor",
            "huntington",
            "wilson",
            "tourette",
            "dyskines",
            "dystonia",
            "akathisia",
            "hyperthermia",
            "serotonin",
        )
    ):
        return "movement"
    if any(
        x in low
        for x in (
            "dementia",
            "alzheimer",
            "delirium",
            "korsakoff",
            "wernicke",
            "sleep",
            "narcolepsy",
            "restless",
        )
    ):
        return "cognition"
    if any(
        x in low
        for x in (
            "myasthen",
            "muscular",
            "myopathy",
            "mcardle",
            "pompe",
            "motor neuron",
            "guillain",
            "rhabdo",
        )
    ):
        return "neuromuscular"
    if any(
        x in low
        for x in (
            "neuropathy",
            "palsy",
            "nerve",
            "radiculopathy",
            "carpal",
            "peroneal",
            "bell",
            "botulism",
        )
    ):
        return "peripheral_nerve"
    if any(x in low for x in ("cord", "cauda", "conus", "syringo", "brown-sequard", "spinal")):
        return "spinal"
    if any(
        x in low
        for x in (
            "glioma",
            "meningioma",
            "schwannoma",
            "adenoma",
            "metasta",
            "lymphoma",
            "medulloblastoma",
            "ependymoma",
            "astrocytoma",
            "hemangioblastoma",
            "craniopharyngioma",
            "hydrocephalus",
            "herniation",
            "intracranial pressure",
            "papilledema",
        )
    ):
        return "neuro_oncology"
    if any(
        x in low
        for x in (
            "cerebral palsy",
            "spinal muscular",
            "tuberous",
            "neurofibromatosis",
            "rett",
            "chiari",
            "dandy",
            "acute flaccid",
        )
    ):
        return "pediatric"
    return "toxic_metabolic"


def main() -> None:
    diseases = [
        r for r in rows(SOURCE / "diseases.csv") if r["organ_system_primary"] == "Neurology"
    ]
    tables = {
        name: rows(SOURCE / "relationships" / f"{name}.csv")
        for name in (
            "disease_presentations",
            "disease_findings",
            "disease_keywords",
            "disease_diagnostics",
            "disease_treatments",
            "disease_differentials",
            "disease_complications",
        )
    }
    lookups = {
        "presentations": {
            r["presentation_id"]: r["name"] for r in rows(SOURCE / "presentations.csv")
        },
        "findings": {r["finding_id"]: r["name"] for r in rows(SOURCE / "findings.csv")},
        "keywords": {r["keyword_id"]: r["keyword_text"] for r in rows(SOURCE / "keywords.csv")},
        "diagnostics": {r["diagnostic_id"]: r["name"] for r in rows(SOURCE / "diagnostics.csv")},
        "treatments": {r["treatment_id"]: r["name"] for r in rows(SOURCE / "treatments.csv")},
        "complications": {r["entity_id"]: r["name"] for r in rows(SOURCE / "complications.csv")},
        "diseases": {r["disease_id"]: r["canonical_name"] for r in diseases},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for disease in diseases:
        did = disease["disease_id"]
        entry: dict[str, object] = {"disease_id": did, "canonical_name": disease["canonical_name"]}
        specs = (
            (
                "presentations",
                "disease_presentations",
                "disease_id",
                "presentation_id",
                "presentations",
            ),
            ("findings", "disease_findings", "disease_id", "finding_id", "findings"),
            ("keywords", "disease_keywords", "disease_id", "keyword_id", "keywords"),
            ("diagnostics", "disease_diagnostics", "disease_id", "diagnostic_id", "diagnostics"),
            ("treatments", "disease_treatments", "disease_id", "treatment_id", "treatments"),
            (
                "complications",
                "disease_complications",
                "disease_id",
                "complication_id",
                "complications",
            ),
        )
        for key, table, disease_field, entity_field, lookup in specs:
            entry[key] = [
                {"entity": lookups[lookup][r[entity_field]], "relationship": r}
                for r in tables[table]
                if r[disease_field] == did
            ]
        entry["differentials"] = [
            {
                "competing_disease": lookups["diseases"].get(
                    r["competing_disease_id"], r["competing_disease_id"]
                ),
                "relationship": r,
            }
            for r in tables["disease_differentials"]
            if r["source_disease_id"] == did
        ]
        grouped[module(disease["canonical_name"])].append(entry)
    for name in MODULES:
        (OUT / f"{name}.yaml").write_text(
            yaml.safe_dump(grouped[name], allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
