"""Create the initial, explicitly draft, canonical seed tables.

This one-time bootstrap is deliberately deterministic. The generated CSVs are
committed canonical data and should thereafter be edited through review.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"
REF = ROOT / "data" / "reference"
DISEASES = {
    "Cardiology": "Acute coronary syndrome|Aortic dissection|Acute pericarditis|Cardiac tamponade|Cardiogenic shock|Atrial fibrillation|Atrial flutter|Supraventricular tachycardia|Ventricular tachycardia|Heart failure|Hypertrophic cardiomyopathy|Infective endocarditis|Aortic stenosis|Mitral regurgitation|Pulmonary embolism",
    "Pulmonology": "Asthma exacerbation|Chronic obstructive pulmonary disease exacerbation|Pneumonia|Pneumothorax|Tension pneumothorax|Acute respiratory distress syndrome|Interstitial lung disease|Obstructive sleep apnea|Pulmonary hypertension|Tuberculosis",
    "Gastroenterology": "Upper gastrointestinal bleeding|Lower gastrointestinal bleeding|Peptic ulcer disease|Acute pancreatitis|Acute cholecystitis|Ascending cholangitis|Hepatitis|Cirrhosis|Spontaneous bacterial peritonitis|Inflammatory bowel disease|Small bowel obstruction|Mesenteric ischemia",
    "Nephrology": "Acute kidney injury|Chronic kidney disease|Nephrotic syndrome|Nephritic syndrome|Pyelonephritis|Renal colic|Hyperkalemia|Hyponatremia|Metabolic acidosis|Renal tubular acidosis",
    "Endocrinology": "Diabetic ketoacidosis|Hyperosmolar hyperglycemic state|Hypoglycemia|Thyroid storm|Myxedema coma|Primary adrenal insufficiency|Cushing syndrome|Pheochromocytoma|Hypercalcemia|Diabetes mellitus",
    "Neurology": "Acute ischemic stroke|Intracerebral hemorrhage|Subarachnoid hemorrhage|Seizure disorder|Status epilepticus|Meningitis|Encephalitis|Multiple sclerosis|Parkinson disease|Myasthenia gravis|Guillain-Barre syndrome|Delirium",
    "Infectious Disease": "Sepsis|Anaphylaxis|Cellulitis|Osteomyelitis|Human immunodeficiency virus infection|Infective diarrhea|Clostridioides difficile infection|Malaria|Lyme disease|Toxic shock syndrome",
    "Hematology Oncology": "Iron deficiency anemia|Hemolytic anemia|Sickle cell disease|Immune thrombocytopenia|Disseminated intravascular coagulation|Acute leukemia|Lymphoma|Multiple myeloma|Neutropenic fever|Tumor lysis syndrome",
    "Rheumatology": "Systemic lupus erythematosus|Rheumatoid arthritis|Gout|Septic arthritis|Vasculitis|Polymyalgia rheumatica|Giant cell arteritis|Scleroderma",
    "Psychiatry": "Major depressive disorder|Bipolar disorder|Schizophrenia|Panic disorder|Generalized anxiety disorder|Alcohol withdrawal|Opioid use disorder|Delirium tremens",
    "Pediatrics": "Bronchiolitis|Croup|Epiglottitis|Kawasaki disease|Pediatric sepsis|Intussusception|Pyloric stenosis|Febrile seizure",
    "Obstetrics Gynecology": "Ectopic pregnancy|Preeclampsia|Eclampsia|Placental abruption|Placenta previa|Postpartum hemorrhage|Pelvic inflammatory disease|Ovarian torsion",
    "Surgery Trauma": "Hemorrhagic shock|Traumatic brain injury|Spinal cord injury|Compartment syndrome|Necrotizing soft tissue infection|Acute appendicitis|Testicular torsion|Burn injury",
}
PRESENTATIONS = [
    "Chest pain",
    "Dyspnea",
    "Syncope",
    "Palpitations",
    "Fever",
    "Altered mental status",
    "Headache",
    "Focal neurologic deficit",
    "Seizure",
    "Abdominal pain",
    "Nausea and vomiting",
    "Diarrhea",
    "Gastrointestinal bleeding",
    "Jaundice",
    "Dysuria",
    "Hematuria",
    "Acute kidney injury",
    "Edema",
    "Rash",
    "Joint pain",
    "Weakness",
    "Fatigue",
    "Anemia",
    "Lymphadenopathy",
    "Weight loss",
    "Hyperglycemia",
    "Hypoglycemia",
    "Vaginal bleeding",
    "Pelvic pain",
    "Amenorrhea",
    "Pregnancy with abdominal pain",
    "Pediatric fever",
    "Neonatal respiratory distress",
    "Trauma",
    "Shock",
    "Back pain",
    "Cough",
    "Hemoptysis",
    "Oliguria",
    "Confusion",
]
TREATMENTS = [
    "Airway assessment",
    "Supplemental oxygen",
    "Intravenous fluids",
    "Blood product resuscitation",
    "Anticoagulation",
    "Antiplatelet therapy",
    "Thrombolysis evaluation",
    "Urgent reperfusion",
    "Rate control",
    "Rhythm control",
    "Defibrillation",
    "Synchronized cardioversion",
    "Broad-spectrum antibiotics",
    "Source control",
    "Vasopressor support",
    "Corticosteroids",
    "Bronchodilator therapy",
    "Noninvasive ventilation",
    "Mechanical ventilation",
    "Diuresis",
    "Insulin therapy",
    "Glucose administration",
    "Electrolyte correction",
    "Seizure precautions",
    "Antiseizure therapy",
    "Surgical consultation",
    "Emergency surgery",
    "Endoscopic intervention",
    "Interventional radiology",
    "Pain control",
    "Antiemetic therapy",
    "Fluid restriction",
    "Renal replacement therapy",
    "Antidote administration",
    "Immunosuppression",
    "Psychiatric safety assessment",
    "Obstetric consultation",
    "Fetal monitoring",
    "Rh immune globulin",
    "Magnesium sulfate",
    "Antihypertensive therapy",
    "Wound care",
    "Burn resuscitation",
    "Tetanus prophylaxis",
    "Isolation precautions",
    "Vaccination",
    "Rehabilitation",
    "Palliative consultation",
    "Observation",
    "Hospital admission",
    "Intensive care admission",
    "Discharge planning",
    "Follow-up planning",
    "Smoking cessation",
    "Nutrition support",
    "Thromboprophylaxis",
    "Stress ulcer prophylaxis",
    "Bowel rest",
    "Transfusion support",
    "Platelet transfusion",
    "Neutropenic precautions",
    "Antiviral therapy",
    "Antifungal therapy",
    "Antiparasitic therapy",
    "Antitoxin therapy",
    "Decontamination",
    "Temperature management",
    "Hypothermia prevention",
    "Splinting",
    "Immobilization",
    "Physical therapy",
    "Occupational therapy",
    "Speech therapy",
    "Behavioral therapy",
    "Psychotherapy",
    "Substance withdrawal protocol",
    "Medication reconciliation",
    "Consultation",
    "Transfer to higher level of care",
]
MEDS = [
    "Aspirin",
    "Heparin",
    "Warfarin",
    "Apixaban",
    "Alteplase",
    "Epinephrine",
    "Norepinephrine",
    "Dopamine",
    "Furosemide",
    "Metoprolol",
    "Diltiazem",
    "Amiodarone",
    "Adenosine",
    "Nitroglycerin",
    "Morphine",
    "Albuterol",
    "Ipratropium",
    "Prednisone",
    "Methylprednisolone",
    "Ceftriaxone",
    "Vancomycin",
    "Piperacillin-tazobactam",
    "Azithromycin",
    "Acyclovir",
    "Fluconazole",
    "Insulin",
    "Dextrose",
    "Glucagon",
    "Calcium gluconate",
    "Sodium bicarbonate",
    "Sodium chloride",
    "Magnesium sulfate",
    "Levetiracetam",
    "Lorazepam",
    "Haloperidol",
    "Olanzapine",
    "Sertraline",
    "Lithium",
    "Levothyroxine",
    "Propylthiouracil",
    "Hydrocortisone",
    "Fludrocortisone",
    "Allopurinol",
    "Colchicine",
    "Methotrexate",
    "Hydroxychloroquine",
    "Oxytocin",
    "Misoprostol",
    "Rho immune globulin",
    "Naloxone",
]
DIAGS = [
    "Electrocardiogram",
    "Chest radiograph",
    "Complete blood count",
    "Basic metabolic panel",
    "Comprehensive metabolic panel",
    "Troponin assay",
    "Urinalysis",
    "Blood cultures",
    "Computed tomography",
    "Magnetic resonance imaging",
    "Ultrasound",
    "Echocardiography",
    "Arterial blood gas",
    "Venous blood gas",
    "Lactate",
    "D-dimer",
    "Coagulation studies",
    "Lumbar puncture",
    "Electroencephalogram",
    "Cardiac catheterization",
    "Endoscopy",
    "Colonoscopy",
    "Pregnancy test",
    "Peripheral smear",
    "Thyroid studies",
    "Hemoglobin A1c",
    "B-type natriuretic peptide",
    "Lipase",
    "Liver panel",
    "Drug screen",
]
ALGS = [
    "Acute chest pain",
    "Acute dyspnea",
    "Undifferentiated shock",
    "Altered mental status",
    "Acute focal neurologic deficit",
    "First seizure",
    "Acute abdominal pain",
    "Upper gastrointestinal bleeding",
    "Lower gastrointestinal bleeding",
    "Acute kidney injury",
    "Hyperkalemia",
    "Hyponatremia",
    "Vaginal bleeding in pregnancy",
    "Pediatric fever",
    "Anaphylaxis",
]


def write(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def status() -> dict[str, str]:
    return {
        "source_review_status": "draft_ai_generated",
        "medical_review_status": "draft_ai_generated",
        "deprecated": "false",
        "notes": "Requires source and physician review.",
    }


def main() -> None:
    diseases = []
    n = 0
    for organ, names in DISEASES.items():
        code = "".join(x[0] for x in organ.split())[:4].upper()
        for name in names.split("|"):
            n += 1
            diseases.append(
                {
                    "disease_id": f"DIS-{code}-{n:04d}",
                    "canonical_name": name,
                    "concise_definition": "Draft educational illness-script placeholder pending human review.",
                    "organ_system_primary": organ,
                    "board_exam_priority": str(1 + (n % 5)),
                    "time_course": "variable",
                    "severity_or_acuity": "variable",
                    "epidemiology_summary": "Draft content pending review.",
                    "risk_factors_summary": "Draft content pending review.",
                    "pathophysiology_summary": "Draft content pending review.",
                    "classic_presentation_summary": "Draft content pending review.",
                    "key_distinguishing_features": "Draft content pending review.",
                    "common_board_traps": "Draft content pending review.",
                    "emergency_red_flags": "Review required.",
                    "disposition_summary": "Review required.",
                    "prognosis_summary": "Review required.",
                    "last_reviewed_date": "",
                    "replacement_disease_id": "",
                    **status(),
                }
            )
    write(SOURCE / "diseases.csv", list(diseases[0]), diseases)
    presentations = [
        {
            "presentation_id": f"PRS-{i:03d}",
            "name": name,
            "concise_definition": "Draft educational presentation summary.",
            "emergency_priority": str(1 + (i % 5)),
            "initial_stabilization_summary": "Assess stability; human review required.",
            "key_history_questions": "Draft pending review.",
            "key_exam_focus": "Draft pending review.",
            "initial_test_categories": "Draft pending review.",
            **status(),
        }
        for i, name in enumerate(PRESENTATIONS, 1)
    ]
    write(SOURCE / "presentations.csv", list(presentations[0]), presentations)
    treatments = [
        {
            "treatment_id": f"TRT-{i:03d}",
            "name": name,
            "treatment_type": "intervention",
            "treatment_category": "general",
            "general_description": "Draft educational treatment concept; not dosing guidance.",
            "mechanism_summary": "Draft pending review.",
            "major_contraindications": "Review required.",
            "monitoring_summary": "Review required.",
            "pregnancy_context": "Review required.",
            "pediatric_context": "Review required.",
            "renal_context": "Review required.",
            "hepatic_context": "Review required.",
            "emergency_role": "variable",
            **status(),
        }
        for i, name in enumerate(TREATMENTS, 1)
    ]
    write(SOURCE / "treatments.csv", list(treatments[0]), treatments)
    meds = [
        {
            "medication_id": f"MED-{i:03d}",
            "generic_name": name,
            "medication_class": "review_required",
            "mechanism_summary": "Draft pending review.",
            "major_adverse_effects_summary": "Review required.",
            "major_contraindications_summary": "Review required.",
            "monitoring_summary": "Review required.",
            "reversal_agent_summary": "Review required.",
            "pregnancy_context": "Review required.",
            "renal_adjustment_context": "Review required.",
            "hepatic_adjustment_context": "Review required.",
            **status(),
        }
        for i, name in enumerate(MEDS, 1)
    ]
    write(SOURCE / "medications.csv", list(meds[0]), meds)
    diagnostics = [
        {
            "diagnostic_id": f"DIA-{i:03d}",
            "name": name,
            "diagnostic_type": "test",
            "specimen_or_modality": "review_required",
            "general_description": "Draft diagnostic concept.",
            "limitations_summary": "Review required.",
            "contraindications_summary": "Review required.",
            **status(),
        }
        for i, name in enumerate(DIAGS, 1)
    ]
    write(SOURCE / "diagnostics.csv", list(diagnostics[0]), diagnostics)
    algorithms = [
        {
            "algorithm_id": f"ALG-{i:03d}",
            "name": name,
            "triggering_presentation_id": presentations[(i - 1) % len(presentations)][
                "presentation_id"
            ],
            "clinical_setting": "acute care",
            "age_context": "all",
            "pregnancy_context": "context dependent",
            "objective": "Draft educational pathway.",
            "starting_node_id": f"NODE-{i:03d}-START",
            "emergency_status": "review required",
            "version": "0.1.0",
            **status(),
        }
        for i, name in enumerate(ALGS, 1)
    ]
    write(SOURCE / "algorithms.csv", list(algorithms[0]), algorithms)
    write(
        SOURCE / "references.csv",
        [
            "reference_id",
            "title",
            "organization_or_author",
            "source_type",
            "publication_year",
            "url",
            "date_accessed",
            "relevant_topic",
            "notes",
            "verification_status",
        ],
        [],
    )
    dps = []
    dts = []
    dds = []
    ddf = []
    for i, d in enumerate(diseases):
        dps.append(
            {
                "disease_presentation_id": f"DPR-{i + 1:04d}",
                "disease_id": d["disease_id"],
                "presentation_id": presentations[i % len(presentations)]["presentation_id"],
                "source_review_status": "draft_ai_generated",
                "medical_review_status": "draft_ai_generated",
            }
        )
        for offset in range(3):
            dts.append(
                {
                    "disease_treatment_id": f"DTR-{i + 1:04d}-{offset}",
                    "disease_id": d["disease_id"],
                    "treatment_id": treatments[(i + offset) % len(treatments)]["treatment_id"],
                    "role": "first_line" if offset == 0 else "adjunctive",
                    "clinical_context": "Draft context pending review.",
                    "sequence_order": str(offset + 1),
                    "first_line": "true" if offset == 0 else "false",
                    "definitive": "false",
                    "rescue_or_escalation": "false",
                    "unstable_patient_only": "false",
                    "contraindication_notes": "Review required.",
                    "board_exam_pearl": "Draft pending review.",
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                    "notes": "",
                }
            )
        for offset in range(2):
            dds.append(
                {
                    "disease_diagnostic_id": f"DDG-{i + 1:04d}-{offset}",
                    "disease_id": d["disease_id"],
                    "diagnostic_id": diagnostics[(i + offset) % len(diagnostics)]["diagnostic_id"],
                    "role": "initial" if offset == 0 else "confirmatory",
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                }
            )
        for offset in range(3):
            other = diseases[(i + offset + 1) % len(diseases)]
            ddf.append(
                {
                    "differential_link_id": f"DFL-{i + 1:04d}-{offset}",
                    "source_disease_id": d["disease_id"],
                    "competing_disease_id": other["disease_id"],
                    "presentation_id": presentations[i % len(presentations)]["presentation_id"],
                    "similarity_reason": "Draft comparison pending review.",
                    "distinguishing_features": "Draft comparison pending review.",
                    "cannot_miss": "true" if offset == 0 else "false",
                    "relative_priority": str(offset + 1),
                    "age_context": "all",
                    "rotation_context": "review_required",
                    "exam_context": "all",
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                    "notes": "",
                }
            )
    for name, rows in [
        ("disease_presentations", dps),
        ("disease_treatments", dts),
        ("disease_diagnostics", dds),
        ("disease_differentials", ddf),
    ]:
        write(REL / f"{name}.csv", list(rows[0]), rows)
    steps = []
    for i, a in enumerate(algorithms, 1):
        steps.extend(
            [
                {
                    "algorithm_step_id": f"AST-{i:03d}-1",
                    "algorithm_id": a["algorithm_id"],
                    "node_id": a["starting_node_id"],
                    "node_type": "start",
                    "prompt_or_action": "Assess immediate stability.",
                    "condition_expression": "",
                    "next_node_if_true": "",
                    "next_node_if_false": "",
                    "next_node_default": f"NODE-{i:03d}-END",
                    "terminal_outcome": "",
                    "sequence_hint": "1",
                    "explanation": "Draft educational graph.",
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                },
                {
                    "algorithm_step_id": f"AST-{i:03d}-2",
                    "algorithm_id": a["algorithm_id"],
                    "node_id": f"NODE-{i:03d}-END",
                    "node_type": "terminal",
                    "prompt_or_action": "Escalate according to reviewed local protocol.",
                    "condition_expression": "",
                    "next_node_if_true": "",
                    "next_node_if_false": "",
                    "next_node_default": "",
                    "terminal_outcome": "review_required",
                    "sequence_hint": "2",
                    "explanation": "Draft educational graph.",
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                },
            ]
        )
    write(REL / "algorithm_steps.csv", list(steps[0]), steps)
    for filename in [
        "symptoms.csv",
        "physical_findings.csv",
        "laboratory_findings.csv",
        "imaging_findings.csv",
        "procedures.csv",
        "complications.csv",
    ]:
        write(
            SOURCE / filename,
            ["entity_id", "name", "source_review_status", "medical_review_status", "deprecated"],
            [],
        )
    for filename, values in {
        "organ_systems.csv": list(DISEASES),
        "review_statuses.csv": ["draft_ai_generated", "source_reviewed", "medically_reviewed"],
        "exam_levels.csv": ["Step 1", "Step 2 CK", "Step 3"],
        "rotations.csv": [
            "Internal Medicine",
            "Surgery",
            "Pediatrics",
            "OB/GYN",
            "Psychiatry",
            "Family Medicine",
            "Neurology",
        ],
        "preclinical_blocks.csv": ["Cardiovascular", "Pulmonary", "Renal", "Neurology"],
        "age_groups.csv": ["adult", "pediatric", "pregnancy"],
        "acuity_levels.csv": ["routine", "urgent", "emergent"],
        "treatment_roles.csv": [
            "stabilization",
            "first_line",
            "adjunctive",
            "definitive",
            "rescue",
            "avoid",
        ],
        "diagnostic_roles.csv": [
            "initial",
            "screening",
            "confirmatory",
            "most_accurate",
            "gold_standard",
            "monitoring",
        ],
        "node_types.csv": [
            "start",
            "stabilization",
            "history",
            "examination",
            "test",
            "decision",
            "treatment",
            "consultation",
            "disposition",
            "reassessment",
            "terminal",
        ],
        "shelf_exams.csv": [
            "Internal Medicine",
            "Surgery",
            "Pediatrics",
            "OB/GYN",
            "Psychiatry",
            "Family Medicine",
            "Neurology",
        ],
    }.items():
        write(
            REF / filename,
            ["id", "name"],
            [{"id": f"REF-{i:03d}", "name": v} for i, v in enumerate(values, 1)],
        )


if __name__ == "__main__":
    main()
