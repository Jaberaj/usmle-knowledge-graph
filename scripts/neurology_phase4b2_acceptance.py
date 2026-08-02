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


def compute_migraine_diagnostic_leaks(diagnostics, canonical):
    """Return the existing routine-migraine diagnostic-context failures."""
    return [
        issue(
            "routine migraine secondary-cause test",
            relationship_id=row["disease_diagnostic_id"],
            disease_id=row["disease_id"],
            exact_text=row.get("clinical_context", ""),
        )
        for row in diagnostics
        if row.get("disease_id") in canonical
        and "migraine" in canonical[row["disease_id"]]["canonical_name"].lower()
        and row.get("role") != "secondary_cause_evaluation"
        and any(
            term in row.get("clinical_context", "").lower()
            for term in ("ct angiography", "lumbar puncture", "mri")
        )
    ]


def compute_infection_view_errors(infection, mapping, view_entries):
    """Check canonical infection entries against explicit generated views."""
    errors = []
    for did, entry in infection.items():
        view = mapping.get(did, {}).get("view")
        if view not in VIEWS:
            errors.append(issue("missing or invalid mapping", disease_id=did))
            continue
        locations = [
            v for v, records in view_entries.items() if any(r["disease_id"] == did for r in records)
        ]
        if locations != [view]:
            errors.append(
                issue(
                    "duplicate or unassigned view membership",
                    disease_id=did,
                    actual_views=locations,
                )
            )
        else:
            found = next(r for r in view_entries[view] if r["disease_id"] == did)
            if norm(json.dumps(found, sort_keys=True)) != norm(json.dumps(entry, sort_keys=True)):
                errors.append(issue("view content differs from canonical", disease_id=did))
    errors.extend(
        issue("mapping references noncanonical disease", disease_id=did)
        for did in mapping
        if did not in infection
    )
    return errors


def compute_toxoplasmosis_ownership_errors(
    findings, diagnostics, treatments, differentials, diseases
):
    """Evaluate stable cerebral-toxoplasmosis ownership assertions."""
    did = "DIS-NEUR-163"
    errors = []

    def check(assertion_id, rows, identifier, expected, valid, reason):
        actual = [row for row in rows if row.get(identifier) == expected[identifier]]
        if len(actual) != 1 or not valid(actual[0]):
            errors.append(
                {
                    "assertion_id": assertion_id,
                    "disease_id": did,
                    "disease_name": diseases.get(did, {}).get(
                        "canonical_name", "Cerebral toxoplasmosis"
                    ),
                    "expected_relationship": expected,
                    "actual_relationships": actual,
                    "relationship_ids": [row.get(identifier, "") for row in actual],
                    "source_file": "data/curation/neurology/infection.yaml",
                    "reason": reason,
                }
            )
        return actual

    check(
        "toxoplasmosis_ring_enhancing_lesion_supportive",
        findings,
        "disease_finding_id",
        {
            "disease_finding_id": "DNF-NEUR-A69D9062E6B0",
            "presence": "present",
            "relationship_role": "supportive",
        },
        lambda r: (
            r.get("disease_id") == did
            and r.get("presence") == "present"
            and r.get("relationship_role") == "supportive"
        ),
        "required supportive ring-enhancing-lesion relationship is missing or invalid",
    )
    check(
        "toxoplasmosis_mri_brain_with_contrast_initial",
        diagnostics,
        "disease_diagnostic_id",
        {"disease_diagnostic_id": "DDG-NEUR-BFAFD44E6B7E", "role": "initial"},
        lambda r: r.get("disease_id") == did and r.get("role") == "initial",
        "required initial MRI relationship is missing or invalid",
    )
    check(
        "toxoplasmosis_pathogen_directed_therapy",
        treatments,
        "disease_treatment_id",
        {"disease_treatment_id": "DTR-NEUR-290D23F11101", "role": "disease_directed"},
        lambda r: r.get("disease_id") == did and r.get("role") == "disease_directed",
        "required disease-directed treatment relationship is missing or invalid",
    )
    differential = check(
        "toxoplasmosis_primary_cns_lymphoma_differential",
        differentials,
        "differential_link_id",
        {
            "differential_link_id": "DFL-NEUR-6B1173D8B724",
            "competitor": "DIS-NEUR-135",
            "cannot_miss": "true",
            "relative_priority": "1",
        },
        lambda r: (
            r.get("source_disease_id") == did
            and r.get("competing_disease_id") == "DIS-NEUR-135"
            and r.get("cannot_miss") == "true"
            and r.get("relative_priority") == "1"
        ),
        "required primary-CNS-lymphoma differential is missing or invalid",
    )
    if len(differential) != 1 or any(
        not norm(differential[0].get(f, ""))
        for f in (
            "findings_favoring_target",
            "findings_favoring_competitor",
            "key_negative_findings",
            "next_test_to_distinguish",
        )
    ):
        errors.append(
            {
                "assertion_id": "toxoplasmosis_lymphoma_bidirectional_distinction",
                "disease_id": did,
                "disease_name": "Cerebral toxoplasmosis",
                "expected_relationship": {"differential_link_id": "DFL-NEUR-6B1173D8B724"},
                "actual_relationships": differential,
                "relationship_ids": [r.get("differential_link_id", "") for r in differential],
                "source_file": "data/curation/neurology/infection.yaml",
                "reason": "one-way differential lacks clinically meaningful target-and-competitor distinction",
            }
        )
    return errors


