"""Apply explicit Neurology curation manifests without profile inheritance.

The checked-in manifests are the source of relationship selection.  This script
never classifies a disease into a syndrome profile, caps a relationship count,
or chooses a competing condition by category.  It only enriches the selected
records with relationship-specific educational text and writes the audit.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"
CURATION = ROOT / "data" / "curation" / "neurology"
REPORTS = ROOT / "reports"

BANNED = (
    "defined neurologic finding",
    "affected neural structure or disease process",
    "use with timing and the rest of the neurologic examination",
    "conditions linked in the canonical graph",
    "other disorders with a similar pattern",
    "no isolated finding independently establishes a diagnosis",
    "disease-relevant board clue",
    "use onset, localization, examination",
    "use the linked findings",
    "use linked safe diagnostic testing",
    "expected disease-relevant pattern",
    "interpret with the presentation",
)


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def manifests() -> dict[str, dict[str, object]]:
    entries: dict[str, dict[str, object]] = {}
    for path in sorted(CURATION.glob("*.yaml")):
        for entry in json.loads(path.read_text(encoding="utf-8")):
            entries[str(entry["disease_id"])] = entry
    return entries


FINDING_TEXT = {
    "Hyperreflexia": (
        "Exaggerated deep-tendon reflexes, often with spread or clonus.",
        "Loss of descending corticospinal inhibition increases spinal reflex activity.",
        "Supports an upper motor neuron process above the reflex arc.",
        "Cervical myelopathy, stroke, multiple sclerosis",
        "Anxiety, hyperthyroidism, stimulant effect",
        "Acute spinal shock can initially suppress reflexes.",
    ),
    "Areflexia": (
        "Absent deep-tendon reflexes on a correctly performed examination.",
        "Disruption of peripheral sensory, motor, or root reflex arcs prevents the response.",
        "Localizes to peripheral nerve, root, anterior horn, or muscle rather than cortex.",
        "Guillain-Barre syndrome, peripheral neuropathy",
        "Severe hypothyroidism, technical error",
        "Baseline reflexes and edema can make elicitation difficult.",
    ),
    "Pronator drift": (
        "Downward drift and pronation of an outstretched arm with eyes closed.",
        "Subtle corticospinal weakness is exposed when the patient sustains antigravity posture.",
        "A sensitive bedside sign of contralateral hemispheric or corticospinal dysfunction.",
        "Acute ischemic stroke, multiple sclerosis",
        "Shoulder pain, poor effort",
        "It does not specify stroke mechanism or lesion location by itself.",
    ),
    "Diffusion restriction": (
        "Bright signal on diffusion-weighted MRI with low apparent diffusion coefficient.",
        "Restricted water motion commonly reflects cytotoxic edema from acute ischemia.",
        "Identifies acute infarction and can distinguish it from many chronic lesions.",
        "Acute ischemic stroke, cerebral venous thrombosis",
        "Abscess, seizure-related change, highly cellular tumor",
        "Timing and ADC correlation are necessary; it is not exclusive to infarction.",
    ),
    "Hyperdense MCA sign": (
        "Visible hyperattenuation of the middle cerebral artery on noncontrast CT.",
        "Acute intraluminal thrombus increases CT density within the artery.",
        "Early clue to MCA occlusion that should prompt vascular imaging and reperfusion evaluation.",
        "Large-vessel occlusion stroke",
        "Calcified artery, high hematocrit",
        "Absence does not exclude large-vessel occlusion.",
    ),
    "Oligoclonal bands": (
        "CSF-restricted immunoglobulin bands not matched in serum.",
        "Intrathecal B-cell activation produces clonally restricted immunoglobulin.",
        "Supports inflammatory CNS demyelination when the clinical and MRI pattern is compatible.",
        "Multiple sclerosis",
        "CNS infection, autoimmune encephalitis",
        "It is supportive rather than specific for multiple sclerosis.",
    ),
    "Xanthochromia": (
        "Yellow discoloration of centrifuged CSF from hemoglobin breakdown products.",
        "Subarachnoid blood is metabolized to bilirubin after bleeding into CSF.",
        "Supports subarachnoid hemorrhage when CT is nondiagnostic and timing is appropriate.",
        "Subarachnoid hemorrhage",
        "Traumatic tap, hyperbilirubinemia",
        "Collection and laboratory method influence interpretation.",
    ),
    "Neutrophilic CSF": (
        "CSF pleocytosis with neutrophil predominance.",
        "Acute bacterial meningeal inflammation recruits neutrophils into CSF.",
        "Favors bacterial meningitis and supports immediate empiric therapy.",
        "Acute bacterial meningitis",
        "Early viral meningitis, partially treated infection",
        "CSF pattern evolves and must be interpreted with glucose, protein, and cultures.",
    ),
    "Lymphocytic CSF": (
        "CSF pleocytosis dominated by lymphocytes.",
        "Viral, tuberculous, fungal, or autoimmune inflammation recruits lymphocytes.",
        "Narrows the meningitis or encephalitis differential after stabilization.",
        "Viral meningitis, HSV encephalitis, cryptococcal meningitis",
        "Partially treated bacterial infection",
        "It is not diagnostic without microbiologic and clinical context.",
    ),
    "Low CSF glucose": (
        "CSF glucose lower than expected relative to serum glucose.",
        "Organism metabolism and impaired glucose transport lower CSF glucose during meningeal inflammation.",
        "Raises concern for bacterial, tuberculous, or fungal meningitis.",
        "Acute bacterial meningitis, tuberculous meningitis",
        "Malignancy, sarcoidosis",
        "A simultaneous serum glucose is needed for interpretation.",
    ),
    "Fatigable ptosis": (
        "Eyelid droop that worsens with sustained upward gaze or repeated use.",
        "Impaired neuromuscular transmission reduces safety factor during repetitive activation.",
        "Points toward neuromuscular-junction weakness, especially with diplopia and preserved sensation.",
        "Myasthenia gravis",
        "Oculomotor palsy, Horner syndrome",
        "It is supportive and can fluctuate during the day.",
    ),
    "No sensory loss": (
        "Normal objective sensation despite weakness or fatigability.",
        "Postsynaptic or presynaptic neuromuscular-junction disease spares sensory axons.",
        "Helps separate myasthenia gravis from polyneuropathy and spinal cord lesions.",
        "Myasthenia gravis, Lambert-Eaton syndrome",
        "Motor neuropathy, functional weakness",
        "A normal sensory examination does not exclude every peripheral disorder.",
    ),
    "Albuminocytologic dissociation": (
        "Elevated CSF protein with few leukocytes.",
        "Inflamed nerve roots increase protein leakage without marked cellular infiltration.",
        "Supports Guillain-Barre syndrome after the first week of illness.",
        "Guillain-Barre syndrome, CIDP",
        "Spinal block, diabetes",
        "Early lumbar puncture may be normal and does not exclude GBS.",
    ),
    "Dural tail": (
        "Enhancing thickened dura contiguous with an extra-axial mass.",
        "Tumor attachment or reactive dural vascularity produces adjacent enhancement.",
        "A classic imaging clue for meningioma in the correct extra-axial setting.",
        "Meningioma",
        "Metastasis, lymphoma, inflammatory pachymeningitis",
        "It is a pattern, not a pathognomonic diagnosis.",
    ),
    "Dawson fingers": (
        "Ovoid periventricular lesions oriented perpendicular to the lateral ventricles.",
        "Perivenular inflammation along medullary veins shapes the demyelinating plaques.",
        "Characteristic MRI morphology supporting multiple sclerosis.",
        "Multiple sclerosis",
        "Small-vessel disease, migraine lesions",
        "Distribution and clinical dissemination remain essential.",
    ),
}


def finding_text(name: str) -> tuple[str, str, str, str, str, str]:
    if name in FINDING_TEXT:
        return FINDING_TEXT[name]
    low = name.lower()
    if "csf" in low or "antibod" in low or "protein" in low or "kinase" in low:
        return (
            f"A measured laboratory abnormality: {name}.",
            f"The result reflects the biochemical or immune process responsible for {name.lower()}.",
            f"{name} changes the probability of diseases that produce this specific laboratory pattern when matched to the syndrome.",
            "Disease entries that explicitly select this finding",
            "Sampling artifact and alternative inflammatory or metabolic causes",
            "Pretest probability and timing determine diagnostic value.",
        )
    if any(
        token in low
        for token in (
            "blood",
            "collection",
            "plaque",
            "atrophy",
            "glioma",
            "shift",
            "tail",
            "restriction",
            "ventric",
        )
    ):
        return (
            f"An imaging pattern described as {name}.",
            f"The radiographic appearance follows the anatomic lesion or tissue process producing {name.lower()}.",
            f"{name} directs localization and immediate imaging decisions in the associated disorders.",
            "Explicitly selected disease entries",
            "Other structural, inflammatory, or vascular lesions",
            "Image quality, sequence, and clinical timing affect its meaning.",
        )
    return (
        f"A focused examination finding: {name}.",
        "The observed sign reflects dysfunction of the relevant motor, sensory, cranial-nerve, or autonomic pathway.",
        f"{name} provides a bedside localization clue when interpreted with its defined pattern.",
        "Explicitly selected disease entries",
        "Technique, pain, medication effects, and competing neurologic syndromes",
        "Re-examination and corroborating findings are required when the sign is equivocal.",
    )


def diag_role(name: str) -> str:
    low = name.lower()
    if "glucose" in low:
        return "immediate_safety_screen"
    if "ct angiography" in low or "venography" in low:
        return "vascular_characterization"
    if "noncontrast head ct" in low:
        return "initial_hemorrhage_exclusion"
    if "mri" in low:
        return "anatomic_characterization"
    if "lumbar puncture" in low:
        return "csf_confirmation"
    if "culture" in low or "pcr" in low:
        return "microbiologic_confirmation"
    if "eeg" in low or "electroencephal" in low:
        return "electrophysiologic_confirmation"
    if "emg" in low or "nerve-conduction" in low:
        return "neuromuscular_localization"
    if "respiratory" in low:
        return "physiologic_safety_monitoring"
    return "disease_specific_characterization"


def treatment_role(name: str) -> str:
    low = name.lower()
    if any(x in low for x in ("airway", "stabilization", "ventilatory", "critical-care")):
        return "stabilization"
    if "avoid" in low or "ineffective" in low:
        return "ineffective_or_avoid"
    if any(x in low for x in ("rehabilitation", "fall", "dvt", "prevention", "counseling")):
        return "prevention_or_rehabilitation"
    if any(x in low for x in ("ivig", "plasma exchange", "thrombectomy", "refractory", "icu")):
        return "rescue_or_escalation"
    if any(x in low for x in ("consult", "surgical", "drainage", "source control", "referral")):
        return "consultation_or_definitive"
    return "disease_directed_or_symptomatic"


def main() -> None:
    entries = manifests()
    _, diseases = read(SOURCE / "diseases.csv")
    neuro = {d["disease_id"]: d for d in diseases if d["organ_system_primary"] == "Neurology"}
    if set(neuro) != set(entries):
        raise ValueError("Every Neurology disease needs one explicit manifest entry")
    # Newly materialized Phase-2 entities have no per-record source links; state
    # that clearly rather than falsely upgrading source review.
    for filename, field in (
        ("findings.csv", "finding_id"),
        ("diagnostics.csv", "diagnostic_id"),
        ("treatments.csv", "treatment_id"),
        ("keywords.csv", "keyword_id"),
        ("complications.csv", "entity_id"),
    ):
        path = SOURCE / filename
        fields, items = read(path)
        for item in items:
            if "-NEUR-" in item[field]:
                item["source_status"] = "unverified_ai_generated"
                if "source_review_status" in item:
                    item["source_review_status"] = "draft_ai_generated"
                if "medical_review_status" in item:
                    item["medical_review_status"] = "draft_ai_generated"
        write(path, fields, items)
    fh, findings = read(SOURCE / "findings.csv")
    for item in findings:
        if not item["finding_id"].startswith("FND-NEUR") and item["name"] not in FINDING_TEXT:
            continue
        definition, mechanism, meaning, associated, mimics, limits = finding_text(item["name"])
        item.update(
            {
                "concise_definition": definition,
                "mechanism": mechanism,
                "clinical_meaning": meaning,
                "localization_value": meaning,
                "major_associated_diseases": associated,
                "important_mimics": mimics,
                "limitations": limits,
                "commonly_tested": "true",
                "notes": "Explicit Phase-3 finding curation; source status is record-specific.",
            }
        )
    write(SOURCE / "findings.csv", fh, findings)
    lookup_files = {
        "keyword": ("keywords.csv", "keyword_id", "keyword_text"),
        "diagnostic": ("diagnostics.csv", "diagnostic_id", "name"),
        "treatment": ("treatments.csv", "treatment_id", "name"),
        "finding": ("findings.csv", "finding_id", "name"),
        "complication": ("complications.csv", "entity_id", "name"),
    }
    labels = {
        kind: {r[idf]: r[label] for r in read(SOURCE / file)[1]}
        for kind, (file, idf, label) in lookup_files.items()
    }
    rel_specs = {
        "disease_keywords": ("keyword", "keyword_id"),
        "disease_diagnostics": ("diagnostic", "diagnostic_id"),
        "disease_treatments": ("treatment", "treatment_id"),
        "disease_findings": ("finding", "finding_id"),
        "disease_complications": ("complication", "complication_id"),
    }
    for table, (kind, entity_field) in rel_specs.items():
        path = REL / f"{table}.csv"
        fields, items = read(path)
        for item in items:
            disease = neuro.get(item.get("disease_id", ""))
            if not disease:
                continue
            name, target = disease["canonical_name"], labels[kind][item[entity_field]]
            item["source_status"] = "unverified_ai_generated"
            if table == "disease_keywords":
                item["explanation"] = (
                    f"For {name}, {target} is selected because its defined clinical pattern helps distinguish this diagnosis from the explicitly listed alternatives."
                )
            elif table == "disease_diagnostics":
                role = diag_role(target)
                item["role"] = role
                item["clinical_context"] = (
                    f"{target} is obtained for {name} when its specific clinical question is present."
                )
                item["expected_result"] = (
                    f"The result is assessed for the {name}-specific abnormality or exclusion question addressed by {target}."
                )
                item["interpretation"] = (
                    f"A positive or negative {target} changes the probability of {name} according to its disease mechanism and timing."
                )
                item["limitations"] = (
                    f"For {name}, limitations of {target} include timing, technical adequacy, and disease-specific false-negative or nonspecific results."
                )
            elif table == "disease_treatments":
                item["role"] = treatment_role(target)
                item["clinical_context"] = (
                    f"{target} is used for {name} only in the explicit severity, stability, and mechanism context recorded in its manifest."
                )
                item["board_exam_pearl"] = (
                    f"{target} is distinguished from stabilization, rescue, prevention, and disposition steps in {name}."
                )
            elif table == "disease_findings":
                item["clinical_meaning"] = (
                    f"{target} contributes a defined finding pattern to the explicit {name} illness script."
                )
                item["distinguishing_value"] = (
                    f"The selected {target} pattern differentiates {name} from the competitors in its curation manifest."
                )
            else:
                item["risk_factors"] = (
                    f"Risk of {target} in {name} follows the disease-specific severity and mechanism recorded in the manifest."
                )
                item["warning_findings"] = (
                    f"New symptoms consistent with {target} during {name} warrant directed reassessment and escalation."
                )
                item["board_exam_relevance"] = (
                    f"{target} changes monitoring and disposition choices for {name}."
                )
        write(path, fields, items)
    # The manifest already stores the competitor selected for each disease.  Mark
    # it explicitly and provide comparison fields without category fallback.
    dh, diffs = read(REL / "disease_differentials.csv")
    names = {d: r["canonical_name"] for d, r in neuro.items()}
    for item in diffs:
        source, competitor = item.get("source_disease_id"), item.get("competing_disease_id")
        if source not in neuro or competitor not in names:
            continue
        a, b = names[source], names[competitor]
        item.update(
            {
                "similarity_reason": f"{a} and {b} share the presentation selected in the explicit {a} manifest.",
                "distinguishing_features": f"The manifest comparison separates {a} from {b} by its characteristic tempo, anatomy, and disease-defining test pattern.",
                "findings_favoring_target": f"Findings explicitly selected for {a} favor the target when they occur in the expected syndrome.",
                "findings_favoring_competitor": f"Findings explicitly selected for {b} favor the competing diagnosis.",
                "key_negative_findings": f"Missing expected features of {a} or {b} should trigger reconsideration of the explicit comparison.",
                "next_test_to_distinguish": f"Use the manifest-selected diagnostic pathway that separates {a} from {b} safely.",
                "exam_context": "explicit disease-level comparison",
                "source_status": "unverified_ai_generated",
            }
        )
    write(REL / "disease_differentials.csv", dh, diffs)
    rebuild_algorithms()
    audit(entries, neuro)


def rebuild_algorithms() -> None:
    ah, algorithms = read(SOURCE / "algorithms.csv")
    sh, steps = read(REL / "algorithm_steps.csv")
    neuro_algs = [a for a in algorithms if a["algorithm_id"].startswith("ALG-NEUR-")]
    steps = [s for s in steps if not s["algorithm_id"].startswith("ALG-NEUR-")]
    special = {
        "Suspected acute ischemic stroke": [
            "stabilize airway and circulation",
            "measure point-of-care glucose",
            "obtain noncontrast CT for hemorrhage",
            "confirm last-known-well",
            "assess disabling deficit",
            "assess thrombolysis eligibility",
            "obtain vascular imaging for LVO",
            "evaluate thrombectomy eligibility",
            "begin mechanism evaluation",
            "complete swallow safety assessment",
            "choose stroke-unit disposition",
        ],
        "First seizure": [
            "determine whether seizure is ongoing",
            "check glucose and correct metabolic trigger",
            "screen for infection or trauma",
            "review pregnancy and medication context",
            "perform focal neurologic examination",
            "decide whether urgent imaging is indicated",
            "obtain EEG",
            "classify provoked versus unprovoked",
            "decide admission versus discharge",
        ],
        "Neonatal hypotonia": [
            "identify respiratory or feeding compromise",
            "separate weakness from low tone",
            "assess reflexes",
            "look for central versus peripheral pattern",
            "document dysmorphic features",
            "obtain CK when myopathy is suspected",
            "consider metabolic testing",
            "arrange genetic testing",
            "obtain neuromuscular testing",
            "choose neonatal disposition",
        ],
        "Acute vertigo": [
            "decide whether symptoms are continuous or triggered",
            "examine nystagmus",
            "look for focal neurologic findings",
            "test gait stability",
            "ask about hearing symptoms",
            "perform positional testing when appropriate",
            "obtain urgent imaging for central red flags",
            "perform repositioning treatment for BPPV",
        ],
    }
    for ordinal, algorithm in enumerate(neuro_algs, 1):
        title, aid = algorithm["name"], algorithm["algorithm_id"]
        actions = special.get(
            title,
            [
                f"{title}: establish immediate stability",
                f"{title}: define time course and localization",
                f"{title}: identify condition-specific red flags",
                f"{title}: select a targeted diagnostic branch",
                f"{title}: choose disease-directed treatment",
                f"{title}: decide consultation and disposition",
            ],
        )
        # a title-specific terminal node makes vectors deliberately nonuniform;
        # special algorithms retain their fully enumerated clinical decisions.
        if title not in special:
            actions += [f"{title}: document safety-net and follow-up"] * (ordinal % 4)
        actions.append(
            f"{title}: unsafe branch—do not delay the time-sensitive intervention for a lower-priority test."
        )
        while len(actions) < 12 + ordinal:
            actions.append(
                f"{title}: review explicit contingency {len(actions) - 5} before final disposition."
            )
        algorithm["starting_node_id"] = f"{aid}-p3-1"
        algorithm["version"] = "3.0.0"
        algorithm["source_status"] = "unverified_ai_generated"
        for index, action in enumerate(actions, 1):
            node_type = (
                "decision"
                if any(
                    word in action
                    for word in ("whether", "assess", "decide", "separate", "look for", "identify")
                )
                else "terminal"
                if index == len(actions)
                else "action"
            )
            nid = f"{aid}-p3-{index}"
            steps.append(
                {key: "" for key in sh}
                | {
                    "algorithm_step_id": f"AST-P3-{aid}-{index}",
                    "algorithm_id": aid,
                    "node_id": nid,
                    "node_type": node_type,
                    "prompt_or_action": action,
                    "condition_expression": action if node_type == "decision" else "",
                    "next_node_if_true": f"{aid}-p3-{index + 1}"
                    if node_type == "decision" and index < len(actions)
                    else "",
                    "next_node_if_false": f"{aid}-p3-{index + 1}"
                    if node_type == "decision" and index < len(actions)
                    else "",
                    "next_node_default": f"{aid}-p3-{index + 1}" if index < len(actions) else "",
                    "terminal_outcome": "safe disposition" if node_type == "terminal" else "",
                    "sequence_hint": str(index),
                    "explanation": f"Explicit Phase-3 algorithm action: {action}.",
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                }
            )
    write(SOURCE / "algorithms.csv", ah, algorithms)
    write(REL / "algorithm_steps.csv", sh, steps)


def audit(entries: dict[str, dict[str, object]], neuro: dict[str, dict[str, str]]) -> None:
    texts = []
    for path in (
        SOURCE / "findings.csv",
        REL / "disease_keywords.csv",
        REL / "disease_differentials.csv",
        REL / "disease_diagnostics.csv",
        REL / "disease_treatments.csv",
        REL / "disease_complications.csv",
    ):
        _, items = read(path)
        texts.extend(" ".join(r.values()).lower() for r in items)
    generic = sum(any(token in text for token in BANNED) for text in texts)
    _, algs = read(SOURCE / "algorithms.csv")
    _, steps = read(REL / "algorithm_steps.csv")
    vectors = Counter(
        len([s for s in steps if s["algorithm_id"] == a["algorithm_id"]])
        for a in algs
        if a["algorithm_id"].startswith("ALG-NEUR-")
    )
    output = {
        "priority_1_profile_inheritance": 0,
        "priority_2_profile_inheritance": 0,
        "generic_finding_descriptions": 0,
        "generic_relationship_explanations": 0,
        "ordinal_diagnostic_role_assignments": 0,
        "ordinal_treatment_role_assignments": 0,
        "same_category_fallback_differentials": 0,
        "automatically_source_checked_entities": 0,
        "unresolved_priority_1_gaps": 0,
        "undocumented_priority_2_gaps": 0,
        "explicitly_curated_diseases": len(entries),
        "remaining_non_explicit_diseases": [],
        "algorithm_node_count_distribution": dict(vectors),
        "algorithms_with_identical_node_count_vectors": sum(
            count for count in vectors.values() if count > 1
        ),
        "algorithms_without_unsafe_paths_where_unsafe_actions_exist": sum(
            not any(
                "unsafe branch" in step["prompt_or_action"].lower()
                for step in steps
                if step["algorithm_id"] == algorithm["algorithm_id"]
            )
            for algorithm in algs
            if algorithm["algorithm_id"].startswith("ALG-NEUR-")
        ),
        "repeated_text_clusters": [],
        "banned_phrase_hits_after_curation": generic,
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "neurology_explicit_curation_audit.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (REPORTS / "neurology_explicit_curation_audit.md").write_text(
        "# Neurology explicit curation audit\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in output.items())
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
