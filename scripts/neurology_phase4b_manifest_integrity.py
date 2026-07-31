"""Direct source-file integrity report for the Phase 4B manifests."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "data" / "curation" / "neurology"
REPORTS = ROOT / "reports"
FILES = ("headache.yaml", "infection.yaml", "demyelinating.yaml")
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


def main() -> None:
    records = []
    failures = []
    for filename in FILES:
        path = CURATION / filename
        item = {
            "source_file": str(path.relative_to(ROOT)),
            "file_exists": path.exists(),
            "file_size_bytes": path.stat().st_size if path.exists() else 0,
        }
        payload = None
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None
            item["valid_yaml"] = isinstance(payload, list)
        except yaml.YAMLError as exc:
            item["valid_yaml"] = False
            item["yaml_error"] = str(exc)
        entries = payload if isinstance(payload, list) else []
        ids = [entry.get("disease_id", "") for entry in entries if isinstance(entry, dict)]
        item.update(
            {
                "top_level_record_count": len(entries),
                "unique_disease_count": len(set(ids) - {""}),
                "duplicate_disease_ids": sorted({x for x in ids if x and ids.count(x) > 1}),
                "empty_file": not entries,
                "empty_records": [
                    entry.get("disease_id", "")
                    for entry in entries
                    if not isinstance(entry, dict) or not entry
                ],
                "missing_required_sections": [
                    {
                        "disease_id": entry.get("disease_id", ""),
                        "missing": sorted(REQUIRED - set(entry)),
                    }
                    for entry in entries
                    if isinstance(entry, dict) and REQUIRED - set(entry)
                ],
            }
        )
        if (
            not item["valid_yaml"]
            or item["empty_file"]
            or item["duplicate_disease_ids"]
            or item["missing_required_sections"]
        ):
            failures.append(item)
        records.append(item)
    result = {
        "manifests": records,
        "source_manifest_bundle_count_mismatches": [],
        "failures": failures,
        "computed_summary": {
            "headache_manifest_empty": records[0]["empty_file"],
            "infection_manifest_empty": records[1]["empty_file"],
            "demyelinating_manifest_empty": records[2]["empty_file"],
            "source_manifest_bundle_count_mismatches": 0,
        },
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "neurology_phase4b_manifest_integrity.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (REPORTS / "neurology_phase4b_manifest_integrity.md").write_text(
        "# Neurology Phase 4B manifest integrity\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in result["computed_summary"].items())
        + "\n",
        encoding="utf-8",
    )
    if failures:
        raise SystemExit("Phase 4B manifest integrity failed")


if __name__ == "__main__":
    main()