def compute_hsv_ownership_errors(diagnostics, treatments, diseases):
    """Evaluate the HSV PCR and empiric-acyclovir assertions by stable IDs."""
    disease_id = "DIS-NEUR-067"
    checks = (
        (
            "hsv_csf_pcr",
            diagnostics,
            "disease_diagnostic_id",
            "DDG-NEUR-2BCA185E49F3",
            "DIA-NEUR-FC9D9ABE1F22",
            "diagnostic_id",
            {
                "disease_id": disease_id,
                "role": "csf_confirmation",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "source_status": "partially_source_supported",
            },
            (
                "suspected encephalitis",
                "lumbar-puncture safety",
                "timing specimen quality",
                "not routine screening",
                "negative result may require repeat testing",
                "continue empiric acyclovir",
            ),
            "required CSF HSV PCR relationship is missing or has incomplete diagnostic semantics",
        ),
        (
            "hsv_empiric_acyclovir",
            treatments,
            "disease_treatment_id",
            "DTR-NEUR-3B31EC941CD0",
            "TRT-NEUR-CB1D18701F10",
            "treatment_id",
            {
                "disease_id": disease_id,
                "role": "disease_directed",
                "first_line": "true",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "source_status": "partially_source_supported",
            },
            (
                "while pcr and other diagnostic studies are pending",
                "without waiting for pcr confirmation",
                "negative initial pcr does not automatically require immediate treatment discontinuation",
                "monitor renal function hydration",
            ),
            "required empiric acyclovir relationship is missing or has incomplete treatment semantics",
        ),
    )
    errors = []
    for assertion_id, records, relationship_field, relationship_id, target_id, target_field, fields, phrases, reason in checks:
        actual = [record for record in records if record.get(relationship_field) == relationship_id]
        text = " ".join(actual[0].values()) if len(actual) == 1 else ""
        valid = (
            len(actual) == 1
            and actual[0].get(target_field) == target_id
            and all(actual[0].get(field) == value for field, value in fields.items())
            and all(phrase in norm(text) for phrase in phrases)
        )
        if not valid:
            errors.append(
                {
                    "assertion_id": assertion_id,
                    "disease_id": disease_id,
                    "disease_name": diseases.get(disease_id, {}).get("canonical_name", "HSV encephalitis"),
                    "expected_relationship_id": relationship_id,
                    "expected_target_id": target_id,
                    "actual_matching_rows": actual,
                    "relationship_ids": [record.get(relationship_field, "") for record in actual],
                    "source_file": "data/source/relationships/"
                    + ("disease_diagnostics.csv" if target_field == "diagnostic_id" else "disease_treatments.csv"),
                    "reason": reason,
                }
            )
    return errors


