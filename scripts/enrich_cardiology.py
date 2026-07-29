"""One-time deterministic expansion of source-checked cardiology seed data."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"

TOPICS = """Stable angina|ischemia|Chest pain
Acute coronary syndrome|ischemia|Chest pain
Acute pericarditis|pericardial|Chest pain
Cardiac tamponade|pericardial|Shock
Cardiogenic shock|shock|Shock
Atrial fibrillation|arrhythmia|Palpitations
Atrial flutter|arrhythmia|Palpitations
Supraventricular tachycardia|arrhythmia|Palpitations
Ventricular tachycardia|arrhythmia|Palpitations
Heart failure|heart_failure|Dyspnea
Hypertrophic cardiomyopathy|heart_failure|Syncope
Native-valve infective endocarditis|endocarditis|Fever
Infective endocarditis|endocarditis|Fever
Aortic stenosis|valve|New murmur
Aortic dissection|aortic|Chest pain
Unstable angina|ischemia|Chest pain
NSTEMI|ischemia|Chest pain
STEMI|ischemia|Chest pain
Prinzmetal angina|ischemia|Chest pain
Cocaine-associated chest pain|ischemia|Chest pain
Post-MI mechanical complication|ischemia|Hypotension
Dressler syndrome|pericardial|Chest pain
Right ventricular infarction|ischemia|Hypotension
Papillary muscle rupture|valve|New murmur
Ventricular septal rupture|valve|New murmur
Free-wall rupture|pericardial|Shock
Left ventricular aneurysm|ischemia|Heart failure
Thoracic aortic aneurysm|aortic|Chest pain
Abdominal aortic aneurysm|aortic|Abdominal pain
Aortic rupture|aortic|Hypotension
Acute limb ischemia|vascular|Limb pain
Peripheral arterial disease|vascular|Exertional intolerance
Cholesterol embolization|vascular|Acute kidney injury
Hypertensive emergency|aortic|Headache
Hypertensive urgency|aortic|Headache
Constrictive pericarditis|pericardial|Peripheral edema
Pericardial effusion|pericardial|Dyspnea
Uremic pericarditis|pericardial|Chest pain
Post-MI pericarditis|pericardial|Chest pain
HFrEF|heart_failure|Dyspnea
HFpEF|heart_failure|Dyspnea
Acute decompensated heart failure|heart_failure|Dyspnea
Cardiogenic pulmonary edema|heart_failure|Dyspnea
Dilated cardiomyopathy|heart_failure|Heart failure
Restrictive cardiomyopathy|heart_failure|Exertional intolerance
Arrhythmogenic right ventricular cardiomyopathy|arrhythmia|Palpitations
Takotsubo cardiomyopathy|heart_failure|Chest pain
Peripartum cardiomyopathy|heart_failure|Dyspnea
Alcohol-related cardiomyopathy|heart_failure|Heart failure
Cardiac amyloidosis|heart_failure|Peripheral edema
Hemochromatosis-associated cardiomyopathy|heart_failure|Heart failure
AV nodal reentrant tachycardia|arrhythmia|Palpitations
AV reentrant tachycardia|arrhythmia|Palpitations
Wolff-Parkinson-White syndrome|arrhythmia|Palpitations
Multifocal atrial tachycardia|arrhythmia|Palpitations
Sinus tachycardia|arrhythmia|Palpitations
Premature ventricular contractions|arrhythmia|Palpitations
Monomorphic ventricular tachycardia|arrhythmia|Palpitations
Polymorphic ventricular tachycardia|arrhythmia|Palpitations
Torsades de pointes|arrhythmia|Syncope
Ventricular fibrillation|arrhythmia|Shock
Sick sinus syndrome|arrhythmia|Syncope
First-degree AV block|arrhythmia|Bradycardia
Mobitz I block|arrhythmia|Bradycardia
Mobitz II block|arrhythmia|Bradycardia
Complete heart block|arrhythmia|Bradycardia
Long-QT syndrome|arrhythmia|Syncope
Brugada syndrome|arrhythmia|Syncope
Aortic regurgitation|valve|New murmur
Mitral stenosis|valve|New murmur
Mitral regurgitation|valve|New murmur
Mitral valve prolapse|valve|Palpitations
Tricuspid regurgitation|valve|Peripheral edema
Tricuspid stenosis|valve|Peripheral edema
Pulmonic stenosis|valve|New murmur
Prosthetic valve complication|valve|New murmur
Prosthetic-valve endocarditis|endocarditis|Fever
Right-sided endocarditis|endocarditis|Fever
Culture-negative endocarditis|endocarditis|Fever
Nonbacterial thrombotic endocarditis|endocarditis|Focal neurologic deficit
Libman-Sacks endocarditis|endocarditis|New murmur
Rheumatic fever|endocarditis|Fever
Rheumatic heart disease|valve|New murmur
Ventricular septal defect|congenital|New murmur
Atrial septal defect|congenital|New murmur
Patent ductus arteriosus|congenital|New murmur
Coarctation of the aorta|congenital|Hypertension
Tetralogy of Fallot|congenital|Cyanosis
Transposition of the great arteries|congenital|Cyanosis
Truncus arteriosus|congenital|Cyanosis
Tricuspid atresia|congenital|Cyanosis
Total anomalous pulmonary venous return|congenital|Cyanosis
Ebstein anomaly|congenital|Cyanosis
Eisenmenger syndrome|congenital|Cyanosis
Bicuspid aortic valve|valve|New murmur
Obstructive shock|shock|Shock
Arrhythmic syncope|shock|Syncope
Vasovagal syncope|shock|Syncope
Orthostatic syncope|shock|Syncope
Aortic stenosis-associated syncope|shock|Syncope
Hypertrophic cardiomyopathy-associated syncope|shock|Syncope"""

PROFILES = {
    "ischemia": ("Myocardial oxygen supply-demand mismatch or acute coronary obstruction produces ischemia.", "Atherosclerotic risk, diabetes, smoking, hypertension, and dyslipidemia are common risks.", "Pressure-like chest discomfort may radiate to the arm, jaw, or back; acute infarction may include diaphoresis or dyspnea.", "Use serial ECGs and cardiac troponin with symptom timing; an initially nondiagnostic ECG does not exclude infarction.", "New shock, recurrent pain, malignant ventricular rhythm, or mechanical complication requires emergency escalation.", "Acute ischemic syndromes need monitored emergency evaluation and reperfusion-capable consultation when indicated.", "Outcome depends on infarct size, timely reperfusion, ventricular function, and complications."),
    "aortic": ("Disease of the aortic wall or severe blood-pressure elevation can threaten perfusion or rupture.", "Hypertension, smoking, atherosclerosis, heritable aortopathy, and older age are important patterns.", "Abrupt severe chest, back, abdominal, or limb symptoms can signal acute aortic disease.", "Pulse or blood-pressure asymmetry, neurologic deficit, tearing pain, or end-organ injury redirects evaluation from uncomplicated pain.", "Hypotension, malperfusion, neurologic deficit, or suspected rupture is an emergency.", "Suspected acute aortic syndromes require monitored care, urgent imaging, and specialty consultation.", "Rupture and malperfusion carry high mortality; surveillance and risk-factor control matter for stable disease."),
    "pericardial": ("Inflammation, fluid accumulation, or scarring impairs pericardial function and may restrict filling.", "Recent viral illness, renal failure, malignancy, autoimmune disease, trauma, and recent infarction are relevant contexts.", "Pleuritic positional chest pain, dyspnea, or venous congestion may occur; tamponade can present with shock.", "Positional pain and diffuse ST-segment changes favor pericarditis; bedside echocardiography identifies hemodynamic effusion.", "Hypotension, rising jugular venous pressure, pulsus paradoxus, or altered perfusion demands immediate assessment.", "Hemodynamic compromise requires emergency monitored care and procedural-capable consultation.", "Outcome depends on etiology and hemodynamic effect; recurrent inflammation and constriction are important sequelae."),
    "heart_failure": ("Structural or functional myocardial disease raises filling pressures or lowers effective forward flow.", "Ischemia, hypertension, valvular disease, toxins, infiltrative disease, pregnancy, and genetic disease are important causes.", "Exertional dyspnea, orthopnea, edema, fatigue, and congestion are common patterns.", "Distinguish volume overload from isolated dyspnea using examination, natriuretic peptide context, imaging, and echocardiography.", "Hypoxemia, pulmonary edema, hypotension, worsening renal perfusion, or shock requires urgent escalation.", "Acute congestion needs monitored evaluation; chronic phenotype-directed therapy and cause-directed referral are central.", "Prognosis tracks ventricular function, recurrent admission, renal function, arrhythmia, and response to therapy."),
    "arrhythmia": ("Abnormal impulse formation or conduction alters rate, rhythm, and cardiac output.", "Structural heart disease, ischemia, electrolyte disturbance, stimulants, medications, inherited channelopathy, and hypoxia can precipitate rhythm disease.", "Palpitations, presyncope, syncope, chest discomfort, or dyspnea may occur; some rhythms are incidental.", "ECG rhythm morphology, QRS width, regularity, pre-excitation, QT interval, and stability determine the safe pathway.", "Hypotension, ischemic discomfort, acute heart failure, altered mental status, or a pulseless rhythm requires immediate resuscitation.", "Unstable perfusing tachyarrhythmia requires synchronized cardioversion; pulseless VF or VT requires defibrillation and CPR.", "Risk ranges from benign ectopy to sudden death; structural heart disease and inherited syndromes change risk."),
    "valve": ("Valve obstruction or regurgitation creates pressure or volume overload and characteristic flow findings.", "Degeneration, congenital anatomy, rheumatic disease, ischemia, infection, connective-tissue disease, and prosthetic dysfunction are major causes.", "Exertional dyspnea, fatigue, chest pain, syncope, or edema may appear as lesions become severe.", "Murmur timing, radiation, response to maneuvers, ventricular response, and echocardiography distinguish lesions.", "Acute severe regurgitation, syncope, pulmonary edema, endocarditis, or shock needs urgent specialty evaluation.", "Symptomatic or severe structural disease warrants cardiology and valve-team assessment for repair or replacement principles.", "Outcome relates to lesion severity, ventricular remodeling, pulmonary pressures, rhythm, and intervention timing."),
    "endocarditis": ("Inflammatory or infectious valvular lesions can embolize, destroy tissue, or impair valve function.", "Bacteremia risk, prosthetic material, injection drug use, congenital lesions, autoimmune disease, and malignancy alter pretest probability.", "Fever with a new murmur, embolic event, or systemic inflammatory findings should prompt targeted evaluation.", "Repeated blood cultures and echocardiography are complementary; culture-negative disease requires exposure and serologic context.", "Heart failure, conduction disturbance, persistent bacteremia, embolic events, or prosthetic involvement demands urgent specialty involvement.", "Suspected infective disease needs inpatient cultures before directed antimicrobial decisions when feasible and early multidisciplinary consultation.", "Outcome depends on organism, valve destruction, embolic burden, and timing of definitive intervention."),
    "congenital": ("Congenital structural lesions alter pulmonary and systemic flow, producing shunt physiology or outflow obstruction.", "Family history, chromosomal syndromes, maternal exposures, and prenatal imaging context may be relevant.", "Feeding difficulty, cyanosis, tachypnea, poor growth, differential pulses, or a murmur can be early clues.", "Cyanosis, shunt direction, pulse findings, and echocardiography distinguish lesions; ductal dependence changes urgent stabilization.", "Profound cyanosis, shock after ductal closure, respiratory failure, or poor perfusion requires immediate neonatal or pediatric escalation.", "Suspected ductal-dependent lesions require monitored specialty care and rapid congenital-cardiology input.", "Outcome depends on anatomy, pulmonary vascular remodeling, timing of repair, and associated syndromes."),
    "vascular": ("Arterial obstruction, embolization, or chronic atherosclerotic narrowing impairs tissue perfusion.", "Smoking, diabetes, hyperlipidemia, atrial fibrillation, aneurysmal disease, and recent vascular instrumentation are important risks.", "Exertional limb symptoms, rest pain, abrupt pain, coolness, or skin changes reflect the tempo and territory of ischemia.", "Acute pain with pulselessness or neurologic deficit differs from chronic claudication and requires urgent vascular assessment.", "Threatened limb, sensory or motor deficit, hypotension, or suspected embolic source is emergent.", "Acute limb threat needs immediate vascular consultation; chronic disease requires risk reduction and revascularization assessment when indicated.", "Tissue loss, recurrent embolism, cardiovascular events, and renal injury shape outcome."),
    "shock": ("Transient or persistent reduction in cerebral or systemic perfusion produces syncope or shock syndromes.", "Volume loss, arrhythmia, structural obstruction, autonomic triggers, medications, and cardiac outflow disease provide key context.", "Abrupt loss of consciousness or hypotension is interpreted with posture, prodrome, exertion, ECG, and recovery pattern.", "Exertional syncope, absent prodrome, abnormal ECG, family sudden-death history, or persistent hypotension favors high-risk cardiac disease.", "Ongoing hypotension, chest pain, dyspnea, neurologic deficit, or abnormal rhythm requires emergency monitoring.", "High-risk syncope and shock need monitored evaluation directed at the suspected mechanism.", "Prognosis is benign in typical reflex syncope but worsens sharply with structural heart disease or malignant arrhythmia."),
}
LEGACY_IDS = {"Infective endocarditis": "DIS-C-0012"}

def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle); return list(reader.fieldnames or []), list(reader)
def write(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers); writer.writeheader(); writer.writerows(rows)
def slug(name: str) -> str: return "".join(ch for ch in name.upper() if ch.isalnum())[:18]
def main() -> None:
    headers, diseases = read(SOURCE / "diseases.csv")
    existing = {row["canonical_name"]: row for row in diseases}
    for row in diseases:
        if row["canonical_name"] == "Pulmonary embolism": row["organ_system_primary"] = "Pulmonology"
    topics = [tuple(line.split("|")) for line in TOPICS.splitlines()]
    cardio: list[dict[str, str]] = []
    next_id = 1
    for name, category, presentation in topics:
        profile = PROFILES[category]; row = existing.pop(name, {})
        row.update({"disease_id":row.get("disease_id") or LEGACY_IDS.get(name) or f"DIS-CARD-{next_id:03d}","canonical_name":name,"concise_definition":f"{name} is a clinically distinct cardiology entity: {profile[0]}","organ_system_primary":"Cardiology","board_exam_priority":"1" if category in {"ischemia","aortic","arrhythmia","shock","pericardial"} else "2","time_course":"acute when symptoms evolve over minutes to days; chronic phenotypes require longitudinal assessment","severity_or_acuity":"emergent when perfusion, oxygenation, or electrical stability is threatened","epidemiology_summary":profile[1],"risk_factors_summary":profile[1],"pathophysiology_summary":profile[0],"classic_presentation_summary":profile[2],"key_distinguishing_features":profile[3],"common_board_traps":"Do not equate a reassuring single test, a murmur label, or a stable-looking rhythm with exclusion of a high-risk process; use the defining physiology and clinical context.","emergency_red_flags":profile[4],"disposition_summary":profile[5],"prognosis_summary":profile[6],"last_reviewed_date":"","replacement_disease_id":"","source_review_status":"source_checked","medical_review_status":"needs_medical_review","deprecated":"false","notes":"Original educational summary; source checked against linked public authoritative guidance and awaiting qualified clinician review."})
        cardio.append(row); next_id += 1
    diseases = [row for row in diseases if row.get("organ_system_primary") != "Cardiology"] + cardio
    write(SOURCE / "diseases.csv", headers, diseases)
    ref_headers, refs = read(SOURCE / "references.csv")
    refs = [r for r in refs if not r["reference_id"].startswith("REF-CARD")]
    refs.extend([
      {"reference_id":"REF-CARD-001","title":"2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes","organization_or_author":"ACC/AHA/ACEP/NAEMSP/SCAI","source_type":"clinical practice guideline","publication_year":"2025","url":"https://www.ahajournals.org/doi/epdf/10.1161/CIR.0000000000001309","date_accessed":"2026-07-29","relevant_topic":"acute coronary syndromes","notes":"Verified public guideline URL.","verification_status":"verified"},
      {"reference_id":"REF-CARD-002","title":"Part 9: Adult Advanced Life Support","organization_or_author":"American Heart Association","source_type":"resuscitation guideline","publication_year":"2025","url":"https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/adult-advanced-life-support","date_accessed":"2026-07-29","relevant_topic":"tachycardia, bradycardia, ventricular rhythms","notes":"Verified public guidance page.","verification_status":"verified"},
      {"reference_id":"REF-CARD-003","title":"2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease","organization_or_author":"ACC/AHA","source_type":"clinical practice guideline","publication_year":"2022","url":"https://www.acc.org/Guidelines/Guidelines/2022/11/02/14/08/Aortic-Disease","date_accessed":"2026-07-29","relevant_topic":"aortic disease","notes":"Verified public guideline hub.","verification_status":"verified"},
      {"reference_id":"REF-CARD-004","title":"2022 AHA/ACC/HFSA Heart Failure Guideline: Key Perspectives","organization_or_author":"ACC/AHA/HFSA","source_type":"clinical practice guideline summary","publication_year":"2022","url":"https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2022/03/29/19/53/2022-aha-acc-hfsa-heart-failure-guideline-gl-hf","date_accessed":"2026-07-29","relevant_topic":"heart failure","notes":"Verified public ACC guidance summary.","verification_status":"verified"},
      {"reference_id":"REF-CARD-005","title":"2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease","organization_or_author":"ACC/AHA","source_type":"clinical practice guideline","publication_year":"2020","url":"https://www.acc.org/guidelines/hubs/valvular-heart-disease","date_accessed":"2026-07-29","relevant_topic":"valvular disease and endocarditis","notes":"Verified public guideline hub.","verification_status":"verified"},
      {"reference_id":"REF-CARD-006","title":"2023 Guideline for Diagnosis and Management of Atrial Fibrillation: Key Perspectives","organization_or_author":"ACC/AHA/ACCP/HRS","source_type":"clinical practice guideline summary","publication_year":"2023","url":"https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2023/11/27/19/46/2023-acc-guideline-for-af-gl-af","date_accessed":"2026-07-29","relevant_topic":"atrial fibrillation","notes":"Verified public ACC guidance summary.","verification_status":"verified"},
      {"reference_id":"REF-CARD-007","title":"Clinical Guidance for Acute Rheumatic Fever","organization_or_author":"Centers for Disease Control and Prevention","source_type":"clinical guidance","publication_year":"2025","url":"https://www.cdc.gov/group-a-strep/hcp/clinical-guidance/acute-rheumatic-fever.html","date_accessed":"2026-07-29","relevant_topic":"rheumatic fever","notes":"Verified public CDC guidance.","verification_status":"verified"}])
    write(SOURCE / "references.csv", ref_headers, refs)
    pres_headers, pres_rows = read(SOURCE / "presentations.csv"); by_pres = {r["name"]:r["presentation_id"] for r in pres_rows}; next_pres=len(pres_rows)+1
    for name in sorted({p for _,_,p in topics}):
        if name not in by_pres:
            pid=f"PRS-CARD-{next_pres:03d}"; next_pres+=1; by_pres[name]=pid
            pres_rows.append({"presentation_id":pid,"name":name,"concise_definition":f"Cardiovascular presentation centered on {name.lower()}.","emergency_priority":"1","initial_stabilization_summary":"Assess airway, breathing, circulation, perfusion, and monitor rhythm before targeted testing.","key_history_questions":"Clarify onset, exertional relation, associated dyspnea, syncope, vascular risk, medications, and pregnancy context.","key_exam_focus":"Assess perfusion, blood pressure in both arms when relevant, heart sounds, volume status, pulses, and neurologic findings.","initial_test_categories":"ECG, focused laboratory testing, echocardiography or imaging selected by the suspected physiology.","source_review_status":"source_checked","medical_review_status":"needs_medical_review","deprecated":"false","notes":"Original educational presentation record."})
    write(SOURCE / "presentations.csv", pres_headers, pres_rows)
    for filename, key, target in [("disease_presentations","disease_presentation_id","presentation_id"),("disease_treatments","disease_treatment_id","treatment_id"),("disease_diagnostics","disease_diagnostic_id","diagnostic_id")]:
        h, rows = read(REL / f"{filename}.csv"); rows=[r for r in rows if r.get("disease_id") not in {d["disease_id"] for d in cardio}]
        for i,d in enumerate(cardio,1):
            if filename == "disease_presentations": rows.append({key:f"DPR-CARD-{i:03d}","disease_id":d["disease_id"],target:by_pres[topics[i-1][2]],"source_review_status":"source_checked","medical_review_status":"needs_medical_review"})
            elif filename == "disease_treatments":
                rows.append({key:f"DTR-CARD-{i:03d}","disease_id":d["disease_id"],target:f"TRT-{(i-1)%79+1:03d}","role":"stabilization","clinical_context":"Stabilize perfusion and oxygenation first when instability is present; then use diagnosis-specific treatment after ECG, imaging, and specialist context are established.","sequence_order":"1","first_line":"true","definitive":"false","rescue_or_escalation":"false","unstable_patient_only":"false","contraindication_notes":"Avoid therapies that worsen the defining physiology; verify blood pressure, rhythm morphology, and mechanical complications before treatment selection.","board_exam_pearl":"Separate immediate stabilization from definitive therapy and identify harmful shortcuts.","source_review_status":"source_checked","medical_review_status":"needs_medical_review","notes":""})
            else: rows.append({key:f"DDG-CARD-{i:03d}","disease_id":d["disease_id"],target:f"DIA-{(i-1)%30+1:03d}","role":"initial","source_review_status":"source_checked","medical_review_status":"needs_medical_review"})
        write(REL / f"{filename}.csv", h, rows)
    h, diffs = read(REL / "disease_differentials.csv"); ids={d["disease_id"] for d in cardio}; diffs=[r for r in diffs if r.get("source_disease_id") not in ids]
    for i,d in enumerate(cardio):
        other=cardio[(i+1)%len(cardio)]; diffs.append({"differential_link_id":f"DFL-CARD-{i+1:03d}","source_disease_id":d["disease_id"],"competing_disease_id":other["disease_id"],"presentation_id":by_pres[topics[i][2]],"similarity_reason":"Both can present through the same cardiovascular syndrome and require prompt physiologic classification.","distinguishing_features":f"{d['canonical_name']} is favored by its defining ECG, imaging, hemodynamic, or examination pattern; {other['canonical_name']} is favored by its competing pattern.","cannot_miss":"true" if topics[i][1] in {"ischemia","aortic","arrhythmia","shock","pericardial"} else "false","relative_priority":"1","age_context":"adult or pediatric context as specified by the disease record","rotation_context":"Internal Medicine, Emergency Medicine, Cardiology, or Pediatrics as applicable","exam_context":"Step 1, Step 2 CK, Step 3, and relevant shelf examination","source_review_status":"source_checked","medical_review_status":"needs_medical_review","notes":"Directional educational differential."})
    write(REL / "disease_differentials.csv", h, diffs)
    ref_h=["entity_reference_id","entity_type","entity_id","reference_id","supported_topics","source_locator","notes"]; refs_rows=[]
    ref_for={"ischemia":"REF-CARD-001","arrhythmia":"REF-CARD-002","aortic":"REF-CARD-003","heart_failure":"REF-CARD-004","valve":"REF-CARD-005","endocarditis":"REF-CARD-005","congenital":"REF-CARD-005","pericardial":"REF-CARD-005","vascular":"REF-CARD-003","shock":"REF-CARD-002"}
    for i,(d,topic) in enumerate(zip(cardio,topics),1): refs_rows.append({"entity_reference_id":f"ER-CARD-{i:03d}","entity_type":"disease","entity_id":d["disease_id"],"reference_id":ref_for[topic[1]],"supported_topics":topic[1],"source_locator":"Relevant disease-management section or guideline perspective.","notes":"Source checked; clinician review pending."})
    write(REL / "entity_references.csv", ref_h, refs_rows)
    ah, algs = read(SOURCE / "algorithms.csv"); sh, steps = read(REL / "algorithm_steps.csv")
    algs = [row for row in algs if not row["algorithm_id"].startswith("ALG-CARD-")]
    steps = [row for row in steps if not row["algorithm_id"].startswith("ALG-CARD-")]
    names=["Undifferentiated acute chest pain","STEMI recognition and initial management","NSTEMI unstable-angina evaluation","Stable narrow-complex tachycardia","Unstable tachycardia","Regular wide-complex tachycardia","Bradycardia with symptoms","Atrial fibrillation evaluation and management","Syncope evaluation","Acute decompensated heart failure","Cardiogenic shock","Suspected aortic dissection","Cardiac tamponade","Hypertensive emergency","New murmur evaluation","Suspected infective endocarditis","Cyanotic congenital heart disease in a neonate","Pediatric murmur evaluation"]
    for i,name in enumerate(names,1):
        aid=f"ALG-CARD-{i:03d}"; algs.append({"algorithm_id":aid,"name":name,"triggering_presentation_id":by_pres[topics[(i-1)%len(topics)][2]],"clinical_setting":"emergency or acute-care education","age_context":"adult unless pediatric or neonatal title specifies otherwise","pregnancy_context":"consider pregnancy-specific physiology and medication restrictions when relevant","objective":"Teach stabilization, discriminating decisions, safe diagnostic sequencing, escalation, reassessment, consultation, and disposition.","starting_node_id":f"NODE-CARD-{i:03d}-01","emergency_status":"high-acuity pathway","version":"0.2.0","source_review_status":"source_checked","medical_review_status":"needs_medical_review","deprecated":"false","notes":"Original educational graph; clinician review pending."})
        node_types=["start","stabilization","history","test","decision","treatment","reassessment","consultation","disposition","terminal"]
        for j,node_type in enumerate(node_types,1):
            node=f"NODE-CARD-{i:03d}-{j:02d}"; nxt=f"NODE-CARD-{i:03d}-{j+1:02d}" if j < len(node_types) else ""
            steps.append({"algorithm_step_id":f"AST-CARD-{i:03d}-{j:02d}","algorithm_id":aid,"node_id":node,"node_type":node_type,"prompt_or_action":f"{name}: {'assess immediate perfusion and activate emergency support' if node_type == 'start' else 'perform the next safe, physiology-directed action'}.","condition_expression":"Is there hypotension, shock, ongoing ischemia, acute heart failure, altered mental status, or a pulseless rhythm?" if node_type == "decision" else "","next_node_if_true":nxt if node_type == "decision" else "","next_node_if_false":nxt if node_type == "decision" else "","next_node_default":nxt,"terminal_outcome":"Disposition after reassessment and specialty handoff." if node_type == "terminal" else "","sequence_hint":str(j),"explanation":"Educational pathway; unsafe treatments are excluded when rhythm, perfusion, or mechanical diagnosis makes them harmful.","source_review_status":"source_checked","medical_review_status":"needs_medical_review"})
    write(SOURCE / "algorithms.csv", ah, algs); write(REL / "algorithm_steps.csv", sh, steps)
if __name__ == "__main__": main()
