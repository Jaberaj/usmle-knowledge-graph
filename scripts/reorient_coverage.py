"""Backward-compatible migration to a coverage-first USMLE data model."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"

CORE_SYSTEMS = {
    "Cardiology",
    "Neurology",
    "Renal and Genitourinary",
    "Musculoskeletal and Rheumatology",
}
ENTITY_TABLES = [
    "diseases.csv",
    "presentations.csv",
    "treatments.csv",
    "medications.csv",
    "diagnostics.csv",
    "algorithms.csv",
    "complications.csv",
    "symptoms.csv",
    "physical_findings.csv",
    "laboratory_findings.csv",
    "imaging_findings.csv",
    "procedures.csv",
]
RELATIONSHIP_DEFAULTS = {
    "disease_presentations.csv": {
        "relationship_role": "common",
        "typicality": "typical",
        "frequency_category": "common",
        "acuity": "variable",
        "age_context": "all ages as clinically relevant",
        "pregnancy_context": "not specific",
        "clinical_setting": "outpatient, emergency, or inpatient according to acuity",
        "key_positive_clues": "Use the linked disease illness script and localizing findings.",
        "key_negative_clues": "Interpret key absent findings in clinical context.",
        "cannot_miss": "false",
        "step_levels": "Step 1; Step 2 CK; Step 3",
        "subject_exams": "Internal Medicine; Surgery; Family Medicine; Pediatrics; Neurology; Emergency Medicine",
        "source_status": "partially_source_supported",
    },
    "disease_treatments.csv": {
        "patient_stability": "stable or unstable according to linked clinical context",
        "rescue": "false",
        "refractory": "false",
        "contraindicated": "false",
        "avoid": "false",
        "age_context": "all ages as clinically relevant",
        "pregnancy_context": "assess pregnancy context before selection",
        "renal_context": "assess renal function where relevant",
        "hepatic_context": "assess hepatic function where relevant",
        "prerequisite_actions": "Stabilize immediate threats and establish diagnosis where appropriate.",
        "monitoring": "Reassess response, adverse effects, and disposition.",
        "step_levels": "Step 1; Step 2 CK; Step 3",
        "subject_exams": "Internal Medicine; Surgery; Family Medicine; Pediatrics; Neurology; Emergency Medicine",
        "source_status": "partially_source_supported",
    },
    "disease_diagnostics.csv": {
        "clinical_context": "Use after history, examination, and stability assessment.",
        "sequence_order": "1",
        "patient_stability": "stable or unstable according to presentation",
        "expected_result": "Interpret in the context of the suspected syndrome.",
        "interpretation": "A single test is not independently diagnostic unless specified by its role.",
        "limitations": "Timing, pretest probability, and specimen or imaging quality affect interpretation.",
        "test_to_avoid": "",
        "age_context": "all ages as clinically relevant",
        "pregnancy_context": "consider radiation and pregnancy-safe alternatives",
        "step_levels": "Step 1; Step 2 CK; Step 3",
        "subject_exams": "Internal Medicine; Surgery; Family Medicine; Pediatrics; Neurology; Emergency Medicine",
        "source_status": "partially_source_supported",
    },
    "disease_differentials.csv": {
        "commonness": "variable",
        "pregnancy_context": "consider when relevant",
        "clinical_setting": "outpatient, emergency, or inpatient according to acuity",
        "findings_favoring_target": "Use the existing distinguishing features with timing and localization.",
        "findings_favoring_competitor": "Use the competing pattern and key negative findings.",
        "key_negative_findings": "Absence of expected features modifies but does not alone exclude probability.",
        "next_test_to_distinguish": "Select the linked initial or confirmatory diagnostic pathway.",
        "step_levels": "Step 1; Step 2 CK; Step 3",
        "subject_exams": "Internal Medicine; Surgery; Family Medicine; Pediatrics; Neurology; Emergency Medicine",
        "source_status": "partially_source_supported",
    },
}

KEYWORDS = {
    "tearing chest pain": (
        "classic_clue",
        "Abrupt tearing chest or back pain is a high-risk clue for acute aortic pathology.",
    ),
    "muddy brown casts": (
        "laboratory_pattern",
        "Granular muddy-brown casts support tubular injury in the appropriate acute kidney injury context.",
    ),
    "red blood cell casts": (
        "laboratory_pattern",
        "Red-cell casts support glomerular bleeding rather than a lower urinary source.",
    ),
    "ascending weakness": (
        "classic_clue",
        "Ascending weakness with areflexia localizes to an acute peripheral neuropathy pattern.",
    ),
    "thunderclap headache": (
        "classic_clue",
        "Abrupt maximal-intensity headache requires assessment for dangerous secondary causes.",
    ),
    "resting tremor": (
        "physical_exam_phrase",
        "Resting tremor with bradykinesia and rigidity supports a parkinsonian syndrome.",
    ),
    "pain out of proportion": (
        "classic_clue",
        "Pain out of proportion may indicate compartment physiology, ischemia, or necrotizing infection and needs urgent context-specific assessment.",
    ),
    "bamboo spine": (
        "imaging_phrase",
        "Spinal ankylosis on imaging supports axial spondyloarthritis in the appropriate clinical context.",
    ),
    "pencil-in-cup": (
        "imaging_phrase",
        "A pencil-in-cup erosive pattern is a classic imaging association of psoriatic arthritis.",
    ),
    "sunburst periosteal reaction": (
        "imaging_phrase",
        "A sunburst periosteal pattern raises concern for an aggressive bone-forming lesion and requires specialist-directed workup.",
    ),
    "onion-skin periosteal reaction": (
        "imaging_phrase",
        "Layered onion-skin periosteal reaction is an imaging association of Ewing sarcoma but is not independently diagnostic.",
    ),
    "red hot swollen joint": (
        "physical_exam_phrase",
        "An acutely inflamed joint requires prompt distinction of infection from crystal and inflammatory causes.",
    ),
    "boot-shaped heart": (
        "imaging_phrase",
        "A boot-shaped cardiac silhouette is a classic association of tetralogy of Fallot.",
    ),
    "water-hammer pulse": (
        "physical_exam_phrase",
        "A bounding water-hammer pulse is a classic clue for significant aortic regurgitation.",
    ),
    "electric shock sensation with neck flexion": (
        "physical_exam_phrase",
        "An electric sensation provoked by neck flexion can support a cervical cord process in the right context.",
    ),
    "target lesions": (
        "pathology_phrase",
        "Target lesions are a pattern requiring dermatologic and infectious or medication context.",
    ),
}

KEYWORD_DISEASES = {
    "tearing chest pain": ["Aortic dissection"],
    "muddy brown casts": ["Ischemic acute tubular necrosis", "Acute kidney injury"],
    "red blood cell casts": ["Nephritic syndrome", "Rapidly progressive glomerulonephritis"],
    "ascending weakness": ["Guillain-Barré syndrome"],
    "thunderclap headache": ["Subarachnoid hemorrhage"],
    "resting tremor": ["Parkinson disease"],
    "pain out of proportion": [
        "Acute compartment syndrome",
        "Acute limb ischemia",
        "Necrotizing soft-tissue infection",
    ],
    "bamboo spine": ["Ankylosing spondylitis"],
    "pencil-in-cup": ["Psoriatic arthritis"],
    "sunburst periosteal reaction": ["Osteosarcoma"],
    "onion-skin periosteal reaction": ["Ewing sarcoma"],
    "red hot swollen joint": ["Septic arthritis", "Acute gout flare"],
    "boot-shaped heart": ["Tetralogy of Fallot"],
    "water-hammer pulse": ["Aortic regurgitation"],
    "electric shock sensation with neck flexion": ["Multiple sclerosis"],
    "target lesions": ["Erythema multiforme"],
}

COMPLICATIONS = [
    "Acute compartment syndrome",
    "Avascular necrosis",
    "Nonunion",
    "Septic arthritis",
    "Papillary muscle rupture",
    "Ventricular septal rupture",
    "Free-wall rupture",
    "Thrombosis",
    "Acute chest syndrome",
    "Stroke",
    "Splenic sequestration",
    "Hearing loss",
    "Hydrocephalus",
]


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def add_columns(path: Path, defaults: dict[str, str]) -> None:
    headers, rows = read(path)
    for column in defaults:
        if column not in headers:
            headers.append(column)
    for row in rows:
        for column, value in defaults.items():
            row.setdefault(column, value)
    write(path, headers, rows)


def source_status(row: dict[str, str]) -> str:
    return (
        "partially_source_supported"
        if row.get("source_review_status") == "source_checked"
        else "unverified_ai_generated"
    )


def scrub(value: str) -> str:
    value = re.sub(r";?\s*qualified clinician review pending\.?", "", value, flags=re.IGNORECASE)
    value = re.sub(r";?\s*clinician review pending\.?", "", value, flags=re.IGNORECASE)
    value = re.sub(
        r";?\s*requires source and physician review\.?",
        "; Source support varies by linked topic.",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"human review required\.?",
        "source status shown with the record.",
        value,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s{2,}", " ", value).strip()


def migrate_entities() -> None:
    for filename in ENTITY_TABLES:
        path = SOURCE / filename
        headers, rows = read(path)
        for column in ("source_status", "human_review_status", "content_tier"):
            if column not in headers:
                headers.append(column)
        if filename == "diseases.csv":
            for column in ("step_levels", "subject_exams", "tested_as"):
                if column not in headers:
                    headers.append(column)
        for row in rows:
            row["source_status"] = source_status(row)
            row["human_review_status"] = "not_requested"
            row["content_tier"] = (
                "core"
                if filename == "diseases.csv" and row.get("organ_system_primary") in CORE_SYSTEMS
                else "index"
            )
            if filename == "diseases.csv":
                row["step_levels"] = "Step 1; Step 2 CK; Step 3"
                row["subject_exams"] = (
                    "Internal Medicine; Surgery; Pediatrics; Family Medicine; Neurology; Emergency Medicine"
                )
                row["tested_as"] = (
                    "definition; presentation; diagnostic_test; differential_diagnosis; first_line_treatment; complication"
                )
            if "notes" in row:
                row["notes"] = scrub(row["notes"])
        write(path, headers, rows)
    for filename, defaults in RELATIONSHIP_DEFAULTS.items():
        add_columns(REL / filename, defaults)
    add_columns(
        REL / "entity_references.csv",
        {
            "date_verified": "",
            "verification_notes": "Linked source support is topic-specific; no entity-wide completeness claim.",
        },
    )
    for path in [*SOURCE.glob("*.csv"), *REL.glob("*.csv")]:
        headers, rows = read(path)
        for row in rows:
            for key, value in row.items():
                row[key] = scrub(value)
        write(path, headers, rows)


def build_keywords(diseases: list[dict[str, str]]) -> None:
    headers = [
        "keyword_id",
        "keyword_text",
        "keyword_type",
        "normalized_keyword",
        "clinical_meaning",
        "source_status",
        "deprecated",
        "notes",
    ]
    keywords = [
        {
            "keyword_id": f"KEY-{i:03d}",
            "keyword_text": text,
            "keyword_type": kind,
            "normalized_keyword": text.lower(),
            "clinical_meaning": meaning,
            "source_status": "partially_source_supported",
            "deprecated": "false",
            "notes": "Original board-recognition clue with explanatory context.",
        }
        for i, (text, (kind, meaning)) in enumerate(KEYWORDS.items(), 1)
    ]
    write(SOURCE / "keywords.csv", headers, keywords)
    ids = {row["canonical_name"]: row["disease_id"] for row in diseases}
    key_ids = {row["keyword_text"]: row["keyword_id"] for row in keywords}
    rel_headers = [
        "disease_keyword_id",
        "disease_id",
        "keyword_id",
        "relevance",
        "specificity",
        "classic_for_disease",
        "commonly_tested",
        "step_levels",
        "subject_exams",
        "explanation",
        "source_status",
    ]
    links = []
    for text, names in KEYWORD_DISEASES.items():
        for name in names:
            if name in ids:
                links.append(
                    {
                        "disease_keyword_id": f"DKW-{len(links) + 1:03d}",
                        "disease_id": ids[name],
                        "keyword_id": key_ids[text],
                        "relevance": "high",
                        "specificity": "supportive rather than independently diagnostic",
                        "classic_for_disease": "true",
                        "commonly_tested": "true",
                        "step_levels": "Step 1; Step 2 CK; Step 3",
                        "subject_exams": "Internal Medicine; Surgery; Pediatrics; Neurology; Emergency Medicine",
                        "explanation": KEYWORDS[text][1],
                        "source_status": "partially_source_supported",
                    }
                )
    write(REL / "disease_keywords.csv", rel_headers, links)
    presentation_headers = [
        "presentation_keyword_id",
        "presentation_id",
        "keyword_id",
        "relationship_role",
        "explanation",
        "source_status",
    ]
    _, presentations = read(SOURCE / "presentations.csv")
    presentation_ids = {row["name"]: row["presentation_id"] for row in presentations}
    presentation_links = []
    for presentation, text in [
        ("Back pain with neurologic deficit", "pain out of proportion"),
        ("Acute monoarthritis", "red hot swollen joint"),
        ("Acute traumatic limb pain", "pain out of proportion"),
        ("Elevated creatinine", "muddy brown casts"),
    ]:
        if presentation in presentation_ids:
            presentation_links.append(
                {
                    "presentation_keyword_id": f"PKW-{len(presentation_links) + 1:03d}",
                    "presentation_id": presentation_ids[presentation],
                    "keyword_id": key_ids[text],
                    "relationship_role": "classic_clue",
                    "explanation": KEYWORDS[text][1],
                    "source_status": "partially_source_supported",
                }
            )
    write(REL / "presentation_keywords.csv", presentation_headers, presentation_links)


def build_complications(diseases: list[dict[str, str]]) -> None:
    headers, rows = read(SOURCE / "complications.csv")
    existing = {row["name"]: row["entity_id"] for row in rows}
    for name in COMPLICATIONS:
        if name not in existing:
            entity_id = f"COM-COV-{len(existing) + 1:03d}"
            rows.append(
                {
                    "entity_id": entity_id,
                    "name": name,
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                    "deprecated": "false",
                }
            )
            existing[name] = entity_id
    write(SOURCE / "complications.csv", headers, rows)
    links = []
    by_name = {row["canonical_name"]: row["disease_id"] for row in diseases}
    mappings = {
        "Myocardial infarction": [
            "Papillary muscle rupture",
            "Ventricular septal rupture",
            "Free-wall rupture",
        ],
        "NSTEMI": ["Papillary muscle rupture"],
        "STEMI": ["Papillary muscle rupture", "Ventricular septal rupture", "Free-wall rupture"],
        "Nephrotic syndrome": ["Thrombosis"],
        "Acute compartment syndrome": ["Acute compartment syndrome"],
        "Femoral neck fracture": ["Avascular necrosis", "Nonunion"],
        "Meningitis": ["Hearing loss", "Hydrocephalus"],
        "Sickle cell disease": ["Acute chest syndrome", "Stroke", "Splenic sequestration"],
    }
    for disease_name, complications in mappings.items():
        if disease_name not in by_name:
            continue
        for complication in complications:
            links.append(
                {
                    "disease_complication_id": f"DCP-{len(links) + 1:03d}",
                    "disease_id": by_name[disease_name],
                    "complication_id": existing[complication],
                    "timing": "acute or delayed according to disease course",
                    "frequency_category": "clinically important",
                    "severity": "high",
                    "cannot_miss": "true",
                    "risk_factors": "Use disease-specific risk factors and trajectory.",
                    "warning_findings": "New instability, organ dysfunction, focal deficit, or escalating pain warrants reassessment.",
                    "prevention": "Use disease-specific prevention and timely follow-up.",
                    "initial_management": "Stabilize and escalate according to the complication pathway.",
                    "step_levels": "Step 1; Step 2 CK; Step 3",
                    "subject_exams": "Internal Medicine; Surgery; Pediatrics; Emergency Medicine",
                    "source_status": "partially_source_supported",
                }
            )
    headers = [
        "disease_complication_id",
        "disease_id",
        "complication_id",
        "timing",
        "frequency_category",
        "severity",
        "cannot_miss",
        "risk_factors",
        "warning_findings",
        "prevention",
        "initial_management",
        "step_levels",
        "subject_exams",
        "source_status",
    ]
    write(REL / "disease_complications.csv", headers, links)


def main() -> None:
    migrate_entities()
    _, diseases = read(SOURCE / "diseases.csv")
    build_keywords(diseases)
    build_complications(diseases)


if __name__ == "__main__":
    main()
