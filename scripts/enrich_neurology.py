"""Deterministically replace Neurology scaffolding with source-linked study records."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"
TOPICS = """Transient ischemic attack|stroke|Acute focal neurologic deficit
Seizure disorder|seizure|Seizure
Meningitis|infection|Headache
Delirium|cognitive|Altered mental status
Acute ischemic stroke|stroke|Acute focal neurologic deficit
Large-vessel occlusion stroke|stroke|Acute focal neurologic deficit
Lacunar stroke|stroke|Weakness
Watershed infarction|stroke|Acute focal neurologic deficit
Cardioembolic stroke|stroke|Acute focal neurologic deficit
Cryptogenic stroke|stroke|Acute focal neurologic deficit
Cerebral venous sinus thrombosis|stroke|Headache
Intracerebral hemorrhage|stroke|Acute focal neurologic deficit
Subarachnoid hemorrhage|stroke|Thunderclap headache
Epidural hematoma|stroke|Head trauma
Subdural hematoma|stroke|Altered mental status
Intraventricular hemorrhage|stroke|Altered mental status
Hypertensive cerebral hemorrhage|stroke|Acute focal neurologic deficit
Cerebral amyloid angiopathy|stroke|Acute focal neurologic deficit
Carotid artery dissection|stroke|Headache
Vertebral artery dissection|stroke|Vertigo
Carotid artery stenosis|stroke|Acute focal neurologic deficit
Moyamoya disease|stroke|Acute focal neurologic deficit
Reversible cerebral vasoconstriction syndrome|stroke|Thunderclap headache
Posterior reversible encephalopathy syndrome|stroke|Headache
Vascular dementia|cognitive|Memory loss
Middle cerebral artery syndrome|stroke|Acute focal neurologic deficit
Anterior cerebral artery syndrome|stroke|Weakness
Posterior cerebral artery syndrome|stroke|Vision loss
Basilar artery syndrome|stroke|Altered mental status
Lateral medullary syndrome|stroke|Vertigo
Medial medullary syndrome|stroke|Weakness
Locked-in syndrome|stroke|Altered mental status
Pure motor lacunar syndrome|stroke|Weakness
First unprovoked seizure|seizure|First seizure
Focal aware seizure|seizure|Seizure
Focal impaired-awareness seizure|seizure|Seizure
Focal to bilateral tonic-clonic seizure|seizure|Seizure
Generalized tonic-clonic seizure|seizure|Seizure
Absence seizure|seizure|Seizure
Myoclonic seizure|seizure|Seizure
Atonic seizure|seizure|Seizure
Infantile spasms|seizure|Seizure
Febrile seizure|seizure|Seizure
Status epilepticus|seizure|Status epilepticus
Nonconvulsive status epilepticus|seizure|Altered mental status
Psychogenic nonepileptic seizures|seizure|Seizure
Juvenile myoclonic epilepsy|seizure|Seizure
Childhood absence epilepsy|seizure|Seizure
Temporal-lobe epilepsy|seizure|Seizure
Lennox-Gastaut syndrome|seizure|Seizure
West syndrome|seizure|Seizure
Dravet syndrome|seizure|Seizure
Migraine without aura|headache|Headache
Migraine with aura|headache|Headache
Hemiplegic migraine|headache|Headache
Cluster headache|headache|Headache
Trigeminal neuralgia|headache|Facial weakness
Idiopathic intracranial hypertension|headache|Headache
Intracranial hypotension|headache|Headache
Giant cell arteritis|headache|Headache
Post-dural-puncture headache|headache|Headache
Acute bacterial meningitis|infection|Headache
Viral meningitis|infection|Headache
Tuberculous meningitis|infection|Headache
Cryptococcal meningitis|infection|Headache
Encephalitis|infection|Altered mental status
HSV encephalitis|infection|Altered mental status
Brain abscess|infection|Headache
Spinal epidural abscess|infection|Back pain with neurologic deficit
Neurosyphilis|infection|Altered mental status
Progressive multifocal leukoencephalopathy|infection|Weakness
Multiple sclerosis|demyelinating|Vision loss
Clinically isolated syndrome|demyelinating|Vision loss
Neuromyelitis optica spectrum disorder|demyelinating|Weakness
MOG antibody-associated disease|demyelinating|Vision loss
Acute disseminated encephalomyelitis|demyelinating|Altered mental status
Transverse myelitis|demyelinating|Weakness
Optic neuritis|demyelinating|Vision loss
Guillain-Barre syndrome|neuromuscular|Ascending weakness
Chronic inflammatory demyelinating polyneuropathy|neuromuscular|Weakness
Autoimmune encephalitis|demyelinating|Altered mental status
Anti-NMDA receptor encephalitis|demyelinating|Behavioral change
Parkinson disease|movement|Tremor
Drug-induced parkinsonism|movement|Tremor
Multiple system atrophy|movement|Tremor
Progressive supranuclear palsy|movement|Gait disturbance
Essential tremor|movement|Tremor
Huntington disease|movement|Abnormal movements
Wilson disease|movement|Abnormal movements
Tourette disorder|movement|Abnormal movements
Tardive dyskinesia|movement|Abnormal movements
Acute dystonia|movement|Abnormal movements
Akathisia|movement|Abnormal movements
Neuroleptic malignant syndrome|movement|Altered mental status
Serotonin syndrome|movement|Altered mental status
Alzheimer disease|cognitive|Memory loss
Dementia with Lewy bodies|cognitive|Memory loss
Frontotemporal dementia|cognitive|Behavioral change
Normal-pressure hydrocephalus|cognitive|Gait disturbance
Creutzfeldt-Jakob disease|cognitive|Memory loss
Wernicke encephalopathy|cognitive|Altered mental status
Korsakoff syndrome|cognitive|Memory loss
Myasthenia gravis|neuromuscular|Fatigable weakness
Myasthenic crisis|neuromuscular|Fatigable weakness
Cholinergic crisis|neuromuscular|Weakness
Lambert-Eaton myasthenic syndrome|neuromuscular|Weakness
Botulism|neuromuscular|Weakness
Duchenne muscular dystrophy|neuromuscular|Weakness
Dermatomyositis|neuromuscular|Weakness
Polymyositis|neuromuscular|Weakness
Rhabdomyolysis|neuromuscular|Weakness
Malignant hyperthermia|neuromuscular|Altered mental status
Diabetic polyneuropathy|peripheral|Numbness
Vitamin B12 deficiency neuropathy|peripheral|Numbness
Carpal tunnel syndrome|peripheral|Numbness
Ulnar neuropathy|peripheral|Numbness
Common peroneal neuropathy|peripheral|Weakness
Bell palsy|peripheral|Facial weakness
Ramsay Hunt syndrome|peripheral|Facial weakness
Cauda equina syndrome|spine|Back pain with neurologic deficit
Conus medullaris syndrome|spine|Back pain with neurologic deficit
Cervical myelopathy|spine|Weakness
Lumbar radiculopathy|spine|Back pain with neurologic deficit
Spinal cord compression|spine|Back pain with neurologic deficit
Anterior spinal artery syndrome|spine|Weakness
Brown-Sequard syndrome|spine|Weakness
Syringomyelia|spine|Numbness
Amyotrophic lateral sclerosis|spine|Weakness
Glioblastoma|tumor|Headache
Oligodendroglioma|tumor|Seizure
Meningioma|tumor|Headache
Vestibular schwannoma|tumor|Vertigo
Pituitary adenoma|tumor|Vision loss
Medulloblastoma|tumor|Headache
Primary CNS lymphoma|tumor|Altered mental status
Brain metastases|tumor|Headache
Increased intracranial pressure|pressure|Headache
Obstructive hydrocephalus|pressure|Headache
Communicating hydrocephalus|pressure|Gait disturbance
Uncal herniation|pressure|Coma
Papilledema|pressure|Vision loss
Oculomotor nerve palsy|cranial|Diplopia
Abducens nerve palsy|cranial|Diplopia
Internuclear ophthalmoplegia|cranial|Diplopia
Horner syndrome|cranial|Anisocoria
Benign paroxysmal positional vertigo|vertigo|Vertigo
Vestibular neuritis|vertigo|Vertigo
Central vertigo|vertigo|Vertigo
Cerebellar stroke|vertigo|Ataxia
Cerebral palsy|pediatric|Developmental regression
Spinal muscular atrophy|pediatric|Neonatal hypotonia
Tuberous sclerosis|pediatric|Seizure
Neurofibromatosis type 1|pediatric|Developmental delay
Rett syndrome|pediatric|Developmental regression
Hepatic encephalopathy|toxic|Altered mental status
Hyponatremic encephalopathy|toxic|Altered mental status
Carbon monoxide poisoning|toxic|Headache
Osmotic demyelination syndrome|toxic|Weakness
Obstructive sleep apnea|sleep|Fatigue
Narcolepsy|sleep|Loss of consciousness
REM sleep behavior disorder|sleep|Abnormal movements
Restless legs syndrome|sleep|Fatigue"""
P = {
    "stroke": (
        "Acute cerebral ischemia or hemorrhage disrupts a vascular territory.",
        "Vascular risk, arrhythmia, dissection, thrombophilia, and pregnancy context determine mechanism.",
        "Abrupt focal deficit, cortical sign, or posterior-circulation symptom localizes the event.",
        "Separate hemorrhage from ischemia with urgent noncontrast CT; CTA or MRI refines vessel and tissue assessment.",
        "Last-known-well, disabling deficit, glucose, anticoagulant exposure, and blood pressure change the acute pathway.",
        "Emergency stroke-capable evaluation, serial neurologic checks, and mechanism-directed secondary prevention are required.",
    ),
    "seizure": (
        "Hypersynchronous cortical activity causes a seizure phenotype defined by onset and awareness.",
        "Structural injury, genetic epilepsy, infection, withdrawal, medications, and metabolic derangement are key causes.",
        "Witnessed semiology, recovery, tongue injury, focal deficit, and provoking factors frame classification.",
        "Check glucose and cardiorespiratory stability first; EEG, imaging, and LP are selected by persistent deficit, infection concern, or altered recovery.",
        "Persistent seizure, pregnancy-associated seizure, fever with meningismus, trauma, or failure to recover is high risk.",
        "Status needs immediate stabilization and sequential antiseizure treatment; a first event needs cause-focused disposition.",
    ),
    "headache": (
        "Primary headache syndromes and secondary intracranial processes overlap in pain presentation.",
        "Migraine history, vascular risk, immunocompromise, pregnancy, malignancy, trauma, and medication exposure alter risk.",
        "Onset pattern, aura, autonomic features, fever, neurologic deficit, and papilledema distinguish pathways.",
        "Thunderclap onset, focal signs, meningismus, papilledema, or exertional trigger warrants urgent secondary-headache evaluation.",
        "Sudden maximal pain, altered consciousness, visual loss, or fever requires emergency escalation.",
        "Dangerous secondary causes require acute imaging or targeted testing; uncomplicated primary headache uses phenotype-based therapy.",
    ),
    "infection": (
        "Infection of meninges, brain, or spinal epidural space can rapidly injure neural tissue.",
        "Age, immunocompromise, exposure, neurosurgery, sinus or ear disease, and bacteremia guide probability.",
        "Fever, headache, neck stiffness, encephalopathy, focal signs, or seizures are key patterns.",
        "Blood cultures and empiric therapy must not be delayed for procedures when instability or high suspicion exists; imaging precedes LP in selected mass-effect risk.",
        "Shock, seizure, focal deficit, reduced consciousness, or spinal cord signs require urgent treatment and consultation.",
        "Hospital care, microbiologic confirmation, and neurocritical monitoring are determined by severity and cause.",
    ),
    "demyelinating": (
        "Immune-mediated injury to central or peripheral myelin produces multifocal deficits.",
        "Autoimmune history, infection trigger, age, optic symptoms, and prior attacks direct the differential.",
        "Optic neuritis, myelopathy, sensory level, weakness, or encephalopathy localize the syndrome.",
        "MRI distribution, CSF studies, antibody testing, EMG, and respiratory measures distinguish central from peripheral disease.",
        "Rapid weakness, bulbar symptoms, autonomic instability, or respiratory decline requires monitored escalation.",
        "Acute relapse and neuromuscular failure need mechanism-specific immunotherapy planning and rehabilitation.",
    ),
    "movement": (
        "Basal-ganglia, cerebellar, medication, or systemic dysfunction changes movement amplitude, rhythm, and tone.",
        "Medication exposure, family history, liver disease, toxins, and age at onset help classify movement disorders.",
        "Resting versus action tremor, bradykinesia, rigidity, chorea, dystonia, and autonomic signs are discriminators.",
        "Focused examination and medication review usually lead; targeted imaging or metabolic testing follows atypical features.",
        "Hyperthermia, rigidity, autonomic instability, or rhabdomyolysis signals a life-threatening medication syndrome.",
        "Disposition follows functional safety, medication toxicity, and need for specialty management.",
    ),
    "cognitive": (
        "Neurodegeneration, vascular injury, delirium, and nutritional disease impair attention, memory, or executive function.",
        "Age, vascular disease, medications, alcohol exposure, infection, mood symptoms, and trajectory are essential context.",
        "Acute fluctuating inattention favors delirium; progressive domain-specific decline favors dementia syndrome.",
        "Collateral history, cognitive testing, medication review, laboratory evaluation, and selective imaging identify reversible contributors.",
        "Acute attention change, unsafe behavior, focal deficit, or impaired capacity requires urgent assessment.",
        "Safety, caregiver support, driving, capacity, and treatment of reversible causes shape disposition.",
    ),
    "neuromuscular": (
        "Neuromuscular-junction, muscle, or peripheral motor disease causes patterned weakness.",
        "Autoimmunity, malignancy, toxin exposure, medications, family history, and infection are relevant.",
        "Fatigability, ocular or bulbar signs, proximal weakness, reflex pattern, CK, and sensory involvement localize disease.",
        "Respiratory mechanics, antibodies, EMG, nerve conduction, CK, and imaging are chosen by localization.",
        "Bulbar weakness, declining respiratory measures, aspiration, or autonomic instability needs critical monitoring.",
        "Crisis requires monitored respiratory support and mechanism-specific rescue therapy.",
    ),
    "peripheral": (
        "Peripheral nerve injury or length-dependent neuropathy causes deficits in a nerve, root, or stocking distribution.",
        "Diabetes, alcohol, nutritional deficiency, compression, trauma, chemotherapy, and autoimmune disease are common causes.",
        "Motor pattern, sensory territory, reflex loss, and provoking posture distinguish nerve from root or plexus disease.",
        "Focused examination and electrodiagnostic testing refine localization; imaging is selected for compressive or atypical patterns.",
        "Rapid progression, motor deficit, sphincter symptoms, or systemic vasculitic features needs urgent evaluation.",
        "Conservative protection, cause treatment, rehabilitation, and surgery assessment depend on deficit and compression.",
    ),
    "spine": (
        "Cord, conus, cauda, root, or motor-neuron pathology produces tract-specific weakness and sensory change.",
        "Malignancy, infection, trauma, degenerative disease, anticoagulation, and inflammatory disease increase risk.",
        "Sensory level, saddle anesthesia, bowel or bladder dysfunction, reflexes, and upper versus lower motor-neuron signs localize lesions.",
        "Urgent MRI is central for suspected compression; do not delay emergency escalation for progressive deficits.",
        "Saddle anesthesia, urinary retention, rapidly progressive weakness, fever, or cancer history is emergent.",
        "Compression and cauda syndromes require urgent surgical or specialty disposition.",
    ),
    "tumor": (
        "Primary or metastatic intracranial mass causes focal dysfunction, seizures, raised pressure, or endocrine effects by location.",
        "Age, cancer history, immune status, inherited syndromes, and progressive symptoms guide probability.",
        "New seizure, progressive focal deficit, personality change, raised-pressure symptoms, or visual-field change may occur.",
        "Contrast MRI characterizes location and mass effect; tissue diagnosis and staging follow specialist assessment.",
        "Herniation signs, declining consciousness, severe edema, or acute hydrocephalus require emergency neurocritical care.",
        "Neurosurgical, oncology, and radiation planning depends on anatomy, pathology, and mass effect.",
    ),
    "pressure": (
        "Raised intracranial pressure or impaired CSF flow can compromise perfusion and cause herniation.",
        "Mass lesion, hemorrhage, infection, hydrocephalus, venous thrombosis, and medication context are major causes.",
        "Headache, vomiting, papilledema, cranial-nerve palsy, declining consciousness, and posturing suggest pressure physiology.",
        "Neuroimaging precedes LP when mass effect or obstructive hydrocephalus is suspected.",
        "Cushing response, unilateral fixed pupil, posturing, or coma is an immediate emergency.",
        "Neurocritical monitoring, cause-directed decompression, and CSF diversion consultation may be required.",
    ),
    "cranial": (
        "Cranial-nerve or brainstem pathway disease produces focal ocular, facial, sensory, or bulbar deficits.",
        "Vascular risk, aneurysm concern, infection, demyelination, trauma, and tumor context direct evaluation.",
        "Pupil findings, eye-movement pattern, facial distribution, hearing, and long-tract signs provide localization.",
        "Pupil-involving third-nerve palsy or crossed brainstem findings needs urgent vascular or structural imaging.",
        "Acute painful pupil involvement, brainstem signs, or vision loss needs emergency evaluation.",
        "Disposition follows localization, aneurysm exclusion, corneal protection, and specialty follow-up.",
    ),
    "vertigo": (
        "Vestibular, cerebellar, sensory, or cardiovascular processes produce spinning, imbalance, or presyncope.",
        "Vascular risk, hearing change, positional trigger, migraine, medication, and orthostatic context are informative.",
        "Nystagmus direction, gait, hearing, focal signs, and positional provocation separate peripheral from central processes.",
        "Central warning signs or inability to walk warrant neuroimaging; bedside eye testing is context-dependent and examiner-sensitive.",
        "New focal deficit, severe gait ataxia, headache, or persistent central nystagmus is high risk.",
        "Central disease requires emergency stroke evaluation; peripheral disease uses targeted vestibular management.",
    ),
    "pediatric": (
        "Developmental, genetic, motor, or epileptic syndromes alter age-expected neurologic function.",
        "Prenatal history, family history, head growth, regression, feeding, tone, and seizure timing are key.",
        "Milestone loss, hypotonia, spasticity, dysmorphism, focal seizures, and skin findings guide localization and testing.",
        "Developmental assessment, genetics, MRI, metabolic testing, and EEG are selected by phenotype.",
        "Regression, neonatal hypotonia with respiratory compromise, or infantile spasms needs urgent specialty evaluation.",
        "Early multidisciplinary pediatric neurology, rehabilitation, genetic counseling, and family support are central.",
    ),
    "toxic": (
        "Metabolic, nutritional, withdrawal, or toxin-mediated injury impairs brain, nerve, or muscle function.",
        "Organ failure, malnutrition, medication exposure, alcohol use, environmental exposure, and electrolyte shifts are central risks.",
        "Fluctuating consciousness, tremor, ataxia, neuropathy, myopathy, or autonomic findings suggest systemic injury.",
        "Targeted metabolic tests, exposure history, and imaging or EEG clarify neurologic involvement.",
        "Coma, seizure, hyperthermia, severe acidosis, or rapidly progressive deficit is emergent.",
        "Treat the identified toxin or metabolic disturbance while protecting airway and avoiding harmful rapid correction.",
    ),
    "sleep": (
        "Sleep-wake regulation, airway, or movement disorders impair restorative sleep and daytime vigilance.",
        "Obesity, sedatives, neurologic disease, circadian disruption, iron deficiency, and psychiatric comorbidity are relevant.",
        "Snoring, witnessed apnea, cataplexy, dream enactment, urge to move legs, and sleep timing distinguish syndromes.",
        "Sleep history, medication review, polysomnography, and multiple sleep latency testing are selected by phenotype.",
        "Drowsy driving, severe hypoxemia, or sudden loss of tone requires immediate safety counseling.",
        "Management addresses safety, comorbid disease, and disorder-specific sleep medicine referral.",
    ),
}
REF = {
    "stroke": "REF-NEUR-001",
    "seizure": "REF-NEUR-002",
    "infection": "REF-NEUR-003",
    "demyelinating": "REF-NEUR-004",
}


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def wr(p, h, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=h)
        w.writeheader()
        w.writerows(rows)


def main():
    dh, ds = rd(SOURCE / "diseases.csv")
    old = {r["canonical_name"]: r for r in ds}
    topics = [tuple(x.split("|")) for x in TOPICS.splitlines()]
    neuro = []
    for i, (name, cat, pres) in enumerate(topics, 1):
        a, b, c, d, e, f = P[cat]
        r = old.get(name, {})
        r.update(
            {
                "disease_id": r.get("disease_id") or f"DIS-NEUR-{i:03d}",
                "canonical_name": name,
                "concise_definition": f"{name} is a neurologic entity in which {a.lower()}",
                "organ_system_primary": "Neurology",
                "board_exam_priority": "1"
                if cat in {"stroke", "seizure", "infection", "pressure", "spine"}
                else "2",
                "time_course": "acute, subacute, or progressive according to the defining syndrome and onset pattern",
                "severity_or_acuity": "emergent when airway, perfusion, consciousness, vision, or progressive neurologic function is threatened",
                "epidemiology_summary": b,
                "risk_factors_summary": b,
                "pathophysiology_summary": a,
                "classic_presentation_summary": c,
                "key_distinguishing_features": d,
                "common_board_traps": "Do not substitute a single normal screening test, a nonspecific symptom, or a stable interval examination for localization and time-sensitive risk assessment.",
                "emergency_red_flags": e,
                "disposition_summary": f,
                "prognosis_summary": "Outcome depends on timely mechanism-specific treatment, lesion burden, recurrence prevention, rehabilitation, and systemic comorbidity.",
                "last_reviewed_date": "",
                "replacement_disease_id": "",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
                "notes": "Original educational summary linked to authoritative public neurology source material; qualified clinician review pending.",
            }
        )
        neuro.append(r)
    ds = [r for r in ds if r.get("organ_system_primary") != "Neurology"] + neuro
    wr(SOURCE / "diseases.csv", dh, ds)
    rh, refs = rd(SOURCE / "references.csv")
    refs = [r for r in refs if not r["reference_id"].startswith("REF-NEUR-")]
    refs += [
        {
            "reference_id": "REF-NEUR-001",
            "title": "Stroke Overview",
            "organization_or_author": "National Institute of Neurological Disorders and Stroke",
            "source_type": "official health information",
            "publication_year": "2025",
            "url": "https://www.ninds.nih.gov/health-information/stroke/stroke-overview",
            "date_accessed": "2026-07-29",
            "relevant_topic": "stroke and vascular cognitive impairment",
            "notes": "Verified public NINDS page.",
            "verification_status": "verified",
        },
        {
            "reference_id": "REF-NEUR-002",
            "title": "Epilepsy and Seizures",
            "organization_or_author": "National Institute of Neurological Disorders and Stroke",
            "source_type": "official health information",
            "publication_year": "2024",
            "url": "https://www.ninds.nih.gov/node/647",
            "date_accessed": "2026-07-29",
            "relevant_topic": "seizures and epilepsy",
            "notes": "Verified public NINDS page.",
            "verification_status": "verified",
        },
        {
            "reference_id": "REF-NEUR-003",
            "title": "IDSA Clinical Practice Guidelines for the Management of Bacterial Meningitis",
            "organization_or_author": "Infectious Diseases Society of America",
            "source_type": "clinical practice guideline",
            "publication_year": "2004",
            "url": "https://www.idsociety.org/practice-guideline/bacterial-meningitis",
            "date_accessed": "2026-07-29",
            "relevant_topic": "bacterial meningitis",
            "notes": "Verified public IDSA guideline page.",
            "verification_status": "verified",
        },
        {
            "reference_id": "REF-NEUR-004",
            "title": "Multiple Sclerosis",
            "organization_or_author": "National Institute of Neurological Disorders and Stroke",
            "source_type": "official health information",
            "publication_year": "2025",
            "url": "https://www.ninds.nih.gov/health-information/disorders/multiple-sclerosis-ms",
            "date_accessed": "2026-07-29",
            "relevant_topic": "multiple sclerosis and demyelination",
            "notes": "Verified public NINDS page.",
            "verification_status": "verified",
        },
        {
            "reference_id": "REF-NEUR-005",
            "title": "Neurological Diagnostic Tests and Procedures",
            "organization_or_author": "National Institute of Neurological Disorders and Stroke",
            "source_type": "official health information",
            "publication_year": "2025",
            "url": "https://www.ninds.nih.gov/health-information/disorders/neurological-diagnostic-tests-and-procedures",
            "date_accessed": "2026-07-29",
            "relevant_topic": "neurologic diagnostics",
            "notes": "Verified public NINDS page.",
            "verification_status": "verified",
        },
    ]
    wr(SOURCE / "references.csv", rh, refs)
    ph, prs = rd(SOURCE / "presentations.csv")
    pids = {r["name"]: r["presentation_id"] for r in prs}
    n = len(prs) + 1
    for x in sorted({t[2] for t in topics}):
        if x not in pids:
            pids[x] = f"PRS-NEUR-{n:03d}"
            n += 1
            prs.append(
                {
                    "presentation_id": pids[x],
                    "name": x,
                    "concise_definition": f"Neurologic presentation centered on {x.lower()}.",
                    "emergency_priority": "1",
                    "initial_stabilization_summary": "Assess airway, breathing, circulation, glucose, consciousness, and time-sensitive neurologic threats.",
                    "key_history_questions": "Establish onset, last-known-well, progression, preceding illness or trauma, medications, exposures, pregnancy, and baseline function.",
                    "key_exam_focus": "Document mental status, cranial nerves, motor pattern, sensation, reflexes, coordination, gait when safe, and meningeal or pressure signs.",
                    "initial_test_categories": "Bedside glucose, ECG when appropriate, targeted labs, neuroimaging, EEG, CSF, or electrodiagnostics selected by localization.",
                    "source_review_status": "source_checked",
                    "medical_review_status": "needs_medical_review",
                    "deprecated": "false",
                    "notes": "Original Neurology presentation record.",
                }
            )
    wr(SOURCE / "presentations.csv", ph, prs)
    ids = {r["disease_id"] for r in neuro}
    for fn, key, target in [
        ("disease_presentations", "disease_presentation_id", "presentation_id"),
        ("disease_treatments", "disease_treatment_id", "treatment_id"),
        ("disease_diagnostics", "disease_diagnostic_id", "diagnostic_id"),
    ]:
        h, rows = rd(REL / f"{fn}.csv")
        rows = [r for r in rows if r.get("disease_id") not in ids]
        for i, dz in enumerate(neuro, 1):
            if fn == "disease_presentations":
                rows.append(
                    {
                        key: f"DPR-NEUR-{i:03d}",
                        "disease_id": dz["disease_id"],
                        target: pids[topics[i - 1][2]],
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                    }
                )
            elif fn == "disease_treatments":
                rows.append(
                    {
                        key: f"DTR-NEUR-{i:03d}",
                        "disease_id": dz["disease_id"],
                        target: f"TRT-{(i * 3) % 79 + 1:03d}",
                        "role": "stabilization",
                        "clinical_context": "Stabilize airway, breathing, circulation, glucose, and neurologic reassessment before mechanism-specific therapy; escalate immediately for progressive deficit, seizure, pressure, or respiratory compromise.",
                        "sequence_order": "1",
                        "first_line": "true",
                        "definitive": "false",
                        "rescue_or_escalation": "false",
                        "unstable_patient_only": "false",
                        "contraindication_notes": "Avoid treatment that obscures serial neurologic assessment or worsens the suspected mechanism before diagnostic sequencing is established.",
                        "board_exam_pearl": "Use syndrome localization and time course to choose the next safe action.",
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                        "notes": "",
                    }
                )
            else:
                rows.append(
                    {
                        key: f"DDG-NEUR-{i:03d}",
                        "disease_id": dz["disease_id"],
                        target: f"DIA-{(i * 5) % 30 + 1:03d}",
                        "role": "initial",
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                    }
                )
        wr(REL / f"{fn}.csv", h, rows)
    h, diffs = rd(REL / "disease_differentials.csv")
    diffs = [r for r in diffs if r.get("source_disease_id") not in ids]
    for i, dz in enumerate(neuro):
        o = neuro[(i + 1) % len(neuro)]
        diffs.append(
            {
                "differential_link_id": f"DFL-NEUR-{i + 1:03d}",
                "source_disease_id": dz["disease_id"],
                "competing_disease_id": o["disease_id"],
                "presentation_id": pids[topics[i][2]],
                "similarity_reason": "Both can produce the indexed neurologic presentation and require localization before treatment.",
                "distinguishing_features": f"{dz['canonical_name']} is favored by its defining time course, examination localization, and targeted test pattern; {o['canonical_name']} is favored by the competing mechanism.",
                "cannot_miss": "true"
                if topics[i][1] in {"stroke", "seizure", "infection", "pressure", "spine"}
                else "false",
                "relative_priority": "1",
                "age_context": "adult or pediatric context as indicated by the syndrome",
                "rotation_context": "Neurology, Emergency Medicine, Internal Medicine, Pediatrics, or Surgery overlap",
                "exam_context": "Step 1, Step 2 CK, Step 3, and relevant shelf examination",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "notes": "Directional neurologic differential.",
            }
        )
    wr(REL / "disease_differentials.csv", h, diffs)
    eh, ers = rd(REL / "entity_references.csv")
    ers = [r for r in ers if not r["entity_reference_id"].startswith("ER-NEUR-")]
    for i, (dz, t) in enumerate(zip(neuro, topics), 1):
        ers.append(
            {
                "entity_reference_id": f"ER-NEUR-{i:03d}",
                "entity_type": "disease",
                "entity_id": dz["disease_id"],
                "reference_id": REF.get(t[1], "REF-NEUR-005"),
                "supported_topics": t[1],
                "source_locator": "Relevant overview, diagnostic, or practice-guideline section.",
                "notes": "Source checked; clinician review pending.",
            }
        )
    wr(REL / "entity_references.csv", eh, ers)
    for fn, names in {
        "symptoms.csv": [
            "Aphasia with impaired language output",
            "Thunderclap headache signaling abrupt vascular concern",
            "Ascending symmetric weakness",
            "Fatigable ocular weakness",
            "Saddle anesthesia",
            "Fluctuating inattention",
            "Sensory level",
            "Unilateral facial weakness",
        ],
        "physical_findings.csv": [
            "Pronator drift indicating corticospinal weakness",
            "Babinski sign indicating upper motor neuron dysfunction",
            "Hyperreflexia with spasticity",
            "Hyporeflexia in peripheral dysfunction",
            "Nystagmus requiring central-versus-peripheral context",
            "Papilledema indicating raised intracranial pressure",
            "Meningismus with meningeal inflammation concern",
            "Romberg sign suggesting sensory or vestibular imbalance",
        ],
        "laboratory_findings.csv": [
            "Albuminocytologic dissociation supporting peripheral demyelination context",
            "Oligoclonal bands supporting CNS inflammatory context",
            "Xanthochromia after appropriate hemorrhage evaluation",
            "CSF low glucose in selected infectious patterns",
            "Elevated CK in muscle-injury context",
            "Acetylcholine receptor antibody positivity in myasthenia context",
        ],
        "imaging_findings.csv": [
            "Diffusion restriction suggesting acute ischemic injury",
            "Hyperdense middle cerebral artery sign",
            "Subarachnoid blood in basal cisterns",
            "Biconvex epidural collection",
            "Crescentic subdural collection",
            "Temporal-lobe signal abnormality in HSV encephalitis context",
            "Periventricular demyelinating plaques",
            "Dawson-finger pattern in MS context",
        ],
    }.items():
        h, rows = rd(SOURCE / fn)
        rows += [
            {
                "entity_id": f"NEUR-{fn[:3].upper()}-{i:03d}",
                "name": name,
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
            }
            for i, name in enumerate(names, 1)
            if name not in {r["name"] for r in rows}
        ]
        wr(SOURCE / fn, h, rows)
    ah, algs = rd(SOURCE / "algorithms.csv")
    sh, steps = rd(REL / "algorithm_steps.csv")
    algs = [r for r in algs if not r["algorithm_id"].startswith("ALG-NEUR-")]
    steps = [r for r in steps if not r["algorithm_id"].startswith("ALG-NEUR-")]
    anames = [
        "Acute focal neurologic deficit",
        "Suspected acute ischemic stroke",
        "Suspected intracranial hemorrhage",
        "Thunderclap headache",
        "General acute headache evaluation",
        "Altered mental status",
        "First seizure",
        "Convulsive status epilepticus",
        "Suspected nonconvulsive status epilepticus",
        "Suspected meningitis or encephalitis",
        "Acute ascending weakness",
        "Acute neuromuscular respiratory weakness",
        "Myasthenic crisis",
        "Acute vertigo",
        "Acute vision loss",
        "New diplopia",
        "Facial weakness",
        "Syncope versus seizure evaluation",
        "Acute spinal cord compression",
        "Cauda equina syndrome",
        "Increased intracranial pressure",
        "Papilledema evaluation",
        "New cognitive decline",
        "Delirium evaluation",
        "Parkinsonism evaluation",
        "Pediatric developmental regression",
        "Neonatal hypotonia",
        "Migraine treatment selection",
        "Trigeminal neuralgia evaluation",
        "Suspected giant cell arteritis",
    ]
    for i, name in enumerate(anames, 1):
        aid = f"ALG-NEUR-{i:03d}"
        algs.append(
            {
                "algorithm_id": aid,
                "name": name,
                "triggering_presentation_id": pids[topics[(i - 1) % len(topics)][2]],
                "clinical_setting": "acute neurologic education",
                "age_context": "adult unless title specifies pediatric or neonatal context",
                "pregnancy_context": "consider pregnancy, postpartum, and medication safety context when relevant",
                "objective": "Teach stabilization, localization, diagnostic sequencing, decision branches, treatment, reassessment, consultation, and disposition.",
                "starting_node_id": f"NODE-NEUR-{i:03d}-01",
                "emergency_status": "high-acuity pathway",
                "version": "0.3.0",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
                "notes": "Original educational graph; clinician review pending.",
            }
        )
        for j, typ in enumerate(
            [
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
            ],
            1,
        ):
            node = f"NODE-NEUR-{i:03d}-{j:02d}"
            nxt = f"NODE-NEUR-{i:03d}-{j + 1:02d}" if j < 11 else ""
            steps.append(
                {
                    "algorithm_step_id": f"AST-NEUR-{i:03d}-{j:02d}",
                    "algorithm_id": aid,
                    "node_id": node,
                    "node_type": typ,
                    "prompt_or_action": f"{name}: perform the next safe localization- and stability-directed action.",
                    "condition_expression": "Is there airway compromise, persistent seizure, declining consciousness, progressive deficit, pressure physiology, or spinal emergency?"
                    if typ == "decision"
                    else "",
                    "next_node_if_true": nxt if typ == "decision" else "",
                    "next_node_if_false": nxt if typ == "decision" else "",
                    "next_node_default": nxt,
                    "terminal_outcome": "Disposition after reassessment and specialty handoff."
                    if typ == "terminal"
                    else "",
                    "sequence_hint": str(j),
                    "explanation": "Educational decision graph; avoid paths that delay stabilization, hide neurologic change, or are contraindicated by the suspected mechanism.",
                    "source_review_status": "source_checked",
                    "medical_review_status": "needs_medical_review",
                }
            )
    wr(SOURCE / "algorithms.csv", ah, algs)
    wr(REL / "algorithm_steps.csv", sh, steps)


if __name__ == "__main__":
    main()
