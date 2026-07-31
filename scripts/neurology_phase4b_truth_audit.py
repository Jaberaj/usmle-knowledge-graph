"""Computed, record-level truth audit for the Phase 4B Neurology scope."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"
CURATION = ROOT / "data" / "curation" / "neurology"
MODULES = ("headache.yaml", "infection.yaml", "demyelinating.yaml")
TEMPLATES = (
    "clinically relevant syndrome anchor",
    "contributes a defined finding pattern",
    "explicitly selected alternatives",
    "manifest-selected diagnostic pathway",
    "condition-specific abnormality",
    "changes the probability of",
    "explicit contingency",
    "unsafe branch—",
    "concrete positive and negative clues",
    "answers the explicit diagnostic question",
    "integrated with the concrete syndrome pattern",
    "timing and the specific false-negative",
    "anatomic, vascular, electrographic, or metabolic result",
    "disease-specific escalation pathway",
)
RELATIONS = (
    "disease_presentations",
    "disease_findings",
    "disease_keywords",
    "disease_diagnostics",
    "disease_treatments",
    "disease_differentials",
    "disease_complications",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized_template(text: str) -> str:
    text = re.sub(r"\b(?:[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,4})\b", "<ENTITY>", text)
    return re.sub(r"\s+", " ", text.lower()).strip()


def scope() -> tuple[dict[str, str], dict[str, str]]:
    disease_module: dict[str, str] = {}
    for filename in MODULES:
        for entry in yaml.safe_load((CURATION / filename).read_text(encoding="utf-8")):
            disease_module[entry["disease_id"]] = filename
    names = {r["disease_id"]: r["canonical_name"] for r in rows(SOURCE / "diseases.csv")}
    return disease_module, names


def audit() -> dict[str, object]:
    disease_module, names = scope()
    defects: list[dict[str, str | int]] = []
    for relation in RELATIONS:
        for row in rows(REL / f"{relation}.csv"):
            did = row.get("disease_id") or row.get("source_disease_id", "")
            if did not in disease_module:
                continue
            stable_id = next((value for key, value in row.items() if key.endswith("_id")), "")
            for field, text in row.items():
                if field.endswith("_id") or not text:
                    continue
                if any(template in text.lower() for template in TEMPLATES):
                    defects.append(
                        {
                            "manifest": disease_module[did],
                            "disease_id": did,
                            "disease_name": names[did],
                            "entity_or_relationship_type": relation,
                            "record_id": stable_id,
                            "field_name": field,
                            "exact_text": text,
                            "normalized_template": normalized_template(text),
                        }
                    )
    counts = Counter(str(item["normalized_template"]) for item in defects)
    for item in defects:
        item["occurrences"] = counts[str(item["normalized_template"])]
    empty_sections = []
    mapping = {
        "presentations": "disease_presentations.csv",
        "findings": "disease_findings.csv",
        "keywords": "disease_keywords.csv",
        "differentials": "disease_differentials.csv",
        "diagnostics": "disease_diagnostics.csv",
        "treatments": "disease_treatments.csv",
    }
    for section, filename in mapping.items():
        data = rows(REL / filename)
        field = "source_disease_id" if section == "differentials" else "disease_id"
        for did in disease_module:
            if not any(row[field] == did for row in data):
                empty_sections.append({"disease_id": did, "section": section})
    duplicate_ids = []
    contradictory_statuses = []
    for relation in RELATIONS:
        data = rows(REL / f"{relation}.csv")
        id_field = next(iter(data[0]))
        for stable_id, count in Counter(row[id_field] for row in data).items():
            if count > 1:
                duplicate_ids.append({"table": relation, "id": stable_id, "occurrences": count})
        for row in data:
            did = row.get("disease_id") or row.get("source_disease_id", "")
            if did not in disease_module:
                continue
            if (
                row.get("source_status") == "unverified_ai_generated"
                and row.get("source_review_status") == "source_checked"
            ):
                contradictory_statuses.append(
                    {"table": relation, "id": row[id_field], "reason": "unverified/source_checked"}
                )
            if (
                row.get("source_status") == "source_supported"
                and row.get("source_review_status") != "source_checked"
            ):
                contradictory_statuses.append(
                    {
                        "table": relation,
                        "id": row[id_field],
                        "reason": "supported without source_checked",
                    }
                )
    return {
        "scope_manifests": list(MODULES),
        "disease_records_by_module": dict(Counter(disease_module.values())),
        "template_defects": defects,
        "empty_sections": empty_sections,
        "duplicate_ids": duplicate_ids,
        "contradictory_source_statuses": contradictory_statuses,
        "computed_summary": {
            "phase4b_scoped_template_hits": len(defects),
            "empty_section_count": len(empty_sections),
            "duplicate_id_count": len(duplicate_ids),
            "contradictory_source_status_count": len(contradictory_statuses),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("before", "after"))
    stage = parser.parse_args().stage
    result = audit()
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    stem = reports / f"neurology_phase4b_truth_audit_{stage}"
    stem.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = result["computed_summary"]
    stem.with_suffix(".md").write_text(
        f"# Neurology Phase 4B truth audit ({stage})\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in summary.items())
        + "\n\nThe JSON report retains every detected record and normalized template.\n",
        encoding="utf-8",
    )
    if stage == "after" and any(summary.values()):
        raise SystemExit("Phase 4B acceptance gate failed; inspect the truth audit")


if __name__ == "__main__":
    main()
