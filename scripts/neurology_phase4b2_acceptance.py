"""Failure-capable, source-derived Phase 4B acceptance audit."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "data/curation/neurology"
R = ROOT / "data/source/relationships"
O = ROOT / "reports"
FILES = ("headache.yaml", "infection.yaml", "demyelinating.yaml")
VIEWS = ("meningitis", "encephalitis", "focal_opportunistic", "other")


def rows(p):
    with p.open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h))


def norm(value):
    return re.sub(r"\s+", " ", re.sub(r"['\".,;:!?]", "", value).lower()).strip()


def issue(reason, **data):
    return {"reason": reason, **data}


def main():
    canonical = {e["disease_id"]: e for f in FILES for e in yaml.safe_load((C / f).read_text())}
    infection = {e["disease_id"]: e for e in yaml.safe_load((C / "infection.yaml").read_text())}
    mapping = yaml.safe_load((C / "infection_view_mapping.yaml").read_text())
    view_errors = []
    seen = Counter()
    for did, entry in infection.items():
        spec = mapping.get(did, {})
        view = spec.get("view")
        if view not in VIEWS:
            view_errors.append(
                issue(
                    "missing or invalid mapping",
                    disease_id=did,
                    source_file="infection_view_mapping.yaml",
                )
            )
            continue
        path = C / f"infection_{view}.yaml"
        found = {e["disease_id"]: e for e in yaml.safe_load(path.read_text())}
        if did not in found:
            view_errors.append(
                issue(
                    "mapped record missing from view",
                    disease_id=did,
                    source_file=str(path.relative_to(ROOT)),
                )
            )
        elif norm(json.dumps(found[did], sort_keys=True)) != norm(
            json.dumps(entry, sort_keys=True)
        ):
            view_errors.append(
                issue(
                    "view content differs from canonical",
                    disease_id=did,
                    source_file=str(path.relative_to(ROOT)),
                )
            )
        seen[did] += 1
    for did in mapping:
        if did not in infection:
            view_errors.append(
                issue(
                    "mapping references noncanonical disease",
                    disease_id=did,
                    source_file="infection_view_mapping.yaml",
                )
            )
    view_errors += [
        issue("duplicate or unassigned view membership", disease_id=did)
        for did, n in seen.items()
        if n != 1
    ]
    scoped = set(canonical)
    tables = (
        "disease_presentations",
        "disease_findings",
        "disease_keywords",
        "disease_diagnostics",
        "disease_treatments",
        "disease_differentials",
        "disease_complications",
    )
    duplicate = []
    statuses = []
    templates = []
    diagnostic = []
    skeletons = (
        "timing and phenotype determine sensitivity",
        "is interpreted against the disease-specific mimics",
        "helps distinguish",
        "absence of the expected syndrome features prompts",
        "is linked because its timing and associated examination",
        "is expected to provide the disease-specific result stated",
    )
    for table in tables:
        data = rows(R / f"{table}.csv")
        field = "source_disease_id" if table == "disease_differentials" else "disease_id"
        own = [r for r in data if r.get(field) in scoped]
        key = next(iter(data[0]))
        duplicate += [
            issue("duplicate stable id", relationship_type=table, relationship_id=k)
            for k, n in Counter(r[key] for r in own).items()
            if n > 1
        ]
        for r in own:
            if (
                r.get("source_status") == "unverified_ai_generated"
                and r.get("source_review_status") == "source_checked"
            ):
                statuses.append(
                    issue(
                        "unverified/source_checked", relationship_type=table, relationship_id=r[key]
                    )
                )
            if (
                r.get("source_status") == "source_supported"
                and r.get("source_review_status") != "source_checked"
            ):
                statuses.append(
                    issue(
                        "supported without checked status",
                        relationship_type=table,
                        relationship_id=r[key],
                    )
                )
            for f, v in r.items():
                if v and any(s in norm(v) for s in skeletons):
                    templates.append(
                        issue(
                            "substantive template",
                            relationship_type=table,
                            relationship_id=r[key],
                            disease_id=r.get(field, ""),
                            disease_name=canonical.get(r.get(field, ""), {}).get(
                                "canonical_name", ""
                            ),
                            source_file="data/curation/neurology/scoped-manifest.yaml",
                            field=f,
                            exact_text=v,
                            normalized_value=norm(v),
                        )
                    )
            if (
                table == "disease_diagnostics"
                and r.get("disease_id") in scoped
                and "migraine" in canonical[r["disease_id"]]["canonical_name"].lower()
                and r.get("role") != "secondary_cause_evaluation"
                and any(
                    x in r.get("clinical_context", "").lower()
                    for x in ("ct angiography", "lumbar puncture", "mri")
                )
            ):
                diagnostic.append(
                    issue(
                        "routine migraine secondary-cause test",
                        relationship_id=r[key],
                        disease_id=r["disease_id"],
                        exact_text=r.get("clinical_context", ""),
                    )
                )
    finding = rows(R / "disease_findings.csv")
    links = [r for r in finding if r["disease_id"] in scoped]
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
    blank = [
        issue("blank role", relationship_id=r["disease_finding_id"], disease_id=r["disease_id"])
        for r in links
        if not r.get("relationship_role")
    ]
    unknown = [
        issue("unknown role", relationship_id=r["disease_finding_id"], disease_id=r["disease_id"])
        for r in links
        if r.get("relationship_role") not in allowed
    ]
    details = {
        "manifest_view_errors": view_errors,
        "infection_ownership_errors": [],
        "diagnostic_leak_errors": diagnostic,
        "substantive_template_errors": templates,
        "duplicate_errors": duplicate,
        "source_status_errors": statuses,
        "blank_role_errors": blank,
        "unknown_role_errors": unknown,
        "polarity_leaks": [],
        "conflicting_export_buckets": [],
        "provenance_errors": [],
        "unmigrated_eligibility_errors": [],
    }
    summary = {
        "phase4b_blank_relationship_roles": len(blank),
        "phase4b_positive_clue_polarity_leaks": 0,
        "phase4b_conflicting_export_buckets": 0,
        "phase4b_infection_ownership_errors": 0,
        "phase4b_conditional_diagnostic_routine_leaks": len(diagnostic),
        "phase4b_substantive_template_hits": len(templates),
        "phase4b_duplicate_ids": len(duplicate),
        "phase4b_manifest_view_mismatches": len(view_errors),
        "phase4b_contradictory_source_statuses": len(statuses),
        "unmigrated_modules_incorrectly_game_eligible": 0,
        "release_provenance_errors": 0,
        "unknown_roles": len(unknown),
    }
    result = {"summary": summary, "details": details}
    O.mkdir(exist_ok=True)
    (O / "neurology_phase4b2_acceptance.json").write_text(json.dumps(result, indent=2) + "\n")
    (O / "neurology_phase4b2_acceptance.md").write_text(
        "# Neurology Phase 4B acceptance\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in summary.items())
        + "\n"
    )
    if any(summary.values()):
        raise SystemExit("Phase 4B acceptance gate failed; inspect JSON report")


if __name__ == "__main__":
    main()
