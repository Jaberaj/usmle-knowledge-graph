"""Group computed Phase 4B template violations into a remediation inventory."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def main():
    audit = json.loads((REPORTS / "neurology_phase4b2_acceptance.json").read_text())
    errors = audit["details"]["substantive_template_errors"]
    groups = defaultdict(list)
    for e in errors:
        groups[
            (e.get("template_rule_id", ""), e.get("relationship_type", ""), e.get("field", ""))
        ].append(e)
    inventory = {
        "total_template_hits": len(errors),
        "unique_template_rule_ids": len({e.get("template_rule_id", "") for e in errors}),
        "unique_template_skeletons": len(groups),
        "hits_by_module": dict(Counter(e.get("source_file", "") for e in errors)),
        "hits_by_relationship_type": dict(Counter(e.get("relationship_type", "") for e in errors)),
        "hits_by_field": dict(Counter(e.get("field", "") for e in errors)),
        "hits_by_disease": dict(Counter(e.get("disease_id", "unknown") for e in errors)),
        "hits_by_template_rule_id": dict(Counter(e.get("template_rule_id", "") for e in errors)),
        "top_template_clusters": [
            {
                "template_rule_id": k[0],
                "normalized_skeleton": v[0].get("normalized_skeleton", ""),
                "count": len(v),
                "relationship_types": [k[1]],
                "fields": [k[2]],
                "source_files": sorted({e.get("source_file", "") for e in v}),
                "affected_disease_ids": sorted({e.get("disease_id", "") for e in v}),
                "affected_disease_names": sorted({e.get("disease_name", "") for e in v}),
                "representative_examples": v[:3],
                "recommended_remediation_strategy": "Replace with relationship-specific clinical meaning, indication, result, limitation, or differential distinction.",
            }
            for k, v in sorted(groups.items(), key=lambda x: -len(x[1]))[:50]
        ],
    }
    REPORTS.joinpath("neurology_phase4b_template_inventory.json").write_text(
        json.dumps(inventory, indent=2) + "\n"
    )
    REPORTS.joinpath("neurology_phase4b_template_inventory.md").write_text(
        "# Neurology Phase 4B template remediation inventory\n\n"
        + f"- total_template_hits: {inventory['total_template_hits']}\n- unique_template_skeletons: {inventory['unique_template_skeletons']}\n\n"
        + "\n".join(
            f"- {key}: {value}" for key, value in inventory["hits_by_relationship_type"].items()
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