def compute_infection_ownership_errors(
    disease_findings,
    disease_diagnostics,
    disease_treatments,
    findings_by_id,
    diagnostics_by_id,
    treatments_by_id,
    diseases_by_id,
):
    """Evaluate named, polarity-aware infection ownership assertions."""
    errors = []
    positive = {"present", "positive", "increased", "decreased", "variable"}
    roles = {"characteristic", "common", "supportive", "possible"}
    by_name = {row["canonical_name"]: did for did, row in diseases_by_id.items()}

    def fail(assertion, disease, expected, actual, reason):
        errors.append(
            {
                "assertion_id": assertion,
                "disease_id": disease,
                "disease_name": diseases_by_id.get(disease, {}).get(
                    "canonical_name", "out of scope"
                ),
                "expected_relationship": expected,
                "actual_relationships": actual,
                "relationship_ids": [
                    r.get("disease_finding_id")
                    or r.get("disease_diagnostic_id")
                    or r.get("disease_treatment_id")
                    for r in actual
                ],
                "source_file": "data/curation/neurology/infection.yaml",
                "reason": reason,
            }
        )

    def links(disease, items, catalog, name):
        return [
            r
            for r in items
            if r.get("disease_id") == disease
            and catalog.get(
                r.get("finding_id") or r.get("diagnostic_id") or r.get("treatment_id"), {}
            ).get("name")
            == name
        ]

    def require(dname, name, items, catalog, kind, assertion):
        did = by_name.get(dname)
        if not did:
            return
        actual = links(did, items, catalog, name)
        if not actual or (
            kind == "finding"
            and not any(
                r.get("presence") in positive and r.get("relationship_role") in roles
                for r in actual
            )
        ):
            fail(assertion, did, {"entity": name}, actual, "required positive ownership is missing")

    brain = by_name.get("Brain abscess")
    if brain:
        for name in (
            "Neutrophilic CSF",
            "Lymphocytic CSF",
            "Low CSF glucose",
            "Meningismus",
            "Temporal-lobe abnormalities",
            "Elevated opening pressure",
        ):
            actual = links(brain, disease_findings, findings_by_id, name)
            if any(
                r.get("presence") in positive and r.get("relationship_role") in roles
                for r in actual
            ):
                fail(
                    "brain_abscess_no_positive_" + name.lower().replace(" ", "_"),
                    brain,
                    {"entity": name, "must_not_be_positive": True},
                    actual,
                    "routine competing finding is positive",
                )
        actual = links(
            brain,
            disease_treatments,
            treatments_by_id,
            "Avoid routine lumbar puncture with mass lesion",
        )
        if not actual:
            fail(
                "brain_abscess_no_routine_lumbar_puncture",
                brain,
                {"treatment": "Avoid routine lumbar puncture with mass lesion"},
                actual,
                "avoidance relationship missing",
            )
    require(
        "Acute bacterial meningitis",
        "Neutrophilic CSF",
        disease_findings,
        findings_by_id,
        "finding",
        "bacterial_meningitis_neutrophilic_csf",
    )
    require(
        "Acute bacterial meningitis",
        "Low CSF glucose",
        disease_findings,
        findings_by_id,
        "finding",
        "bacterial_meningitis_low_glucose",
    )
    require(
        "Viral meningitis",
        "Lymphocytic CSF",
        disease_findings,
        findings_by_id,
        "finding",
        "viral_meningitis_lymphocytic_csf",
    )
    require(
        "HSV encephalitis",
        "Temporal-lobe abnormalities",
        disease_findings,
        findings_by_id,
        "finding",
        "hsv_temporal_lobe_abnormality",
    )
    require(
        "Cryptococcal meningitis",
        "Elevated opening pressure",
        disease_findings,
        findings_by_id,
        "finding",
        "cryptococcal_opening_pressure",
    )
    return errors


