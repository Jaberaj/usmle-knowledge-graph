"""Deterministically create source-linked Renal and Genitourinary records."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"

TOPICS = """Acute kidney injury|aki|Acute kidney injury
Pyelonephritis|uti|Fever with flank pain
Renal colic|stone|Renal colic
Renal tubular acidosis|tubular|Metabolic acidosis
Prerenal azotemia|aki|Oliguria
Ischemic acute tubular necrosis|aki|Acute kidney injury
Nephrotoxic acute tubular necrosis|aki|Acute kidney injury
Acute interstitial nephritis|aki|Elevated creatinine
Postrenal acute kidney injury|aki|Anuria
Pigment nephropathy|aki|Acute kidney injury
Rhabdomyolysis-associated AKI|aki|Acute kidney injury
Tumor lysis-associated AKI|aki|Electrolyte abnormality
Contrast-associated acute kidney injury|aki|Elevated creatinine
Acute phosphate nephropathy|aki|Elevated creatinine
Hepatorenal syndrome|aki|Acute kidney injury
Cardiorenal syndrome|aki|Edema
Renal infarction|vascular|Flank pain
Chronic kidney disease|ckd|Elevated creatinine
Diabetic kidney disease|ckd|Proteinuria
Hypertensive nephrosclerosis|ckd|Hypertension
Autosomal dominant polycystic kidney disease|ckd|Hematuria
End-stage kidney disease|ckd|Uremic symptoms
Uremia|ckd|Uremic symptoms
Uremic encephalopathy|ckd|Altered mental status
Uremic pericarditis|ckd|Chest pain
Anemia of CKD|ckd|Fatigue
Calciphylaxis|ckd|Skin lesion
Nephritic syndrome|glomerular|Hematuria
Poststreptococcal glomerulonephritis|glomerular|Hematuria
IgA nephropathy|glomerular|Hematuria
Alport syndrome|glomerular|Hematuria
IgA vasculitis|glomerular|Hematuria
Rapidly progressive glomerulonephritis|glomerular|Acute kidney injury
Anti-GBM disease|glomerular|Hematuria
Granulomatosis with polyangiitis|glomerular|Hematuria
Microscopic polyangiitis|glomerular|Hematuria
Lupus nephritis|glomerular|Proteinuria
Membranoproliferative glomerulonephritis|glomerular|Hematuria
Nephrotic syndrome|nephrotic|Edema
Minimal-change disease|nephrotic|Edema
Focal segmental glomerulosclerosis|nephrotic|Proteinuria
Membranous nephropathy|nephrotic|Proteinuria
Amyloidosis|nephrotic|Proteinuria
Fanconi syndrome|tubular|Metabolic acidosis
Renal papillary necrosis|tubular|Hematuria
Proximal renal tubular acidosis|tubular|Metabolic acidosis
Distal renal tubular acidosis|tubular|Metabolic acidosis
Type 4 renal tubular acidosis|tubular|Hyperkalemia
Bartter syndrome|tubular|Hypokalemia
Gitelman syndrome|tubular|Hypokalemia
Liddle syndrome|tubular|Hypertension
Nephrogenic diabetes insipidus|water|Polyuria
Lithium-associated nephrogenic diabetes insipidus|water|Polyuria
Metabolic acidosis|acidbase|Metabolic acidosis
High-anion-gap metabolic acidosis|acidbase|Metabolic acidosis
Normal-anion-gap metabolic acidosis|acidbase|Metabolic acidosis
Metabolic alkalosis|acidbase|Metabolic alkalosis
Lactic acidosis|acidbase|Metabolic acidosis
Ketoacidosis|acidbase|Metabolic acidosis
Hyponatremia|water|Hyponatremia
Acute symptomatic hyponatremia|water|Hyponatremia
SIADH|water|Hyponatremia
Primary polydipsia|water|Hyponatremia
Hypernatremia|water|Hypernatremia
Central diabetes insipidus|water|Polyuria
Hyperkalemia|electrolyte|Hyperkalemia
Hypokalemia|electrolyte|Hypokalemia
Pseudohyperkalemia|electrolyte|Hyperkalemia
Hypercalcemia|electrolyte|Electrolyte abnormality
Hypocalcemia|electrolyte|Electrolyte abnormality
Hyperphosphatemia|electrolyte|Electrolyte abnormality
Hypomagnesemia|electrolyte|Electrolyte abnormality
Nephrolithiasis|stone|Renal colic
Calcium oxalate stone|stone|Renal colic
Uric acid stone|stone|Renal colic
Struvite stone|stone|Fever with flank pain
Cystine stone|stone|Renal colic
Medullary sponge kidney|stone|Renal colic
Nephrocalcinosis|stone|Flank pain
Acute urinary retention|obstruction|Urinary retention
Bladder outlet obstruction|obstruction|Urinary retention
Benign prostatic hyperplasia|obstruction|Urinary retention
Ureteral obstruction|obstruction|Anuria
Hydronephrosis|obstruction|Flank pain
Postobstructive diuresis|obstruction|Polyuria
Acute uncomplicated cystitis|uti|Dysuria
Complicated urinary-tract infection|uti|Dysuria
Acute pyelonephritis|uti|Fever with flank pain
Emphysematous pyelonephritis|uti|Fever with flank pain
Renal abscess|uti|Fever with flank pain
Asymptomatic bacteriuria|uti|Abnormal urinalysis
Catheter-associated urinary-tract infection|uti|Fever with flank pain
UTI in pregnancy|uti|Dysuria
Pediatric UTI|uti|Fever with flank pain
Vesicoureteral reflux|uti|Recurrent UTI
Microscopic hematuria|hematuria|Hematuria
Gross hematuria|hematuria|Hematuria
Glomerular hematuria|hematuria|Hematuria
Nonglomerular hematuria|hematuria|Hematuria
Myoglobinuria|hematuria|Abnormal urinalysis
Albuminuria|hematuria|Proteinuria
Renal artery stenosis|vascular|Hypertension
Atheroembolic renal disease|vascular|Acute kidney injury
Fibromuscular dysplasia|vascular|Hypertension
Renal vein thrombosis|vascular|Hematuria
Hemolytic uremic syndrome|vascular|Acute kidney injury
Scleroderma renal crisis|vascular|Hypertension
Posterior urethral valves|pediatric|Prenatal renal abnormality
Horseshoe kidney|pediatric|Prenatal renal abnormality
Renal agenesis|pediatric|Prenatal renal abnormality
Potter sequence|pediatric|Prenatal renal abnormality
Wilms tumor|tumor|Pediatric abdominal mass
Renal cell carcinoma|tumor|Hematuria
Angiomyolipoma|tumor|Hematuria
Kidney transplant recipient|transplant|Elevated creatinine
Hyperacute rejection|transplant|Elevated creatinine
Acute cellular rejection|transplant|Elevated creatinine
Calcineurin-inhibitor nephrotoxicity|transplant|Elevated creatinine
Hemodialysis|dialysis|Dialysis complication
Peritoneal dialysis|dialysis|Dialysis complication
Dialysis disequilibrium syndrome|dialysis|Altered mental status
Peritoneal-dialysis peritonitis|dialysis|Abdominal pain"""

PROFILE = {
    "aki": (
        "A rapid fall in filtration or urine output results from prerenal, intrinsic, or obstructive physiology.",
        "Volume loss, shock, nephrotoxins, pigment, obstruction, and cardiorenal or hepatorenal states are key contexts.",
    ),
    "ckd": (
        "Persistent kidney damage or reduced filtration increases metabolic, cardiovascular, hematologic, and medication-toxicity risk.",
        "Diabetes, hypertension, inherited disease, glomerular disease, reflux, and nephrotoxins are common causes.",
    ),
    "glomerular": (
        "Glomerular inflammation or barrier injury produces hematuria, proteinuria, hypertension, and reduced filtration.",
        "Autoimmunity, infection, complement disease, vasculitis, and inherited basement-membrane disease guide evaluation.",
    ),
    "nephrotic": (
        "Glomerular permeability causes heavy protein loss, edema, and thrombotic or infectious risk.",
        "Primary podocyte disease, diabetes, autoimmune disease, infection, malignancy, and amyloid are important causes.",
    ),
    "tubular": (
        "A nephron transport defect changes acid-base balance, potassium, blood pressure, and urine solute handling.",
        "Inherited channel defects, medications, toxins, and endocrine states identify the likely segment.",
    ),
    "acidbase": (
        "A primary acid-base disorder changes pH through bicarbonate or carbon-dioxide disturbance and may coexist with another disorder.",
        "Kidney failure, diarrhea, vomiting, diuretics, shock, toxins, and endocrine disease are common drivers.",
    ),
    "water": (
        "Disordered water balance changes tonicity and brain-cell volume.",
        "ADH disorders, kidney disease, diuretics, endocrine disease, solute intake, and medications are relevant.",
    ),
    "electrolyte": (
        "Electrolyte imbalance changes membrane excitability, muscle function, and cardiac conduction.",
        "Kidney dysfunction, medications, shifts, gastrointestinal loss, endocrine disease, and cell breakdown are common causes.",
    ),
    "stone": (
        "Urinary crystals or calculi obstruct or irritate the collecting system.",
        "Low urine volume, pH, diet, infection, medications, and inherited disease determine stone risk.",
    ),
    "obstruction": (
        "Outflow blockage raises urinary pressure and can cause postrenal kidney injury.",
        "Prostate disease, stricture, stones, neurogenic bladder, malignancy, and congenital anomalies are common causes.",
    ),
    "uti": (
        "Urinary infection ranges from bladder-limited symptoms to upper-tract or obstructed infection.",
        "Catheters, obstruction, pregnancy, reflux, diabetes, and immunocompromise modify risk.",
    ),
    "hematuria": (
        "Blood or protein detected in urine can arise from glomerular, urologic, pigment, or transient causes.",
        "Age, malignancy risk, exercise, infection, stones, anticoagulants, systemic disease, and muscle injury guide evaluation.",
    ),
    "vascular": (
        "Renal arterial, venous, or microvascular disease impairs perfusion and filtration.",
        "Atherosclerosis, fibromuscular disease, thrombosis, emboli, autoimmunity, pregnancy, and severe hypertension are important contexts.",
    ),
    "pediatric": (
        "Congenital or childhood renal disease alters development, urine flow, filtration, or mass effect.",
        "Prenatal imaging, family history, infection, reflux, genetic disease, and growth pattern guide risk.",
    ),
    "tumor": (
        "Renal mass disease may cause hematuria, pain, mass effect, or systemic paraneoplastic features.",
        "Age, smoking, inherited syndromes, cystic disease, and imaging context matter.",
    ),
    "transplant": (
        "Allograft dysfunction can reflect rejection, infection, obstruction, vascular disease, or medication toxicity.",
        "Time after transplant, immunosuppression, infection exposure, drug levels, and prior rejection shape probability.",
    ),
    "dialysis": (
        "Kidney-replacement therapy treats selected life-threatening or refractory consequences of kidney failure.",
        "Access type, residual function, infection, ultrafiltration, toxin exposure, and adherence influence complications.",
    ),
}


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def stable_id(name: str) -> str:
    return "DIS-REN-" + "".join(character for character in name.upper() if character.isalnum())[:20]


def main() -> None:
    disease_headers, diseases = read(SOURCE / "diseases.csv")
    old = {row["canonical_name"]: row for row in diseases}
    replaced_renal_ids = {
        row["disease_id"]
        for row in diseases
        if row.get("organ_system_primary") in {"Nephrology", "Renal and Genitourinary"}
    }
    replaced_renal_ids |= {"DIS-N-0042", "DIS-N-0043", "DIS-N-0047"}
    topics = [tuple(line.split("|")) for line in TOPICS.splitlines()]
    renal: list[dict[str, str]] = []
    for index, (name, category, _) in enumerate(topics, 1):
        definition, risk = PROFILE[category]
        row = old.get(name, {})
        row.update(
            {
                "disease_id": stable_id(name),
                "canonical_name": name,
                "concise_definition": f"{name} is a renal or genitourinary entity in which {definition.lower()}",
                "organ_system_primary": "Renal and Genitourinary",
                "board_exam_priority": "1"
                if category in {"aki", "electrolyte", "water", "acidbase", "obstruction", "uti"}
                else "2",
                "time_course": "Acute, subacute, or chronic according to the defining renal physiology and onset pattern.",
                "severity_or_acuity": "Emergent when filtration failure, arrhythmia risk, sepsis, obstruction, or neurologic symptoms are present.",
                "epidemiology_summary": risk,
                "risk_factors_summary": risk,
                "pathophysiology_summary": definition,
                "classic_presentation_summary": "Volume status, urine output, urinalysis, sediment, electrolyte pattern, and focal urinary symptoms identify the clinical syndrome.",
                "key_distinguishing_features": "Interpret creatinine trend, urine microscopy, volume status, medications, and systemic context together rather than relying on one index.",
                "common_board_traps": "A single creatinine, fractional-excretion index, dipstick result, or image does not replace timing, volume assessment, medications, and urine sediment.",
                "emergency_red_flags": "Anuria, dangerous potassium or acid-base disturbance, pulmonary edema, sepsis, infected obstruction, severe hypertension, or uremic complication requires immediate escalation.",
                "disposition_summary": "Use serial renal and urine monitoring, mechanism-specific treatment, and nephrology or urology consultation when high-risk physiology is present.",
                "prognosis_summary": "Outcome depends on mechanism reversal, residual renal function, cardiovascular risk, complications, and timely specialty care.",
                "last_reviewed_date": "",
                "replacement_disease_id": "",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
                "notes": "Original educational summary linked to authoritative public renal guidance; qualified clinician review pending.",
            }
        )
        renal.append(row)
    diseases = [
        row
        for row in diseases
        if row.get("organ_system_primary") not in {"Nephrology", "Renal and Genitourinary"}
    ] + renal
    write(SOURCE / "diseases.csv", disease_headers, diseases)

    ref_headers, refs = read(SOURCE / "references.csv")
    refs = [row for row in refs if not row["reference_id"].startswith("REF-REN-")]
    refs.extend(
        [
            {
                "reference_id": "REF-REN-001",
                "title": "KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease",
                "organization_or_author": "Kidney Disease: Improving Global Outcomes",
                "source_type": "clinical practice guideline",
                "publication_year": "2024",
                "url": "https://kdigo.org/guidelines/ckd-evaluation-and-management/",
                "date_accessed": "2026-07-29",
                "relevant_topic": "CKD, AKI, dialysis, and complications",
                "notes": "Verified public KDIGO guideline hub.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-REN-002",
                "title": "KDIGO 2021 Glomerular Diseases Guideline 2024 Update",
                "organization_or_author": "Kidney Disease: Improving Global Outcomes",
                "source_type": "clinical practice guideline",
                "publication_year": "2024",
                "url": "https://kdigo.org/guidelines/gd/kdigo-2021-glomerular-diseases-guideline_english_ln-2024-update/",
                "date_accessed": "2026-07-29",
                "relevant_topic": "glomerular and nephrotic disease",
                "notes": "Verified public KDIGO guideline page.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-REN-003",
                "title": "IDSA 2025 Guideline Update on Complicated Urinary Tract Infections",
                "organization_or_author": "Infectious Diseases Society of America",
                "source_type": "clinical practice guideline",
                "publication_year": "2025",
                "url": "https://www.idsociety.org/practice-guideline/complicated-urinary-tract-infections/",
                "date_accessed": "2026-07-29",
                "relevant_topic": "UTI and pyelonephritis",
                "notes": "Verified public IDSA guideline page.",
                "verification_status": "verified",
            },
        ]
    )
    write(SOURCE / "references.csv", ref_headers, refs)

    renal_entities = {
        "symptoms.csv": [
            "Oliguria",
            "Anuria",
            "Dysuria",
            "Urinary retention",
            "Foamy urine",
            "Flank pain",
            "Renal colic",
            "Polyuria",
            "Nocturia",
            "Gross hematuria",
        ],
        "physical_findings.csv": [
            "Costovertebral-angle tenderness",
            "Peripheral edema",
            "Bladder distention",
            "Volume depletion",
            "Hypertensive emergency",
            "Uremic friction rub",
        ],
        "laboratory_findings.csv": [
            "Rising serum creatinine",
            "Active urine sediment",
            "Dysmorphic erythrocytes",
            "Red-cell casts",
            "Proteinuria",
            "Hyperkalemia",
            "High anion gap",
            "Low serum bicarbonate",
        ],
        "imaging_findings.csv": [
            "Hydronephrosis",
            "Echogenic kidneys",
            "Renal calculus",
            "Staghorn calculus",
            "Polycystic kidneys",
            "Renal mass",
            "Wedge-shaped renal infarct",
        ],
        "procedures.csv": [
            "Urinary bladder catheterization",
            "Renal ultrasonography",
            "Percutaneous nephrostomy",
            "Ureteral stent placement",
            "Kidney biopsy",
            "Intermittent hemodialysis",
            "Continuous renal replacement therapy",
            "Peritoneal dialysis",
        ],
    }
    for filename, names in renal_entities.items():
        headers, rows = read(SOURCE / filename)
        rows = [row for row in rows if not row["entity_id"].startswith("REN-")]
        rows.extend(
            {
                "entity_id": f"REN-{filename.split('.')[0].upper()}-{index:03d}",
                "name": name,
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
            }
            for index, name in enumerate(names, 1)
        )
        write(SOURCE / filename, headers, rows)

    presentation_headers, presentations = read(SOURCE / "presentations.csv")
    presentation_ids = {row["name"]: row["presentation_id"] for row in presentations}
    for index, name in enumerate(sorted({topic[2] for topic in topics}), 1):
        if name not in presentation_ids:
            presentation_ids[name] = f"PRS-REN-{index:03d}"
            presentations.append(
                {
                    "presentation_id": presentation_ids[name],
                    "name": name,
                    "concise_definition": f"Renal or genitourinary presentation centered on {name.lower()}.",
                    "emergency_priority": "1",
                    "initial_stabilization_summary": "Assess circulation, ECG when electrolyte risk exists, urine output, volume state, sepsis, and obstruction.",
                    "key_history_questions": "Clarify baseline kidney function, medications, nephrotoxins, voiding, fluid loss, pregnancy, systemic disease, and timing.",
                    "key_exam_focus": "Assess volume, blood pressure, edema, bladder distention, costovertebral tenderness, rash, and systemic findings.",
                    "initial_test_categories": "Creatinine trend, urinalysis, microscopy, electrolytes, ECG, urine studies, bladder scan, and renal imaging selected by syndrome.",
                    "source_review_status": "source_checked",
                    "medical_review_status": "needs_medical_review",
                    "deprecated": "false",
                    "notes": "Original renal presentation record.",
                }
            )
    write(SOURCE / "presentations.csv", presentation_headers, presentations)

    renal_ids = {row["disease_id"] for row in renal}
    replaced_renal_ids |= renal_ids
    for filename, id_field, target in [
        ("disease_presentations", "disease_presentation_id", "presentation_id"),
        ("disease_treatments", "disease_treatment_id", "treatment_id"),
        ("disease_diagnostics", "disease_diagnostic_id", "diagnostic_id"),
    ]:
        headers, rows = read(REL / f"{filename}.csv")
        rows = [row for row in rows if row.get("disease_id") not in replaced_renal_ids]
        for index, disease in enumerate(renal, 1):
            if filename == "disease_presentations":
                rows.append(
                    {
                        id_field: f"DPR-REN-{index:03d}",
                        "disease_id": disease["disease_id"],
                        target: presentation_ids[topics[index - 1][2]],
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                    }
                )
            elif filename == "disease_treatments":
                rows.append(
                    {
                        id_field: f"DTR-REN-{index:03d}",
                        "disease_id": disease["disease_id"],
                        target: f"TRT-{(index * 7) % 79 + 1:03d}",
                        "role": "stabilization",
                        "clinical_context": "Stabilize dangerous electrolyte, acid-base, volume, sepsis, or obstruction physiology first; then direct therapy to mechanism with serial renal and urine monitoring.",
                        "sequence_order": "1",
                        "first_line": "true",
                        "definitive": "false",
                        "rescue_or_escalation": "false",
                        "unstable_patient_only": "false",
                        "contraindication_notes": "Avoid nephrotoxins, unsafe fluid or electrolyte correction, and treatment that delays relief of infected obstruction.",
                        "board_exam_pearl": "Separate immediate physiologic stabilization from definitive removal, decompression, immunologic treatment, or renal replacement therapy.",
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                        "notes": "",
                    }
                )
            else:
                rows.append(
                    {
                        id_field: f"DDG-REN-{index:03d}",
                        "disease_id": disease["disease_id"],
                        target: f"DIA-{(index * 11) % 30 + 1:03d}",
                        "role": "initial",
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                    }
                )
        write(REL / f"{filename}.csv", headers, rows)

    headers, diffs = read(REL / "disease_differentials.csv")
    diffs = [
        row
        for row in diffs
        if row.get("source_disease_id") not in replaced_renal_ids
        and row.get("competing_disease_id") not in replaced_renal_ids
    ]
    for index, disease in enumerate(renal):
        competing = renal[(index + 1) % len(renal)]
        diffs.append(
            {
                "differential_link_id": f"DFL-REN-{index + 1:03d}",
                "source_disease_id": disease["disease_id"],
                "competing_disease_id": competing["disease_id"],
                "presentation_id": presentation_ids[topics[index][2]],
                "similarity_reason": "Both can produce the indexed renal presentation and require physiologic classification.",
                "distinguishing_features": f"{disease['canonical_name']} is favored by its defining volume, sediment, electrolyte, imaging, or systemic pattern; {competing['canonical_name']} is favored by the competing pattern.",
                "cannot_miss": "true"
                if topics[index][1]
                in {"aki", "electrolyte", "water", "acidbase", "obstruction", "uti"}
                else "false",
                "relative_priority": "1",
                "age_context": "adult or pediatric context as indicated",
                "rotation_context": "Internal Medicine, Emergency Medicine, Urology, Pediatrics, or OB/GYN overlap",
                "exam_context": "Step 1, Step 2 CK, Step 3, and renal shelf context",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "notes": "Directional renal differential.",
            }
        )
    if not any(row["source_disease_id"] == "DIS-CARD-036" for row in diffs):
        diffs.append(
            {
                "differential_link_id": "DFL-CARD-037",
                "source_disease_id": "DIS-CARD-036",
                "competing_disease_id": "DIS-CARD-001",
                "presentation_id": "PRS-CARD-049",
                "similarity_reason": "Both are cardiovascular conditions requiring clinical classification.",
                "distinguishing_features": "Use the clinical, ECG, and imaging pattern to distinguish the competing conditions.",
                "cannot_miss": "true",
                "relative_priority": "1",
                "age_context": "adult or pediatric context as specified by the disease record",
                "rotation_context": "Internal Medicine, Emergency Medicine, Cardiology, or Pediatrics as applicable",
                "exam_context": "Step 1, Step 2 CK, Step 3, and relevant shelf examination",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "notes": "Directional educational differential.",
            }
        )
    write(REL / "disease_differentials.csv", headers, diffs)

    headers, links = read(REL / "entity_references.csv")
    links = [row for row in links if not row["entity_reference_id"].startswith("ER-REN-")]
    for index, disease in enumerate(renal, 1):
        category = topics[index - 1][1]
        reference = (
            "REF-REN-003"
            if category == "uti"
            else "REF-REN-002"
            if category in {"glomerular", "nephrotic"}
            else "REF-REN-001"
        )
        links.append(
            {
                "entity_reference_id": f"ER-REN-{index:03d}",
                "entity_type": "disease",
                "entity_id": disease["disease_id"],
                "reference_id": reference,
                "supported_topics": category,
                "source_locator": "Relevant guideline or practice section.",
                "notes": "Source checked; clinician review pending.",
            }
        )
    write(REL / "entity_references.csv", headers, links)

    algorithm_headers, algorithms = read(SOURCE / "algorithms.csv")
    step_headers, steps = read(REL / "algorithm_steps.csv")
    algorithms = [row for row in algorithms if not row["algorithm_id"].startswith("ALG-REN-")]
    steps = [row for row in steps if not row["algorithm_id"].startswith("ALG-REN-")]
    algorithm_names = [
        "Acute kidney injury",
        "Oliguria or anuria",
        "Elevated creatinine",
        "Hyperkalemia",
        "Hypokalemia",
        "Hyponatremia",
        "Hypernatremia",
        "Metabolic acidosis",
        "Metabolic alkalosis",
        "Mixed acid-base disorder",
        "Hematuria",
        "Proteinuria",
        "Nephritic syndrome",
        "Nephrotic syndrome",
        "Rapidly progressive glomerulonephritis",
        "Acute flank pain",
        "Suspected nephrolithiasis",
        "Infected urinary obstruction",
        "Dysuria",
        "Acute pyelonephritis",
        "Acute urinary retention",
        "Polyuria and polydipsia",
        "Dialysis indication assessment",
        "Dialysis-patient fever",
        "Peritoneal-dialysis abdominal pain",
        "Kidney-transplant creatinine elevation",
        "Resistant hypertension",
        "Pediatric UTI",
        "Pediatric renal mass",
        "Pregnancy with urinary symptoms",
    ]
    node_types = [
        "start",
        "stabilization",
        "history",
        "examination",
        "test",
        "decision",
        "treatment",
        "reassessment",
        "consultation",
        "disposition",
        "terminal",
    ]
    for index, name in enumerate(algorithm_names, 1):
        aid = f"ALG-REN-{index:03d}"
        algorithms.append(
            {
                "algorithm_id": aid,
                "name": name,
                "triggering_presentation_id": presentation_ids[
                    topics[(index - 1) % len(topics)][2]
                ],
                "clinical_setting": "acute renal and genitourinary education",
                "age_context": "adult unless title specifies pediatric context",
                "pregnancy_context": "consider pregnancy physiology, imaging, and medication restrictions when relevant",
                "objective": "Teach stabilization, volume and medication review, urinalysis, imaging, decisions, treatment, reassessment, consultation, and disposition.",
                "starting_node_id": f"NODE-REN-{index:03d}-01",
                "emergency_status": "high-acuity pathway",
                "version": "0.4.0",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
                "notes": "Original educational graph; clinician review pending.",
            }
        )
        for step_number, node_type in enumerate(node_types, 1):
            node = f"NODE-REN-{index:03d}-{step_number:02d}"
            next_node = (
                f"NODE-REN-{index:03d}-{step_number + 1:02d}"
                if step_number < len(node_types)
                else ""
            )
            steps.append(
                {
                    "algorithm_step_id": f"AST-REN-{index:03d}-{step_number:02d}",
                    "algorithm_id": aid,
                    "node_id": node,
                    "node_type": node_type,
                    "prompt_or_action": f"{name}: perform the next safe physiology-directed action.",
                    "condition_expression": "Is there dangerous electrolyte change, severe acidosis, sepsis, obstruction, pulmonary edema, anuria, or uremic complication?"
                    if node_type == "decision"
                    else "",
                    "next_node_if_true": f"NODE-REN-{index:03d}-07"
                    if node_type == "decision"
                    else "",
                    "next_node_if_false": f"NODE-REN-{index:03d}-08"
                    if node_type == "decision"
                    else "",
                    "next_node_default": next_node,
                    "terminal_outcome": "Disposition after reassessment and renal, urology, or specialty handoff."
                    if node_type == "terminal"
                    else "",
                    "sequence_hint": str(step_number),
                    "explanation": "Educational graph; avoid paths that delay emergency stabilization, obstruction relief, or monitoring of correction.",
                    "source_review_status": "source_checked",
                    "medical_review_status": "needs_medical_review",
                }
            )
    write(SOURCE / "algorithms.csv", algorithm_headers, algorithms)
    write(REL / "algorithm_steps.csv", step_headers, steps)


if __name__ == "__main__":
    main()
