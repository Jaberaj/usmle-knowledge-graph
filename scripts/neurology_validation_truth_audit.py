"""Truthful, data-derived audit for Neurology curation.

Unlike the Phase-3 summary, this report deliberately retains every offending
identifier and does not turn an unfixed defect into a zero-valued claim.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"
CURATION = ROOT / "data" / "curation" / "neurology"
REPORTS = ROOT / "reports"
GENERIC = (
    "clinically relevant syndrome anchor",
    "contributes a defined finding pattern",
    "explicitly selected alternatives",
    "manifest-selected diagnostic pathway",
    "condition-specific abnormality",
    "changes the probability of",
    "explicit contingency",
    "unsafe branch—do not delay",
    "the competing diagnoses are separated by the concrete positive and negative clues",
    "answers the explicit diagnostic question for this presentation",
    "integrated with the concrete syndrome pattern",
    "timing and the specific false-negative or nonspecific limitations",
    "the anatomic, vascular, electrographic, or metabolic result described by the illness script",
    "curated as a distinct cerebrovascular or epilepsy entity rather than a parent syndrome",
    "retained only when it directly expresses that syndrome-specific pattern",
    "concrete positive and negative clues",
    "disease-specific escalation pathway",
)
REQUIRED = {
    "disease_id",
    "canonical_name",
    "presentations",
    "findings",
    "keywords",
    "differentials",
    "diagnostics",
    "treatments",
    "complications",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized(text: str) -> str:
    text = re.sub(r"\b(?:[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,3})\b", "<NAME>", text)
    return re.sub(r"\s+", " ", text.lower()).strip()


def audit() -> dict[str, object]:
    diseases = {
        r["disease_id"]: r
        for r in read(SOURCE / "diseases.csv")
        if r["organ_system_primary"] == "Neurology"
    }
    manifests: dict[str, dict[str, object]] = {}
    phase4a_ids: set[str] = set()
    invalid_yaml: list[dict[str, str]] = []
    empty: list[str] = []
    missing: list[dict[str, object]] = []
    for path in sorted(CURATION.glob("*.yaml")):
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            invalid_yaml.append({"file": str(path.relative_to(ROOT)), "error": str(exc)})
            continue
        if not isinstance(payload, list) or not payload:
            empty.append(str(path.relative_to(ROOT)))
            continue
        for entry in payload:
            if not isinstance(entry, dict):
                missing.append({"file": str(path.relative_to(ROOT)), "missing": ["mapping entry"]})
                continue
            absent = sorted(REQUIRED - set(entry))
            if absent:
                missing.append({"disease_id": entry.get("disease_id", ""), "missing": absent})
            elif str(entry["disease_id"]) in manifests:
                missing.append(
                    {"disease_id": entry["disease_id"], "missing": ["duplicate manifest entry"]}
                )
            else:
                manifests[str(entry["disease_id"])] = entry
                if path.stem in {"vascular", "seizures"}:
                    phase4a_ids.add(str(entry["disease_id"]))
    non_explicit = sorted(set(diseases) - set(manifests))
    prose_rows = []
    for file in (
        "disease_presentations",
        "disease_findings",
        "disease_keywords",
        "disease_diagnostics",
        "disease_treatments",
        "disease_differentials",
        "disease_complications",
    ):
        for row in read(REL / f"{file}.csv"):
            did = row.get("disease_id") or row.get("source_disease_id")
            if did not in diseases:
                continue
            for field, text in row.items():
                if field.endswith("id") or not text:
                    continue
                if any(template in text.lower() for template in GENERIC):
                    prose_rows.append(
                        {
                            "table": file,
                            "id": next((v for k, v in row.items() if k.endswith("_id")), ""),
                            "disease_id": did,
                            "field": field,
                            "text": text,
                        }
                    )
    sentences: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for item in prose_rows:
        sentences[normalized(item["text"])].append(item)
    repeats = [items for items in sentences.values() if len(items) > 1]
    differential_defects = [
        {"id": r["differential_link_id"], "reason": "missing explicit distinction"}
        for r in read(REL / "disease_differentials.csv")
        if r["source_disease_id"] in diseases
        and (
            not r.get("findings_favoring_target")
            or not r.get("findings_favoring_competitor")
            or not r.get("next_test_to_distinguish")
        )
    ]
    steps = read(REL / "algorithm_steps.csv")
    algorithms = [
        r for r in read(SOURCE / "algorithms.csv") if r["algorithm_id"].startswith("ALG-NEUR-")
    ]
    by_algorithm: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for step in steps:
        by_algorithm[step["algorithm_id"]].append(step)
    algorithm_defects = []
    for algorithm in algorithms:
        own = by_algorithm[algorithm["algorithm_id"]]
        for step in own:
            if (
                step["node_type"] == "decision"
                and step.get("next_node_if_true") == step.get("next_node_if_false")
                and step.get("next_node_if_true")
            ):
                algorithm_defects.append(
                    {
                        "algorithm_id": algorithm["algorithm_id"],
                        "node_id": step["node_id"],
                        "reason": "true and false branches converge without documented reason",
                    }
                )
            if (
                "explicit contingency" in step.get("prompt_or_action", "").lower()
                or "unsafe branch—" in step.get("prompt_or_action", "").lower()
            ):
                algorithm_defects.append(
                    {
                        "algorithm_id": algorithm["algorithm_id"],
                        "node_id": step["node_id"],
                        "reason": "manufactured generic algorithm node",
                    }
                )
    generated_source_checked = []
    for filename, idfield in (
        ("findings.csv", "finding_id"),
        ("diagnostics.csv", "diagnostic_id"),
        ("treatments.csv", "treatment_id"),
        ("keywords.csv", "keyword_id"),
        ("complications.csv", "entity_id"),
    ):
        for row in read(SOURCE / filename):
            if "-NEUR-" in row[idfield] and row.get("source_review_status") == "source_checked":
                generated_source_checked.append({"table": filename, "id": row[idfield]})
    result = {
        "invalid_yaml": invalid_yaml,
        "empty_manifests": empty,
        "manifest_entries_missing_required_content": missing,
        "priority_1_profile_inheritance": [
            did
            for did, d in diseases.items()
            if d["board_exam_priority"] == "1" and did in non_explicit
        ],
        "priority_2_profile_inheritance": [
            did
            for did, d in diseases.items()
            if d["board_exam_priority"] == "2" and did in non_explicit
        ],
        "generic_relationship_explanations": prose_rows,
        "phase4a_generic_relationship_explanations": [
            row for row in prose_rows if row["disease_id"] in phase4a_ids
        ],
        "repeated_text_clusters": repeats,
        "differentials_without_explicit_clues": differential_defects,
        "algorithm_defects": algorithm_defects,
        "automatically_source_checked_entities": generated_source_checked,
        "explicitly_curated_diseases": sorted(manifests),
        "remaining_non_explicit_diseases": non_explicit,
        "computed_summary": {
            "manifest_disease_count": len(manifests),
            "neurology_disease_count": len(diseases),
            "algorithm_count": len(algorithms),
            "relationship_template_hits": len(prose_rows),
            "phase4a_relationship_template_hits": len(
                [row for row in prose_rows if row["disease_id"] in phase4a_ids]
            ),
            "algorithm_defect_count": len(algorithm_defects),
        },
    }
    return result


def main() -> None:
    result = audit()
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "neurology_validation_truth_audit.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (REPORTS / "neurology_validation_truth_audit.md").write_text(
        "# Neurology validation truth audit\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in result["computed_summary"].items())
        + "\n\nSee JSON for offending IDs and text.\n",
        encoding="utf-8",
    )
    if any(
        result[key]
        for key in (
            "invalid_yaml",
            "empty_manifests",
            "manifest_entries_missing_required_content",
            "generic_relationship_explanations",
            "algorithm_defects",
        )
    ):
        raise SystemExit(
            "Truth audit found curation defects; see reports/neurology_validation_truth_audit.json"
        )


if __name__ == "__main__":
    main()
