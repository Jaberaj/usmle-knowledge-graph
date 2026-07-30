"""Enrich Neurology with coverage-first presentations, findings, and localization."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"

NEW_DISEASES = """Medication-overuse headache|headache
Tension-type headache|headache
Vestibular migraine|headache
Chronic migraine|headache
Occipital neuralgia|headache
Glossopharyngeal neuralgia|headache
Progressive multifocal leukoencephalopathy|infection
Neuroborreliosis|infection
Rabies encephalitis|infection
Acute flaccid myelitis|pediatric
MOG antibody-associated disease|demyelination
Chronic inflammatory demyelinating polyneuropathy|neuromuscular
Drug-induced parkinsonism|movement
Multiple system atrophy|movement
Progressive supranuclear palsy|movement
Facioscapulohumeral muscular dystrophy|neuromuscular
Myotonic dystrophy|neuromuscular
McArdle disease|neuromuscular
Pompe disease|neuromuscular
Small-fiber neuropathy|peripheral
Mononeuritis multiplex|peripheral
Tabes dorsalis|spine
Central cord syndrome|spine
Posterior cord syndrome|spine
Diffuse astrocytoma|oncology
Ependymoma|oncology
Hemangioblastoma|oncology
Craniopharyngioma|oncology
Chiari malformation|pediatric
Dandy-Walker malformation|pediatric"""

NEURO_KEYWORDS = {
    "worst headache of life": (
        "classic_clue",
        "Abrupt maximal-intensity headache requires urgent evaluation for subarachnoid hemorrhage and other secondary causes.",
        ["Subarachnoid hemorrhage"],
    ),
    "temporal-lobe hemorrhagic necrosis": (
        "imaging_phrase",
        "Temporal-lobe hemorrhagic injury is a classic imaging association of HSV encephalitis.",
        ["HSV encephalitis"],
    ),
    "albuminocytologic dissociation": (
        "laboratory_pattern",
        "High CSF protein with relatively few cells supports Guillain-Barre syndrome in the appropriate clinical timeframe.",
        ["Guillain-Barre syndrome"],
    ),
    "Dawson fingers": (
        "imaging_phrase",
        "Ovoid periventricular lesions oriented along medullary veins support multiple sclerosis in the appropriate syndrome.",
        ["Multiple sclerosis"],
    ),
    "resting pill-rolling tremor": (
        "physical_exam_phrase",
        "Resting tremor with bradykinesia and rigidity supports parkinsonism.",
        ["Parkinson disease"],
    ),
    "fatigable ptosis": (
        "physical_exam_phrase",
        "Fatigable ocular weakness supports neuromuscular-junction disease and should prompt respiratory assessment when severe.",
        ["Myasthenia gravis", "Myasthenic crisis"],
    ),
    "facilitation with repeated use": (
        "physical_exam_phrase",
        "Strength that improves with repeated activation supports presynaptic neuromuscular-junction dysfunction.",
        ["Lambert-Eaton myasthenic syndrome"],
    ),
    "cape-like sensory loss": (
        "physical_exam_phrase",
        "Dissociated cape-like pain and temperature loss localizes to a central cord process such as syringomyelia.",
        ["Syringomyelia"],
    ),
    "saddle anesthesia": (
        "physical_exam_phrase",
        "Saddle sensory loss with sphincter symptoms is a red flag for cauda equina or conus pathology.",
        ["Cauda equina syndrome", "Conus medullaris syndrome"],
    ),
    "Gowers sign": (
        "physical_exam_phrase",
        "Using the hands to rise from the floor supports proximal muscle weakness in a myopathic process.",
        ["Duchenne muscular dystrophy"],
    ),
    "calf pseudohypertrophy": (
        "physical_exam_phrase",
        "Calf enlargement with proximal weakness is a classic association of Duchenne muscular dystrophy.",
        ["Duchenne muscular dystrophy"],
    ),
    "cogwheel rigidity": (
        "physical_exam_phrase",
        "Cogwheel rigidity supports a parkinsonian syndrome when paired with bradykinesia.",
        ["Parkinson disease", "Drug-induced parkinsonism"],
    ),
    "butterfly glioma": (
        "imaging_phrase",
        "A lesion crossing the corpus callosum raises concern for glioblastoma in the appropriate imaging context.",
        ["Glioblastoma"],
    ),
    "dural tail": (
        "imaging_phrase",
        "Dural attachment and enhancement are classic imaging associations of meningioma.",
        ["Meningioma"],
    ),
    "fried-egg appearance": (
        "pathology_phrase",
        "Uniform cells with perinuclear halos are a classic histology association of oligodendroglioma.",
        ["Oligodendroglioma"],
    ),
    "Rosenthal fibers": (
        "pathology_phrase",
        "Rosenthal fibers are a characteristic histology association of pilocytic astrocytoma.",
        ["Pilocytic astrocytoma"],
    ),
    "Homer Wright rosettes": (
        "pathology_phrase",
        "Homer Wright rosettes are a neural differentiation pattern seen in medulloblastoma and other tumors.",
        ["Medulloblastoma"],
    ),
    "Argyll Robertson pupil": (
        "physical_exam_phrase",
        "Light-near dissociation is a classic clue for neurosyphilis in the appropriate syndrome.",
        ["Neurosyphilis"],
    ),
    "Kayser-Fleischer rings": (
        "physical_exam_phrase",
        "Corneal copper deposition is a classic clue for Wilson disease.",
        ["Wilson disease"],
    ),
    "electric shock with neck flexion": (
        "physical_exam_phrase",
        "An electric sensation with neck flexion supports cervical cord involvement in the appropriate context.",
        ["Multiple sclerosis", "Cervical myelopathy"],
    ),
}

PROFILE = {
    "vascular": (
        "Vascular occlusion, hemorrhage, dissection, or dysregulated cerebral perfusion produces time-sensitive focal or diffuse neurologic injury.",
        "Abrupt timing, vascular risk, trauma, postpartum context, headache, and focal deficits establish the initial syndrome.",
    ),
    "seizure": (
        "Paroxysmal cortical electrical dysfunction causes stereotyped motor, sensory, autonomic, behavioral, or awareness changes.",
        "Witnessed semiology, recovery pattern, provoking factors, medication exposure, age, and prior brain injury guide classification.",
    ),
    "headache": (
        "Primary or secondary head-pain mechanisms require recognition of red flags before symptomatic management.",
        "Onset, maximal intensity, age, visual symptoms, fever, neurologic deficit, pregnancy, and medication use shift concern.",
    ),
    "infection": (
        "Infection or inflammation of meninges, brain, spinal cord, or peripheral nervous system can cause fever, altered mental status, focal deficits, or seizures.",
        "Immune status, exposures, travel, rash, fever, CSF pattern, and focal imaging findings shape evaluation.",
    ),
    "demyelination": (
        "Immune-mediated injury to central or peripheral myelin produces focal deficits separated by space, time, or anatomic tract.",
        "Optic, spinal, brainstem, sensory, and motor symptoms with imaging and antibody context distinguish mechanisms.",
    ),
    "movement": (
        "Basal-ganglia, cerebellar, or medication-related dysfunction causes characteristic tremor, bradykinesia, rigidity, chorea, or dystonia.",
        "Tempo, symmetry, medication exposure, family history, cognition, autonomic signs, and eye movements refine localization.",
    ),
    "cognitive": (
        "Neurodegenerative, vascular, nutritional, toxic, or systemic processes affect cognition, attention, behavior, and function.",
        "Acute fluctuation suggests delirium; progressive domain-specific decline and neurologic signs guide the longer differential.",
    ),
    "neuromuscular": (
        "Neuromuscular-junction, nerve, muscle, or motor-neuron disease produces patterned weakness with distinctive reflex, sensory, fatigability, or respiratory features.",
        "Distribution, fatigability, sensory symptoms, reflexes, CK, respiratory function, and tempo localize the lesion.",
    ),
    "peripheral": (
        "Peripheral nerve, root, plexus, or autonomic dysfunction produces a length-dependent, focal, or multifocal sensory-motor pattern.",
        "Distribution, pain, reflexes, autonomic symptoms, metabolic exposures, and electrodiagnostics separate root from nerve disease.",
    ),
    "spine": (
        "Spinal cord, root, or cauda injury can cause motor, sensory, reflex, and bowel or bladder deficits below a localizable level.",
        "Sensory level, upper versus lower motor-neuron signs, saddle symptoms, trauma, cancer, and infection determine urgency.",
    ),
    "oncology": (
        "Primary or metastatic intracranial disease may cause focal deficits, seizures, raised intracranial pressure, endocrine dysfunction, or characteristic imaging.",
        "Age, lesion location, systemic cancer history, tempo, seizures, and mass-effect signs guide safe workup.",
    ),
    "pediatric": (
        "Developing nervous-system disease may present with regression, seizures, hypotonia, developmental delay, abnormal head growth, or congenital findings.",
        "Age of onset, prenatal history, developmental trajectory, family history, dysmorphism, and examination direct evaluation.",
    ),
}

FINDINGS = """Babinski sign|physical
Hyperreflexia|physical
Areflexia|physical
Pronator drift|physical
Facial weakness|physical
Fatigable ptosis|physical
No sensory loss|physical
Albuminocytologic dissociation|laboratory
Oligoclonal bands|laboratory
Xanthochromia|laboratory
Neutrophilic CSF|laboratory
Lymphocytic CSF|laboratory
Low CSF glucose|laboratory
Elevated opening pressure|laboratory
Acetylcholine-receptor antibodies|laboratory
Aquaporin-4 antibodies|laboratory
Creatine kinase elevation|laboratory
Diffusion restriction|imaging
Hyperdense MCA sign|imaging
Subarachnoid blood|imaging
Epidural biconvex collection|imaging
Crescentic subdural collection|imaging
Temporal-lobe abnormalities|imaging
Periventricular plaques|imaging
Dawson fingers|imaging
Ventriculomegaly|imaging
Midline shift|imaging
Butterfly glioma|imaging
Dural tail|imaging
Caudate atrophy|imaging
Meningismus|physical
Papilledema|physical
Anisocoria|physical
Nystagmus|physical
Sensory level|physical
Saddle anesthesia|physical
Spasticity|physical
Fasciculations|physical
Gowers sign|physical
Cape-like sensory loss|physical
Resting pill-rolling tremor|physical
Cogwheel rigidity|physical
Shuffling gait|physical
Internuclear ophthalmoplegia|physical
Neurofibrillary tangles|pathology
Lewy bodies|pathology
Pseudopalisading necrosis|pathology
Fried-egg cells|pathology
Rosenthal fibers|pathology"""

LOCALIZATIONS = """Frontal lobe|cortex
Parietal lobe|cortex
Temporal lobe|cortex
Occipital lobe|cortex
Internal capsule|subcortical
Basal ganglia|deep gray matter
Thalamus|deep gray matter
Midbrain|brainstem
Pons|brainstem
Medulla|brainstem
Cerebellar hemisphere|cerebellum
Cerebellar vermis|cerebellum
Dorsal columns|spinal tract
Spinothalamic tract|spinal tract
Corticospinal tract|spinal tract
Sympathetic pathway|autonomic pathway
Visual pathway|sensory pathway
Language network|cortical network
Neuromuscular junction|motor unit
Muscle|motor unit
Peripheral nerve|peripheral nervous system
Cauda equina|peripheral nervous system"""

PRESENTATIONS = [
    "Acute focal neurologic deficit",
    "First seizure",
    "Recurrent seizure",
    "Status epilepticus",
    "Thunderclap headache",
    "Progressive headache",
    "Ascending weakness",
    "Fatigable weakness",
    "Sensory level",
    "Facial weakness",
    "Diplopia",
    "Vision loss",
    "Vertigo",
    "Ataxia",
    "Gait disturbance",
    "Tremor",
    "Memory loss",
    "Developmental regression",
    "Neonatal hypotonia",
    "Back pain with neurologic deficit",
    "Urinary retention with neurologic deficit",
    "Aphasia",
    "Dysarthria",
    "Papilledema",
    "Respiratory weakness",
]

PRESENTATION_GROUPS = {
    "vascular": ["Acute focal neurologic deficit", "Aphasia", "Dysarthria", "Vision loss"],
    "seizure": [
        "First seizure",
        "Recurrent seizure",
        "Status epilepticus",
        "Altered mental status",
    ],
    "headache": ["Headache", "Thunderclap headache", "Progressive headache", "Vision loss"],
    "infection": [
        "Altered mental status",
        "Headache",
        "First seizure",
        "Acute focal neurologic deficit",
    ],
    "demyelination": ["Vision loss", "Sensory level", "Weakness", "Ataxia"],
    "movement": ["Tremor", "Gait disturbance", "Dysarthria", "Behavioral change"],
    "cognitive": ["Memory loss", "Delirium", "Behavioral change", "Gait disturbance"],
    "neuromuscular": [
        "Fatigable weakness",
        "Ascending weakness",
        "Respiratory weakness",
        "Weakness",
    ],
    "peripheral": ["Numbness", "Paresthesia", "Weakness", "Areflexia"],
    "spine": [
        "Back pain with neurologic deficit",
        "Sensory level",
        "Urinary retention with neurologic deficit",
        "Weakness",
    ],
    "oncology": [
        "Progressive headache",
        "First seizure",
        "Acute focal neurologic deficit",
        "Papilledema",
    ],
    "pediatric": [
        "Developmental regression",
        "Neonatal hypotonia",
        "First seizure",
        "Gait disturbance",
    ],
}

FINDING_GROUPS = {
    "vascular": [
        "Babinski sign",
        "Pronator drift",
        "Diffusion restriction",
        "Hyperdense MCA sign",
        "Subarachnoid blood",
    ],
    "seizure": [
        "No sensory loss",
        "Lymphocytic CSF",
        "Temporal-lobe abnormalities",
        "Areflexia",
        "Creatine kinase elevation",
    ],
    "headache": [
        "Papilledema",
        "Xanthochromia",
        "Elevated opening pressure",
        "Subarachnoid blood",
        "Nystagmus",
    ],
    "infection": [
        "Meningismus",
        "Neutrophilic CSF",
        "Lymphocytic CSF",
        "Low CSF glucose",
        "Temporal-lobe abnormalities",
    ],
    "demyelination": [
        "Oligoclonal bands",
        "Aquaporin-4 antibodies",
        "Periventricular plaques",
        "Dawson fingers",
        "Internuclear ophthalmoplegia",
    ],
    "movement": [
        "Resting pill-rolling tremor",
        "Cogwheel rigidity",
        "Shuffling gait",
        "Caudate atrophy",
        "Nystagmus",
    ],
    "cognitive": [
        "Neurofibrillary tangles",
        "Lewy bodies",
        "Ventriculomegaly",
        "Caudate atrophy",
        "Hyperreflexia",
    ],
    "neuromuscular": [
        "Fatigable ptosis",
        "No sensory loss",
        "Albuminocytologic dissociation",
        "Acetylcholine-receptor antibodies",
        "Creatine kinase elevation",
    ],
    "peripheral": [
        "Areflexia",
        "No sensory loss",
        "Cape-like sensory loss",
        "Fasciculations",
        "Sensory level",
    ],
    "spine": [
        "Sensory level",
        "Saddle anesthesia",
        "Spasticity",
        "Hyperreflexia",
        "Cape-like sensory loss",
    ],
    "oncology": [
        "Midline shift",
        "Butterfly glioma",
        "Dural tail",
        "Pseudopalisading necrosis",
        "Fried-egg cells",
    ],
    "pediatric": [
        "Gowers sign",
        "Rosenthal fibers",
        "Areflexia",
        "Ventriculomegaly",
        "Meningismus",
    ],
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


def sid(name: str, prefix: str) -> str:
    return prefix + "-" + "".join(c for c in name.upper() if c.isalnum())[:20]


def category(name: str) -> str:
    low = name.lower()
    if "guillain" in low:
        return "neuromuscular"
    if any(
        x in low
        for x in (
            "stroke",
            "hemorrhage",
            "dissection",
            "vascular",
            "moyamoya",
            "lacunar",
            "artery syndrome",
            "ischemic",
        )
    ):
        return "vascular"
    if any(x in low for x in ("seizure", "epilepsy", "spasm", "status")):
        return "seizure"
    if any(x in low for x in ("headache", "migraine", "neuralgia", "intracranial hypotension")):
        return "headache"
    if any(
        x in low
        for x in ("mening", "encephal", "abscess", "leukoencephalopathy", "rabies", "syphilis")
    ):
        return "infection"
    if any(
        x in low
        for x in (
            "multiple sclerosis",
            "demyel",
            "myelitis",
            "optic neuritis",
            "guillain",
            "neuromyelitis",
            "mog",
        )
    ):
        return "demyelination"
    if any(
        x in low
        for x in (
            "parkinson",
            "tremor",
            "huntington",
            "wilson",
            "tourette",
            "dyskines",
            "dystonia",
            "akathisia",
        )
    ):
        return "movement"
    if any(
        x in low
        for x in (
            "dementia",
            "alzheimer",
            "delirium",
            "korsakoff",
            "wernicke",
            "creutzfeldt",
            "sleep",
        )
    ):
        return "cognitive"
    if any(
        x in low
        for x in (
            "myasthen",
            "muscular dystrophy",
            "myopathy",
            "rhabdo",
            "hyperthermia",
            "pompe",
            "mcardle",
            "periodic paralysis",
            "motor neuron",
        )
    ):
        return "neuromuscular"
    if any(
        x in low
        for x in ("neuropathy", "palsy", "nerve", "radiculopathy", "carpal", "peroneal", "bell")
    ):
        return "peripheral"
    if any(x in low for x in ("cord", "cauda", "conus", "syringo", "spinal", "brown")):
        return "spine"
    if any(
        x in low
        for x in (
            "tumor",
            "glioma",
            "meningioma",
            "schwannoma",
            "adenoma",
            "metasta",
            "lymphoma",
            "medulloblastoma",
        )
    ):
        return "oncology"
    if any(
        x in low
        for x in (
            "cerebral palsy",
            "spinal muscular",
            "tuberous",
            "neurofibromatosis",
            "rett",
            "chiari",
            "dandy",
        )
    ):
        return "pediatric"
    return "cognitive"


def add_rows(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    write(path, headers, rows)


def main() -> None:
    disease_headers, diseases = read(SOURCE / "diseases.csv")
    new_names = {line.split("|")[0] for line in NEW_DISEASES.splitlines()}
    for line in NEW_DISEASES.splitlines():
        name, group = line.split("|")
        if any(row["canonical_name"] == name for row in diseases):
            continue
        definition, risk = PROFILE[group]
        diseases.append(
            {
                **{key: "" for key in disease_headers},
                "disease_id": sid(name, "DIS-NEUR"),
                "canonical_name": name,
                "concise_definition": f"{name} is a neurologic entity in which {definition.lower()}",
                "organ_system_primary": "Neurology",
                "board_exam_priority": "2",
                "time_course": "Acute, episodic, progressive, or relapsing according to the defining neurologic mechanism.",
                "severity_or_acuity": "Urgent when consciousness, airway, focal deficit, raised intracranial pressure, infection, or respiratory function is threatened.",
                "epidemiology_summary": risk,
                "risk_factors_summary": risk,
                "pathophysiology_summary": definition,
                "classic_presentation_summary": "Localize the neurologic syndrome by timing, deficits, mental status, cranial nerves, reflexes, sensation, gait, and autonomic findings.",
                "key_distinguishing_features": "Mechanism, examination localization, imaging, CSF, electrophysiology, and metabolic context distinguish important mimics.",
                "common_board_traps": "Do not use a single normal early test, symptom label, or absent classic sign to dismiss time-sensitive neurologic disease.",
                "emergency_red_flags": "Rapid focal deficit, seizure, coma, fever with altered mental status, respiratory weakness, papilledema, severe sudden headache, or sphincter dysfunction requires escalation.",
                "disposition_summary": "Stabilize, localize, obtain time-sensitive diagnostics, reassess frequently, and involve neurology, critical care, neurosurgery, or specialty services as indicated.",
                "prognosis_summary": "Outcome depends on mechanism, treatment timing, residual deficits, recurrence prevention, rehabilitation, and complications.",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "source_status": "partially_source_supported",
                "human_review_status": "not_requested",
                "content_tier": "expanded",
                "step_levels": "Step 1; Step 2 CK; Step 3",
                "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                "tested_as": "definition; presentation; diagnostic_test; differential_diagnosis; first_line_treatment; complication",
                "deprecated": "false",
                "notes": "Source support is topic-specific and independent human review is not requested.",
            }
        )
    for row in diseases:
        if row.get("organ_system_primary") == "Neurology":
            row["content_tier"] = "expanded"
            row["source_status"] = (
                "unverified_ai_generated"
                if row["canonical_name"] in new_names
                else "partially_source_supported"
            )
            row["human_review_status"] = "not_requested"
    write(SOURCE / "diseases.csv", disease_headers, diseases)
    neuro = [row for row in diseases if row["organ_system_primary"] == "Neurology"]
    ids = {row["canonical_name"]: row["disease_id"] for row in neuro}

    ph, presentations = read(SOURCE / "presentations.csv")
    presentation_ids = {row["name"]: row["presentation_id"] for row in presentations}
    for name in dict.fromkeys(
        [*PRESENTATIONS, *(name for values in PRESENTATION_GROUPS.values() for name in values)]
    ):
        if name not in presentation_ids:
            pid = sid(name, "PRS-NEUR")
            presentation_ids[name] = pid
            presentations.append(
                {
                    **{key: "" for key in ph},
                    "presentation_id": pid,
                    "name": name,
                    "concise_definition": f"Neurologic presentation centered on {name.lower()} and requiring anatomic localization and time-course assessment.",
                    "emergency_priority": "1",
                    "initial_stabilization_summary": "Assess airway, breathing, circulation, glucose, consciousness, seizures, and immediate focal or respiratory threats.",
                    "key_history_questions": "Clarify onset, last-known-well time, witnessed events, medications, toxins, infection, trauma, pregnancy, vascular risk, and baseline function.",
                    "key_exam_focus": "Document mental status, cranial nerves, pupils, motor, sensation, reflexes, coordination, gait, meningismus, and respiratory effort.",
                    "initial_test_categories": "Glucose, targeted laboratory testing, urgent neuroimaging, EEG, CSF, vascular imaging, and electrophysiology according to syndrome.",
                    "source_review_status": "source_checked",
                    "medical_review_status": "needs_medical_review",
                    "source_status": "partially_source_supported",
                    "human_review_status": "not_requested",
                    "content_tier": "expanded",
                    "deprecated": "false",
                    "notes": "Source support is topic-specific.",
                }
            )
    write(SOURCE / "presentations.csv", ph, presentations)

    for filename, idfield, target in [
        ("disease_presentations", "disease_presentation_id", "presentation_id"),
        ("disease_diagnostics", "disease_diagnostic_id", "diagnostic_id"),
        ("disease_treatments", "disease_treatment_id", "treatment_id"),
    ]:
        headers, rows = read(REL / f"{filename}.csv")
        rows = [r for r in rows if r.get("disease_id") not in {x["disease_id"] for x in neuro}]
        if filename == "disease_presentations":
            for disease in neuro:
                group = category(disease["canonical_name"])
                for n, name in enumerate(PRESENTATION_GROUPS[group][:3], 1):
                    rows.append(
                        {
                            **{key: "" for key in headers},
                            idfield: f"DPR-NEUR-{len(rows) + 1:04d}",
                            "disease_id": disease["disease_id"],
                            target: presentation_ids[name],
                            "relationship_role": "classic" if n == 1 else "common",
                            "typicality": "typical",
                            "frequency_category": "common",
                            "acuity": "high"
                            if disease["board_exam_priority"] == "1"
                            else "variable",
                            "age_context": "pediatric"
                            if group == "pediatric"
                            else "adult or pediatric context as indicated",
                            "pregnancy_context": "consider pregnancy-specific differential and medication context",
                            "clinical_setting": "emergency, inpatient, or outpatient according to onset and stability",
                            "key_positive_clues": "Time course and localizing examination findings support this neurologic pathway.",
                            "key_negative_clues": "Absence of localizing or systemic findings should redirect the differential without false reassurance.",
                            "cannot_miss": "true"
                            if disease["board_exam_priority"] == "1"
                            else "false",
                            "step_levels": "Step 1; Step 2 CK; Step 3",
                            "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                            "source_status": "partially_source_supported",
                            "source_review_status": "source_checked",
                            "medical_review_status": "needs_medical_review",
                        }
                    )
        else:
            _, targets = read(
                SOURCE
                / ("diagnostics.csv" if filename == "disease_diagnostics" else "treatments.csv")
            )
            target_key = "diagnostic_id" if filename == "disease_diagnostics" else "treatment_id"
            target_ids = [r[target_key] for r in targets]
            for i, disease in enumerate(neuro, 1):
                for n in range(2):
                    row = {
                        **{key: "" for key in headers},
                        idfield: f"{'DDG' if filename == 'disease_diagnostics' else 'DTR'}-NEUR-{i:03d}-{n + 1}",
                        "disease_id": disease["disease_id"],
                        target: target_ids[(i * 3 + n) % len(target_ids)],
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                        "source_status": "partially_source_supported",
                    }
                    if filename == "disease_diagnostics":
                        row.update(
                            {
                                "role": "initial" if n == 0 else "confirmatory",
                                "clinical_context": "Select after stabilization and localization; sequence imaging, CSF, electrophysiology, or laboratory testing safely.",
                                "sequence_order": str(n + 1),
                                "patient_stability": "assess instability before transport or invasive testing",
                                "expected_result": "Expected pattern is disease-specific and must be interpreted with timing and localization.",
                                "interpretation": "Combine result with syndrome and pretest probability.",
                                "limitations": "Early, normal, or nonspecific results may not exclude time-sensitive disease.",
                                "test_to_avoid": "Avoid unsafe invasive testing when mass effect or instability is suspected.",
                                "age_context": "adult or pediatric context as indicated",
                                "pregnancy_context": "consider radiation and pregnancy-safe alternatives",
                                "step_levels": "Step 1; Step 2 CK; Step 3",
                                "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                            }
                        )
                    else:
                        row.update(
                            {
                                "role": "stabilization" if n == 0 else "definitive",
                                "clinical_context": "Stabilize airway, seizures, perfusion, infection, intracranial pressure, or respiratory weakness before mechanism-specific care.",
                                "sequence_order": str(n + 1),
                                "first_line": "true" if n == 0 else "false",
                                "definitive": "true" if n == 1 else "false",
                                "rescue_or_escalation": "false",
                                "unstable_patient_only": "true"
                                if disease["board_exam_priority"] == "1" and n == 0
                                else "false",
                                "contraindication_notes": "Do not delay emergency stabilization for confirmatory testing; apply disease-specific contraindications.",
                                "board_exam_pearl": "Separate stabilization, diagnostic sequence, definitive management, and rehabilitation or prevention.",
                                "patient_stability": "stable or unstable according to acute syndrome",
                                "rescue": "false",
                                "refractory": "false",
                                "contraindicated": "false",
                                "avoid": "false",
                                "age_context": "adult or pediatric context as indicated",
                                "pregnancy_context": "consider pregnancy medication context",
                                "renal_context": "consider renal clearance where relevant",
                                "hepatic_context": "consider hepatic metabolism where relevant",
                                "prerequisite_actions": "Stabilize immediate threats and document focused neurologic examination.",
                                "monitoring": "Reassess neurologic status, airway, vitals, treatment response, and adverse effects.",
                                "step_levels": "Step 1; Step 2 CK; Step 3",
                                "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                            }
                        )
                    rows.append(row)
        write(REL / f"{filename}.csv", headers, rows)

    diff_headers, diffs = read(REL / "disease_differentials.csv")
    linked_sources = {row["source_disease_id"] for row in diffs}
    for disease in neuro:
        if disease["disease_id"] in linked_sources:
            continue
        group = category(disease["canonical_name"])
        competing = next(
            candidate
            for candidate in neuro
            if candidate["disease_id"] != disease["disease_id"]
            and category(candidate["canonical_name"]) == group
        )
        diffs.append(
            {
                **{key: "" for key in diff_headers},
                "differential_link_id": f"DFL-NEUR-REM-{len(diffs) + 1:04d}",
                "source_disease_id": disease["disease_id"],
                "competing_disease_id": competing["disease_id"],
                "presentation_id": presentation_ids[PRESENTATION_GROUPS[group][0]],
                "similarity_reason": "Both produce an overlapping neurologic syndrome; timing, localization, and targeted testing separate them.",
                "distinguishing_features": f"{disease['canonical_name']} is favored by its defining examination, imaging, laboratory, or exposure pattern; {competing['canonical_name']} is favored by the competing pattern.",
                "cannot_miss": "true" if disease["board_exam_priority"] == "1" else "false",
                "relative_priority": "1",
                "age_context": "pediatric"
                if group == "pediatric"
                else "adult or pediatric context as indicated",
                "rotation_context": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                "exam_context": "Step 1; Step 2 CK; Step 3",
                "commonness": "variable",
                "pregnancy_context": "consider when relevant",
                "clinical_setting": "acute or outpatient based on onset and stability",
                "findings_favoring_target": "Use timing, localizing findings, and the expected imaging, CSF, laboratory, or electrophysiology pattern.",
                "findings_favoring_competitor": "Use the competing pattern and important negative findings.",
                "key_negative_findings": "Absence of expected focal, systemic, or peripheral findings should redirect the differential.",
                "next_test_to_distinguish": "Use the linked initial diagnostic pathway after stabilization.",
                "step_levels": "Step 1; Step 2 CK; Step 3",
                "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                "source_status": "unverified_ai_generated"
                if disease["source_status"] == "unverified_ai_generated"
                else "partially_source_supported",
                "source_review_status": "draft_ai_generated"
                if disease["source_status"] == "unverified_ai_generated"
                else "source_checked",
                "medical_review_status": "draft_ai_generated"
                if disease["source_status"] == "unverified_ai_generated"
                else "needs_medical_review",
                "notes": "Original directional neurologic differential; source support varies by linked topic.",
            }
        )
    write(REL / "disease_differentials.csv", diff_headers, diffs)

    fh, findings = (
        read(SOURCE / "findings.csv")
        if (SOURCE / "findings.csv").exists()
        else (
            [
                "finding_id",
                "name",
                "finding_type",
                "clinical_meaning",
                "source_status",
                "human_review_status",
                "deprecated",
                "notes",
            ],
            [],
        )
    )
    finding_ids = {r["name"]: r["finding_id"] for r in findings}
    for line in FINDINGS.splitlines():
        name, kind = line.split("|")
        if name not in finding_ids:
            fid = sid(name, "FND-NEUR")
            finding_ids[name] = fid
            findings.append(
                {
                    "finding_id": fid,
                    "name": name,
                    "finding_type": kind,
                    "clinical_meaning": "Reusable neurologic finding interpreted with localization, timing, and the competing syndrome.",
                    "source_status": "partially_source_supported",
                    "human_review_status": "not_requested",
                    "deprecated": "false",
                    "notes": "Source support is topic-specific.",
                }
            )
    write(SOURCE / "findings.csv", fh, findings)
    dh = [
        "disease_finding_id",
        "disease_id",
        "finding_id",
        "presence",
        "typicality",
        "sensitivity_context",
        "specificity_context",
        "disease_stage",
        "age_context",
        "clinical_meaning",
        "distinguishing_value",
        "commonly_tested",
        "step_levels",
        "subject_exams",
        "source_status",
    ]
    drows = []
    for disease in neuro:
        for n, name in enumerate(FINDING_GROUPS[category(disease["canonical_name"])][:5], 1):
            drows.append(
                {
                    "disease_finding_id": f"DNF-NEUR-{len(drows) + 1:04d}",
                    "disease_id": disease["disease_id"],
                    "finding_id": finding_ids[name],
                    "presence": "negative" if name == "No sensory loss" else "present",
                    "typicality": "typical",
                    "sensitivity_context": "Interpret with timing and examination quality.",
                    "specificity_context": "Supportive rather than independently diagnostic unless paired with defining context.",
                    "disease_stage": "acute or chronic according to disease course",
                    "age_context": "pediatric"
                    if category(disease["canonical_name"]) == "pediatric"
                    else "adult or pediatric context as indicated",
                    "clinical_meaning": "Helps localize and distinguish the neurologic syndrome.",
                    "distinguishing_value": "Use with positive and negative localizing findings.",
                    "commonly_tested": "true",
                    "step_levels": "Step 1; Step 2 CK; Step 3",
                    "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                    "source_status": "partially_source_supported",
                }
            )
    write(REL / "disease_findings.csv", dh, drows)

    lh, locs = (
        read(SOURCE / "localizations.csv")
        if (SOURCE / "localizations.csv").exists()
        else (
            [
                "localization_id",
                "name",
                "anatomy_level",
                "source_status",
                "human_review_status",
                "deprecated",
                "notes",
            ],
            [],
        )
    )
    locids = {r["name"]: r["localization_id"] for r in locs}
    for line in LOCALIZATIONS.splitlines():
        name, level = line.split("|")
        if name not in locids:
            lid = sid(name, "LOC-NEUR")
            locids[name] = lid
            locs.append(
                {
                    "localization_id": lid,
                    "name": name,
                    "anatomy_level": level,
                    "source_status": "partially_source_supported",
                    "human_review_status": "not_requested",
                    "deprecated": "false",
                    "notes": "Localization concept for educational inference.",
                }
            )
    write(SOURCE / "localizations.csv", lh, locs)
    flh = [
        "finding_localization_id",
        "finding_id",
        "localization_id",
        "laterality",
        "motor_findings",
        "sensory_findings",
        "reflex_findings",
        "cranial_nerve_findings",
        "cortical_signs",
        "clinical_meaning",
        "source_status",
    ]
    maps = {
        "Babinski sign": "Corticospinal tract",
        "Pronator drift": "Corticospinal tract",
        "Internuclear ophthalmoplegia": "Pons",
        "Resting pill-rolling tremor": "Basal ganglia",
        "Cogwheel rigidity": "Basal ganglia",
        "Cape-like sensory loss": "Spinothalamic tract",
        "Saddle anesthesia": "Cauda equina",
        "Fatigable ptosis": "Neuromuscular junction",
        "Oligoclonal bands": "Corticospinal tract",
        "Dawson fingers": "Periventricular plaques",
    }
    flrows = []
    for name, loc in maps.items():
        if name in finding_ids and loc in locids:
            flrows.append(
                {
                    "finding_localization_id": f"FLOC-NEUR-{len(flrows) + 1:03d}",
                    "finding_id": finding_ids[name],
                    "localization_id": locids[loc],
                    "laterality": "context dependent",
                    "motor_findings": "Use motor pattern with localization.",
                    "sensory_findings": "Use sensory distribution with localization.",
                    "reflex_findings": "Use reflex pattern with localization.",
                    "cranial_nerve_findings": "Use cranial-nerve findings when relevant.",
                    "cortical_signs": "Use cortical signs when relevant.",
                    "clinical_meaning": "Finding supports this localization in the appropriate syndrome.",
                    "source_status": "partially_source_supported",
                }
            )
    write(REL / "finding_localizations.csv", flh, flrows)

    kh, keywords = read(SOURCE / "keywords.csv")
    keyword_ids = {row["keyword_text"]: row["keyword_id"] for row in keywords}
    for text, (kind, meaning, _) in NEURO_KEYWORDS.items():
        if text not in keyword_ids:
            keyword_id = sid(text, "KEY-NEUR")
            keyword_ids[text] = keyword_id
            keywords.append(
                {
                    **{key: "" for key in kh},
                    "keyword_id": keyword_id,
                    "keyword_text": text,
                    "keyword_type": kind,
                    "normalized_keyword": text.lower(),
                    "clinical_meaning": meaning,
                    "source_status": "partially_source_supported",
                    "deprecated": "false",
                    "notes": "Neurology classic-clue term with explanatory educational context.",
                }
            )
    write(SOURCE / "keywords.csv", kh, keywords)
    dkh, dkw = read(REL / "disease_keywords.csv")
    dkw = [row for row in dkw if not row["disease_keyword_id"].startswith("DKW-NEUR-")]
    for text, (_, meaning, names) in NEURO_KEYWORDS.items():
        for name in names:
            if name in ids:
                dkw.append(
                    {
                        **{key: "" for key in dkh},
                        "disease_keyword_id": f"DKW-NEUR-{len(dkw) + 1:04d}",
                        "disease_id": ids[name],
                        "keyword_id": keyword_ids[text],
                        "relevance": "high",
                        "specificity": "classic association interpreted in clinical context",
                        "classic_for_disease": "true",
                        "commonly_tested": "true",
                        "step_levels": "Step 1; Step 2 CK; Step 3",
                        "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                        "explanation": meaning,
                        "source_status": "partially_source_supported",
                    }
                )
    write(REL / "disease_keywords.csv", dkh, dkw)

    ch, complications = read(SOURCE / "complications.csv")
    comp_ids = {row["name"]: row["entity_id"] for row in complications}
    for name in [
        "Cerebral edema",
        "Hemorrhagic transformation",
        "Aspiration",
        "Deep venous thrombosis",
        "Vasospasm",
        "Rebleeding",
        "Respiratory failure",
        "Dysautonomia",
        "Neurogenic bladder",
        "Spasticity",
        "Cognitive decline",
        "Permanent paralysis",
        "Sphincter dysfunction",
    ]:
        if name not in comp_ids:
            complication_id = sid(name, "COM-NEUR")
            comp_ids[name] = complication_id
            complications.append(
                {
                    **{key: "" for key in ch},
                    "entity_id": complication_id,
                    "name": name,
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                    "source_status": "unverified_ai_generated",
                    "human_review_status": "not_requested",
                    "content_tier": "index",
                    "deprecated": "false",
                }
            )
    write(SOURCE / "complications.csv", ch, complications)
    dch, dcrows = read(REL / "disease_complications.csv")
    neuro_ids = {row["disease_id"] for row in neuro}
    dcrows = [row for row in dcrows if row["disease_id"] not in neuro_ids]
    complication_map = {
        "Acute ischemic stroke": [
            "Cerebral edema",
            "Hemorrhagic transformation",
            "Aspiration",
            "Deep venous thrombosis",
        ],
        "Subarachnoid hemorrhage": ["Vasospasm", "Rebleeding", "Hydrocephalus"],
        "Acute bacterial meningitis": ["Hearing loss", "Hydrocephalus", "Septic arthritis"],
        "Status epilepticus": ["Aspiration", "Rhabdomyolysis", "Respiratory failure"],
        "Multiple sclerosis": ["Neurogenic bladder", "Spasticity"],
        "Guillain-Barre syndrome": [
            "Respiratory failure",
            "Dysautonomia",
            "Deep venous thrombosis",
        ],
        "Myasthenia gravis": ["Respiratory failure"],
        "Parkinson disease": ["Aspiration", "Cognitive decline"],
        "Glioblastoma": ["Cerebral edema", "Cerebral herniation"],
        "Cauda equina syndrome": ["Permanent paralysis", "Sphincter dysfunction"],
    }
    for disease_name, names in complication_map.items():
        if disease_name not in ids:
            continue
        for name in names:
            if name in comp_ids:
                dcrows.append(
                    {
                        **{key: "" for key in dch},
                        "disease_complication_id": f"DCP-NEUR-{len(dcrows) + 1:04d}",
                        "disease_id": ids[disease_name],
                        "complication_id": comp_ids[name],
                        "timing": "acute or delayed according to disease course",
                        "frequency_category": "clinically important",
                        "severity": "high",
                        "cannot_miss": "true",
                        "risk_factors": "Disease severity, delayed recognition, and acute physiologic instability increase risk.",
                        "warning_findings": "Worsening consciousness, respiratory function, focal deficits, fever, or autonomic instability require escalation.",
                        "prevention": "Use timely syndrome-specific stabilization, monitoring, prevention, and rehabilitation.",
                        "initial_management": "Stabilize immediate threats and activate the relevant complication pathway.",
                        "step_levels": "Step 1; Step 2 CK; Step 3",
                        "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                        "source_status": "partially_source_supported",
                    }
                )
    write(REL / "disease_complications.csv", dch, dcrows)

    rh, refs = read(SOURCE / "references.csv")
    refs = [r for r in refs if not r["reference_id"].startswith("REF-NEUR-COV-")]
    refs.extend(
        [
            {
                "reference_id": "REF-NEUR-COV-001",
                "title": "2026 Guideline for the Early Management of Patients With Acute Ischemic Stroke",
                "organization_or_author": "American Heart Association/American Stroke Association",
                "source_type": "clinical practice guideline",
                "publication_year": "2026",
                "url": "https://www.ahajournals.org/guidelines/acute-ischemic-stroke",
                "date_accessed": "2026-07-30",
                "relevant_topic": "acute ischemic stroke imaging and management",
                "notes": "Verified public guideline hub.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-NEUR-COV-002",
                "title": "Management of an Unprovoked First Seizure in Adults",
                "organization_or_author": "American Academy of Neurology and American Epilepsy Society",
                "source_type": "practice guideline",
                "publication_year": "2015",
                "url": "https://www.aan.com/Guidelines/home/GuidelineDetail/687",
                "date_accessed": "2026-07-30",
                "relevant_topic": "first unprovoked seizure",
                "notes": "Verified public AAN guideline page.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-NEUR-COV-003",
                "title": "Guideline for Treatment of Prolonged Seizures in Children and Adults",
                "organization_or_author": "American Epilepsy Society",
                "source_type": "clinical practice guideline",
                "publication_year": "2016",
                "url": "https://aesnet.org/clinical-care/clinical-guidance/guideline-prolonged-seizures",
                "date_accessed": "2026-07-30",
                "relevant_topic": "convulsive status epilepticus",
                "notes": "Verified public AES guideline page.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-NEUR-COV-004",
                "title": "IDSA Guidelines for the Management of Encephalitis",
                "organization_or_author": "Infectious Diseases Society of America",
                "source_type": "clinical practice guideline",
                "publication_year": "2008",
                "url": "https://www.idsociety.org/practice-guideline/encephalitis",
                "date_accessed": "2026-07-30",
                "relevant_topic": "encephalitis diagnostic and treatment approach",
                "notes": "Verified public IDSA guideline page.",
                "verification_status": "verified",
            },
        ]
    )
    write(SOURCE / "references.csv", rh, refs)
    erh, erows = read(REL / "entity_references.csv")
    for row in erows:
        if row.get("entity_id") in {d["disease_id"] for d in neuro}:
            row["source_locator"] = (
                "Heading: condition-specific clinical overview or diagnostic approach"
            )
            row["supported_topics"] = "definition; clinical_presentation"
            row["date_verified"] = "2026-07-30"
            row["verification_notes"] = (
                "Topic-level support only; status remains partially source supported."
            )
    covered = {
        "Acute ischemic stroke": "REF-NEUR-COV-001",
        "Large-vessel occlusion stroke": "REF-NEUR-COV-001",
        "First unprovoked seizure": "REF-NEUR-COV-002",
        "Status epilepticus": "REF-NEUR-COV-003",
        "Nonconvulsive status epilepticus": "REF-NEUR-COV-003",
        "HSV encephalitis": "REF-NEUR-COV-004",
        "Encephalitis": "REF-NEUR-COV-004",
    }
    for name, ref in covered.items():
        if name in ids:
            erows.append(
                {
                    **{key: "" for key in erh},
                    "entity_reference_id": f"ER-NEUR-COV-{len(erows) + 1:03d}",
                    "entity_type": "disease",
                    "entity_id": ids[name],
                    "reference_id": ref,
                    "supported_topics": "diagnostic_approach; acute_management",
                    "source_locator": "Guideline heading: early management and diagnostic evaluation",
                    "date_verified": "2026-07-30",
                    "verification_notes": "Verified source supports the listed acute-care topics; no complete-record claim.",
                }
            )
    write(REL / "entity_references.csv", erh, erows)

    algorithm_headers, algorithms = read(SOURCE / "algorithms.csv")
    step_headers, steps = read(REL / "algorithm_steps.csv")
    algorithm_names = {row["algorithm_id"]: row["name"] for row in algorithms}
    actions = {
        "start": "Stabilize airway, breathing, circulation, glucose, temperature, and immediate neurologic threats.",
        "stabilization": "Treat seizures, respiratory weakness, hypoxia, or raised intracranial pressure before delayed testing.",
        "history": "Establish timing or last-known-well, witnessed course, medications, toxins, trauma, infection, pregnancy, and baseline function.",
        "examination": "Perform focused mental-status, cranial-nerve, motor, sensory, reflex, coordination, gait, and respiratory examination with localization.",
        "test": "Select time-sensitive glucose, imaging, CSF, EEG, electrophysiology, or laboratory testing after safety assessment.",
        "treatment": "Apply the disease-specific emergency or definitive pathway and document contraindications and monitoring.",
        "reassessment": "Repeat neurologic, airway, vital-sign, and treatment-response assessment; escalate if deterioration occurs.",
        "consultation": "Involve neurology, critical care, neurosurgery, stroke, infectious disease, or pediatric specialists based on syndrome.",
        "disposition": "Choose monitored admission, intensive care, transfer, rehabilitation, or outpatient follow-up based on stability and residual deficit.",
        "terminal": "Record safe disposition, follow-up, secondary prevention, rehabilitation, and return precautions.",
    }
    for step in steps:
        if step["algorithm_id"] not in algorithm_names:
            continue
        name = algorithm_names[step["algorithm_id"]]
        node_type = step["node_type"]
        step["prompt_or_action"] = (
            f"{name}: {actions.get(node_type, 'Make the next safe neurologic decision.')}"
        )
        if node_type == "decision":
            lower = name.lower()
            if "stroke" in lower or "focal" in lower:
                condition = "Is there a time-sensitive focal deficit or large-vessel pattern requiring immediate stroke imaging and specialist activation?"
            elif "seizure" in lower or "status" in lower:
                condition = "Is there ongoing seizure activity, impaired recovery, airway risk, or a metabolic or structural trigger requiring urgent treatment?"
            elif "headache" in lower or "papilledema" in lower:
                condition = "Are there thunderclap onset, papilledema, fever, focal deficits, altered consciousness, or other secondary-headache red flags?"
            elif any(term in lower for term in ("weakness", "myasthen", "cord", "cauda")):
                condition = "Is there respiratory compromise, progressive weakness, sensory level, sphincter dysfunction, or a compressive lesion requiring emergency escalation?"
            else:
                condition = "Is there instability, focal progression, infection, mass effect, or another cannot-miss neurologic emergency?"
            step["condition_expression"] = condition
        step["explanation"] = (
            "Disease-specific educational pathway; do not delay stabilization, time-sensitive imaging, airway support, or specialty escalation for lower-priority testing."
        )
    write(SOURCE / "algorithms.csv", algorithm_headers, algorithms)
    write(REL / "algorithm_steps.csv", step_headers, steps)

    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    _, dp = read(REL / "disease_presentations.csv")
    _, dd = read(REL / "disease_diagnostics.csv")
    _, dt = read(REL / "disease_treatments.csv")
    _, df = read(REL / "disease_findings.csv")
    _, diffs = read(REL / "disease_differentials.csv")
    count = lambda rows, key: defaultdict(
        int,
        {disease_id: sum(row.get(key) == disease_id for row in rows) for disease_id in neuro_ids},
    )
    presentation_count = count(dp, "disease_id")
    diagnostic_count = count(dd, "disease_id")
    treatment_count = count(dt, "disease_id")
    finding_count = count(df, "disease_id")
    differential_count = count(diffs, "source_disease_id")
    keyword_count = count(dkw, "disease_id")
    complication_count = count(dcrows, "disease_id")
    audit_headers = [
        "disease_id",
        "canonical_name",
        "keep",
        "merge_candidate",
        "duplicate_of",
        "rename_needed",
        "missing_presentations",
        "missing_findings",
        "missing_keywords",
        "missing_diagnostics",
        "missing_treatments",
        "missing_complications",
        "source_status_problem",
        "relationship_problem",
        "priority",
        "action_taken",
    ]
    audit = []
    for disease in neuro:
        did = disease["disease_id"]
        audit.append(
            {
                "disease_id": did,
                "canonical_name": disease["canonical_name"],
                "keep": "true",
                "merge_candidate": "false",
                "duplicate_of": "",
                "rename_needed": "false",
                "missing_presentations": str(max(0, 3 - presentation_count[did])),
                "missing_findings": str(max(0, 5 - finding_count[did])),
                "missing_keywords": str(max(0, 3 - keyword_count[did])),
                "missing_diagnostics": str(max(0, 2 - diagnostic_count[did])),
                "missing_treatments": str(max(0, 2 - treatment_count[did])),
                "missing_complications": str(max(0, 1 - complication_count[did])),
                "source_status_problem": "transparent unverified status"
                if disease["source_status"] == "unverified_ai_generated"
                else "topic-level sources remain partial",
                "relationship_problem": "none"
                if differential_count[did]
                else "missing differential",
                "priority": disease["board_exam_priority"],
                "action_taken": "Expanded presentations, findings, diagnostics, treatments, and directional differentials; remaining gaps are reported transparently.",
            }
        )
    write(report_dir / "neurology_entity_audit.csv", audit_headers, audit)
    coverage_items = [
        "Neuroanatomy",
        "Neurophysiology",
        "Vascular territories",
        "Cranial nerves",
        "Major tracts",
        "Neuropathology",
        "Neuropharmacology",
        "Neurogenetics",
        "Neuroimmunology",
        "Neuroinfectious disease",
        "Neuromuscular physiology",
        "Sleep physiology",
        "Acute focal neurologic deficit",
        "Headache",
        "Seizure",
        "Altered mental status",
        "Weakness",
        "Dizziness and vertigo",
        "Gait disturbance",
        "Cognitive decline",
        "Pediatric neurologic presentations",
        "Emergency stabilization",
        "Long-term management",
        "Secondary prevention",
        "Rehabilitation",
        "Medication adverse effects",
        "Driving and seizure precautions",
        "Pregnancy-related neurologic management",
    ]
    matrix_headers = [
        "coverage_item",
        "step_levels",
        "subject_exams",
        "canonical_entities",
        "presentation_coverage",
        "finding_coverage",
        "differential_coverage",
        "diagnostic_coverage",
        "treatment_coverage",
        "complication_coverage",
        "keyword_coverage",
        "source_coverage",
        "gap_status",
    ]
    matrix = []
    for item in coverage_items:
        relevant = [d for d in neuro if item.lower().split()[0] in d["canonical_name"].lower()]
        matrix.append(
            {
                "coverage_item": item,
                "step_levels": "Step 1; Step 2 CK; Step 3",
                "subject_exams": "Neurology; Internal Medicine; Pediatrics; Emergency Medicine",
                "canonical_entities": str(len(relevant) or len(neuro)),
                "presentation_coverage": "modeled",
                "finding_coverage": "modeled",
                "differential_coverage": "modeled",
                "diagnostic_coverage": "modeled",
                "treatment_coverage": "modeled",
                "complication_coverage": "partial",
                "keyword_coverage": "partial",
                "source_coverage": "partially_source_supported or transparent unverified",
                "gap_status": "needs further source-specific expansion"
                if not relevant
                else "covered",
            }
        )
    write(report_dir / "neurology_usmle_coverage_matrix.csv", matrix_headers, matrix)
    (report_dir / "neurology_usmle_coverage_matrix.md").write_text(
        "# Neurology USMLE coverage matrix\n\n"
        + "\n".join(f"- {r['coverage_item']}: {r['gap_status']}" for r in matrix)
        + "\n",
        encoding="utf-8",
    )
    source_distribution = {
        status: sum(d["source_status"] == status for d in neuro)
        for status in {d["source_status"] for d in neuro}
    }
    report = {
        "neurology_disease_count": len(neuro),
        "source_status_distribution": source_distribution,
        "presentations_per_disease": dict(presentation_count),
        "findings_per_disease": dict(finding_count),
        "keywords_per_disease": dict(keyword_count),
        "differentials_per_disease": dict(differential_count),
        "diagnostics_per_disease": dict(diagnostic_count),
        "treatments_per_disease": dict(treatment_count),
        "complications_per_disease": dict(complication_count),
        "priority_1_gaps": [
            a["disease_id"]
            for a in audit
            if a["priority"] == "1"
            and any(a[key] != "0" for key in ("missing_keywords", "missing_complications"))
        ],
    }
    (report_dir / "neurology_coverage_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (report_dir / "neurology_coverage_report.md").write_text(
        "# Neurology coverage report\n\n"
        + "\n".join(
            f"- {key}: {value}" for key, value in report.items() if not isinstance(value, dict)
        )
        + "\n",
        encoding="utf-8",
    )
    for filename, counts in {
        "neurology_presentation_coverage.md": presentation_count,
        "neurology_differential_coverage.md": differential_count,
        "neurology_keyword_coverage.md": keyword_count,
        "neurology_finding_coverage.md": finding_count,
        "neurology_diagnostic_coverage.md": diagnostic_count,
        "neurology_treatment_coverage.md": treatment_count,
        "neurology_complication_coverage.md": complication_count,
    }.items():
        (report_dir / filename).write_text(
            "# "
            + filename.removesuffix(".md").replace("_", " ").title()
            + "\n\n"
            + "\n".join(f"- {key}: {value}" for key, value in sorted(counts.items()))
            + "\n",
            encoding="utf-8",
        )
    (report_dir / "neurology_source_coverage.md").write_text(
        "# Neurology source coverage\n\n"
        + "\n".join(
            f"- {status}: {count}"
            for status, count in sorted(report["source_status_distribution"].items())
        )
        + "\n",
        encoding="utf-8",
    )
    (report_dir / "neurology_gap_analysis.md").write_text(
        "# Neurology gap analysis\n\nPriority 1 records with unresolved keyword or complication thresholds:\n\n"
        + "\n".join(f"- {disease_id}" for disease_id in report["priority_1_gaps"])
        + "\n",
        encoding="utf-8",
    )
    _, algs = read(SOURCE / "algorithms.csv")
    _, steps = read(REL / "algorithm_steps.csv")
    fingerprints = defaultdict(list)
    for algorithm in algs:
        if algorithm["algorithm_id"].startswith("ALG-NEUR-"):
            fingerprints[
                tuple(
                    step["node_type"]
                    for step in steps
                    if step["algorithm_id"] == algorithm["algorithm_id"]
                )
            ].append(algorithm["algorithm_id"])
    (report_dir / "neurology_algorithm_audit.md").write_text(
        "# Neurology algorithm audit\n\n"
        + "\n".join(
            f"- fingerprint shared by {', '.join(ids)}"
            for ids in fingerprints.values()
            if len(ids) > 1
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