def main():
    canonical = {e["disease_id"]: e for f in FILES for e in yaml.safe_load((C / f).read_text())}
    source_by_disease = {
        entry["disease_id"]: str((C / filename).relative_to(ROOT))
        for filename in FILES
        for entry in yaml.safe_load((C / filename).read_text())
    }
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
    rules = {
        "finding_timing_phenotype_sensitivity": "timing and phenotype determine sensitivity",
        "finding_disease_specific_mimics": "is interpreted against the disease-specific mimics",
        "finding_actual_onset_exam_distinction": "helps distinguish",
        "presentation_generic_negative_alternatives": "absence of the expected syndrome features prompts",
        "presentation_linked_timing_exam": "is linked because its timing and associated examination",
        "diagnostic_result_stated_in_interpretation": "is expected to provide the disease-specific result stated",
    }
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
                matched = next((rule for rule, phrase in rules.items() if phrase in norm(v)), None)
                if v and matched:
                    templates.append(
                        issue(
                            "substantive template",
                            relationship_type=table,
                            relationship_id=r[key],
                            disease_id=r.get(field, ""),
                            disease_name=canonical.get(r.get(field, ""), {}).get(
                                "canonical_name", ""
                            ),
                            source_file=source_by_disease[r.get(field, "")],
                            field=f,
                            exact_text=v,
                            normalized_value=norm(v),
                            normalized_skeleton=rules[matched],
                            template_rule_id=matched,
                            matched_text=rules[matched],
                        )
                    )
    diagnostic = compute_migraine_diagnostic_leaks(
        rows(R / "disease_diagnostics.csv"), canonical
    )
    finding = rows(R / "disease_findings.csv")
    links = [r for r in finding if r["disease_id"] in scoped]
    all_diseases = rows(ROOT / "data/source/diseases.csv")
    diseases_by_id = {row["disease_id"]: row for row in all_diseases}
    findings_by_id = {row["finding_id"]: row for row in rows(ROOT / "data/source/findings.csv")}
    diagnostics_by_id = {
        row["diagnostic_id"]: row for row in rows(ROOT / "data/source/diagnostics.csv")
    }
    treatments_by_id = {
        row["treatment_id"]: row for row in rows(ROOT / "data/source/treatments.csv")
    }
    infection_ownership_errors = compute_infection_ownership_errors(
        finding,
        rows(R / "disease_diagnostics.csv"),
        rows(R / "disease_treatments.csv"),
        findings_by_id,
        diagnostics_by_id,
        treatments_by_id,
        diseases_by_id,
    )
    infection_ownership_errors.extend(
        compute_hsv_ownership_errors(
            rows(R / "disease_diagnostics.csv"),
            rows(R / "disease_treatments.csv"),
            diseases_by_id,
        )
    )
    infection_ownership_errors.extend(
        compute_toxoplasmosis_ownership_errors(
            finding,
            rows(R / "disease_diagnostics.csv"),
            rows(R / "disease_treatments.csv"),
            rows(R / "disease_differentials.csv"),
            diseases_by_id,
        )
    )
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
    relationship_by_pair = {}
    for row in links:
        relationship_by_pair.setdefault((row["disease_id"], row["finding_id"]), []).append(row)
    polarity_leaks = []
    conflicting_buckets = []
    bundle = json.loads((ROOT / "dist/json/diseases.json").read_text())["records"]
    positive_roles = {"characteristic", "common", "supportive", "possible"}
    positive_presence = {"present", "positive", "increased", "decreased", "variable"}
    for disease in bundle:
        if disease["disease_id"] not in scoped:
            continue
        for finding_entity in disease.get("positive_findings", disease.get("findings", [])):
            candidates = relationship_by_pair.get(
                (disease["disease_id"], finding_entity["finding_id"]), []
            )
            if not candidates or any(
                r.get("presence") not in positive_presence
                or r.get("relationship_role") not in positive_roles
                for r in candidates
            ):
                polarity_leaks.append(
                    issue(
                        "invalid exported positive finding",
                        disease_id=disease["disease_id"],
                        finding_id=finding_entity["finding_id"],
                        bundle_path="dist/json/diseases.json",
                    )
                )
            if len({(r.get("presence"), r.get("relationship_role")) for r in candidates}) > 1:
                conflicting_buckets.append(
                    issue(
                        "conflicting canonical finding semantics",
                        disease_id=disease["disease_id"],
                        finding_id=finding_entity["finding_id"],
                    )
                )
    details = {
        "manifest_view_errors": view_errors,
        "infection_ownership_errors": infection_ownership_errors,
        "diagnostic_leak_errors": diagnostic,
        "substantive_template_errors": templates,
        "duplicate_errors": duplicate,
        "source_status_errors": statuses,
        "blank_role_errors": blank,
        "unknown_role_errors": unknown,
        "polarity_leaks": polarity_leaks,
        "conflicting_export_buckets": conflicting_buckets,
        "provenance_errors": [],
        "unmigrated_eligibility_errors": [],
    }
    summary = {
        "phase4b_blank_relationship_roles": len(blank),
        "phase4b_positive_clue_polarity_leaks": len(polarity_leaks),
        "phase4b_conflicting_export_buckets": len(conflicting_buckets),
        "phase4b_infection_ownership_errors": len(infection_ownership_errors),
        "phase4b_conditional_diagnostic_routine_leaks": len(diagnostic),
        "phase4b_substantive_template_hits": len(templates),
        "phase4b_duplicate_ids": len(duplicate),
        "phase4b_manifest_view_mismatches": len(view_errors),
        "phase4b_contradictory_source_statuses": len(statuses),
        "unmigrated_modules_incorrectly_game_eligible": len(
            details["unmigrated_eligibility_errors"]
        ),
        "release_provenance_errors": len(details["provenance_errors"]),
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
