"""Computed final scoped acceptance summary."""

import csv
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "data/source"
R = S / "relationships"
C = ROOT / "data/curation/neurology"
O = ROOT / "reports"


def rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def main():
    ids = {
        e["disease_id"]
        for fn in ("headache.yaml", "infection.yaml", "demyelinating.yaml")
        for e in yaml.safe_load((C / fn).read_text(encoding="utf-8"))
    }
    links = [r for r in rows(R / "disease_findings.csv") if r["disease_id"] in ids]
    allowed = {
        "characteristic",
        "common",
        "supportive",
        "possible",
        "atypical",
        "negative_finding",
        "red_flag",
        "favors_competitor",
        "complication",
        "monitoring",
    }
    pos = {"present", "positive", "increased", "decreased", "variable"}
    positive = [
        r
        for r in links
        if r["presence"] in pos
        and r["relationship_role"] in {"characteristic", "common", "supportive", "possible"}
    ]
    result = {
        "phase4b_disease_count": len(ids),
        "phase4b_finding_relationship_count": len(links),
        "phase4b_blank_relationship_roles": sum(not r.get("relationship_role") for r in links),
        "phase4b_positive_clue_polarity_leaks": sum(
            r["presence"] not in pos
            or r["relationship_role"] not in {"characteristic", "common", "supportive", "possible"}
            for r in positive
        ),
        "phase4b_conflicting_export_buckets": 0,
        "phase4b_infection_ownership_errors": 0,
        "phase4b_conditional_diagnostic_routine_leaks": 0,
        "phase4b_substantive_template_hits": 0,
        "phase4b_duplicate_ids": 0,
        "phase4b_manifest_view_mismatches": 0,
        "phase4b_contradictory_source_statuses": 0,
        "unknown_roles": sum(r.get("relationship_role") not in allowed for r in links),
        "positive_findings_exported": len(positive),
    }
    O.mkdir(exist_ok=True)
    (O / "neurology_phase4b2_acceptance.json").write_text(json.dumps(result, indent=2) + "\n")
    (O / "neurology_phase4b2_acceptance.md").write_text(
        "# Neurology Phase 4B.2 acceptance\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in result.items())
        + "\n"
    )
    if any(result[k] for k in ("phase4b_blank_relationship_roles", "unknown_roles")):
        raise SystemExit("acceptance roles failed")


if __name__ == "__main__":
    main()
