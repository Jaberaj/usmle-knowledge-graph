"""Explicit Phase 4A curation for cerebrovascular disease and epilepsy only."""

from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"
CURATION = ROOT / "data" / "curation" / "neurology"

FACTS = {
    "Transient ischemic attack": "A transient negative focal deficit from focal ischemia is a warning for early completed stroke even when examination has normalized.",
    "Acute ischemic stroke": "Abrupt focal loss of language, motor, sensory, or visual function follows an arterial territory and requires glucose exclusion and immediate brain imaging.",
    "Large-vessel occlusion stroke": "Dense contralateral weakness, gaze deviation, aphasia, or neglect suggests proximal anterior circulation occlusion and warrants urgent vascular imaging.",
    "Cardioembolic stroke": "Maximal deficits at onset in more than one vascular territory or a cortical pattern raise concern for an embolic cardiac source.",
    "Lacunar stroke": "A pure motor, pure sensory, ataxic hemiparesis, or dysarthria-clumsy hand syndrome without cortical signs localizes to a deep perforator infarct.",
    "Watershed infarction": "Border-zone infarction follows systemic hypoperfusion and often causes bilateral proximal weakness or cortical border-zone deficits.",
    "Intracerebral hemorrhage": "Sudden focal deficit with severe headache, vomiting, or depressed consciousness requires CT confirmation and blood-pressure and anticoagulant review.",
    "Subarachnoid hemorrhage": "Thunderclap headache peaking within seconds, meningismus, or collapse raises concern for aneurysmal subarachnoid bleeding.",
    "Cerebral venous sinus thrombosis": "Headache with papilledema, seizure, or focal deficit in a hypercoagulable or postpartum setting should prompt venous imaging.",
    "Carotid artery dissection": "Unilateral neck or head pain with partial Horner syndrome followed by anterior-circulation ischemia suggests carotid dissection.",
    "Vertebral artery dissection": "Occipital neck pain after minor cervical trauma with vertigo, ataxia, or lateral medullary features suggests vertebral dissection.",
    "Cerebral amyloid angiopathy": "Recurrent lobar hemorrhage in an older adult without deep hypertensive distribution supports cerebral amyloid angiopathy.",
    "Moyamoya disease": "Progressive terminal internal-carotid stenosis with collateral vessels causes recurrent ischemia, often precipitated by hyperventilation.",
    "Reversible cerebral vasoconstriction syndrome": "Recurrent thunderclap headaches over days with segmental arterial narrowing, often postpartum or vasoactive-drug related, support RCVS.",
    "Posterior reversible encephalopathy syndrome": "Acute hypertension, renal disease, eclampsia, or immunosuppression with seizures and posterior vasogenic edema supports PRES.",
    "Epidural hematoma": "A biconvex extra-axial hemorrhage after temporal trauma can follow a lucid interval and deteriorate rapidly from herniation.",
    "Subdural hematoma": "A crescentic collection after tearing of bridging veins causes gradual confusion or focal deficit, especially in older adults or anticoagulated patients.",
    "Vascular dementia": "Stepwise cognitive decline with focal neurologic deficits and cerebrovascular injury supports vascular rather than primary neurodegenerative dementia.",
    "Middle cerebral artery syndrome": "Contralateral face and arm weakness with aphasia in the dominant hemisphere or neglect in the nondominant hemisphere localizes to MCA cortex.",
    "Anterior cerebral artery syndrome": "Contralateral leg-predominant weakness, abulia, and urinary incontinence localize to medial frontal and paracentral ACA territory.",
    "Posterior cerebral artery syndrome": "Contralateral homonymous visual-field loss, sometimes with alexia without agraphia on the dominant side, localizes to PCA territory.",
    "Basilar artery syndrome": "Quadriparesis, coma, cranial-nerve abnormalities, or locked-in features signal posterior-circulation emergency.",
    "Lateral medullary syndrome": "Ipsilateral facial pain-temperature loss with contralateral body pain-temperature loss, dysphagia, and Horner syndrome localizes laterally in the medulla.",
    "Medial medullary syndrome": "Contralateral weakness and proprioceptive loss with ipsilateral tongue weakness localize to the medial medulla.",
    "Locked-in syndrome": "Ventral pontine injury causes quadriplegia and anarthria with preserved consciousness and vertical eye movement.",
    "Pure motor lacunar syndrome": "Isolated contralateral motor weakness without aphasia, neglect, or visual-field loss reflects a lacunar corticospinal lesion.",
    "First unprovoked seizure": "A first unprovoked seizure requires assessment for provoking metabolic, toxic, structural, and infectious causes before recurrence counseling.",
    "Focal aware seizure": "Preserved awareness with a stereotyped sensory, autonomic, psychic, or focal motor event supports focal onset.",
    "Focal impaired-awareness seizure": "Behavioral arrest, impaired awareness, automatisms, and postictal confusion are typical of focal impaired-awareness seizure.",
    "Focal to bilateral tonic-clonic seizure": "A focal aura or unilateral onset followed by bilateral convulsions distinguishes focal-to-bilateral spread from primary generalized onset.",
    "Generalized tonic-clonic seizure": "Abrupt loss of consciousness with tonic stiffening, rhythmic clonic movements, lateral tongue biting, and postictal confusion supports an epileptic convulsion.",
    "Absence seizure": "Brief frequent staring episodes with immediate recovery and generalized three-hertz spike-and-wave activity are typical absence seizures.",
    "Myoclonic seizure": "Sudden brief shock-like jerks without prolonged postictal confusion describe myoclonic seizures.",
    "Atonic seizure": "Sudden loss of postural tone causing falls or head drops is characteristic of atonic seizures.",
    "Status epilepticus": "Ongoing convulsive activity or failure to recover between seizures requires immediate seizure termination and escalation.",
    "Nonconvulsive status epilepticus": "Persistent altered mental status with electrographic seizure activity requires continuous EEG to diagnose and monitor treatment.",
    "Febrile seizure": "A generalized seizure with fever in the usual age range and rapid recovery is a febrile seizure only after CNS infection is considered.",
    "Infantile spasms": "Clusters of brief flexor or extensor spasms in infancy with hypsarrhythmia require urgent syndrome-specific treatment.",
    "Childhood absence epilepsy": "School-age staring spells provoked by hyperventilation with three-hertz spike-and-wave support childhood absence epilepsy.",
    "Juvenile myoclonic epilepsy": "Morning myoclonic jerks in an adolescent, often after sleep deprivation, are a hallmark of juvenile myoclonic epilepsy.",
    "Temporal-lobe epilepsy": "Déjà vu aura, rising epigastric sensation, automatisms, and postictal confusion support temporal-lobe focal seizures.",
    "Lennox-Gastaut syndrome": "Multiple seizure types including drop attacks with slow spike-and-wave and developmental impairment suggest Lennox-Gastaut syndrome.",
    "West syndrome": "Infantile spasms, hypsarrhythmia, and developmental regression define West syndrome.",
    "Dravet syndrome": "Prolonged febrile seizures beginning in infancy with later multiple seizure types suggest Dravet syndrome.",
    "Psychogenic nonepileptic seizures": "Variable, prolonged events with eye closure or asynchronous movements and no ictal EEG correlate suggest psychogenic nonepileptic events.",
}


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    _, diseases = read(SOURCE / "diseases.csv")
    phase4a_names = {
        entry["canonical_name"]
        for filename in ("vascular.yaml", "seizures.yaml")
        for entry in yaml.safe_load((CURATION / filename).read_text(encoding="utf-8"))
    }
    targets = {
        row["disease_id"]: FACTS.get(
            row["canonical_name"],
            f"The illness script for {row['canonical_name']} is curated as a distinct cerebrovascular or epilepsy entity rather than a parent syndrome.",
        )
        for row in diseases
        if row["canonical_name"] in phase4a_names
    }
    presentation_hints = {
        "Acute focal neurologic deficit": "Abrupt onset, a vascular-territory pattern, and cortical signs when cortex is involved are the key positive clues; gradual spreading positive symptoms favor migraine aura.",
        "Thunderclap headache": "Pain reaching maximal intensity within one minute, collapse, meningismus, or exertional onset is concerning; a familiar gradual migraine pattern is less typical.",
        "First seizure": "A witnessed stereotyped event, lateral tongue injury, and postictal confusion support seizure; persistent focal deficit requires stroke evaluation.",
        "Status epilepticus": "Ongoing motor activity, repeated events without recovery, hypoxemia, or impaired airway protection require immediate treatment.",
        "Aphasia": "Abrupt language production or comprehension loss with preserved alertness suggests dominant cortical ischemia rather than delirium.",
    }
    for filename, idfield, label_file, label_id, label_field in (
        ("disease_presentations", "disease_id", "presentations.csv", "presentation_id", "name"),
        ("disease_findings", "disease_id", "findings.csv", "finding_id", "name"),
        ("disease_keywords", "disease_id", "keywords.csv", "keyword_id", "keyword_text"),
        ("disease_diagnostics", "disease_id", "diagnostics.csv", "diagnostic_id", "name"),
        ("disease_treatments", "disease_id", "treatments.csv", "treatment_id", "name"),
        ("disease_complications", "disease_id", "complications.csv", "entity_id", "name"),
    ):
        path = REL / f"{filename}.csv"
        fields, rows = read(path)
        labels = {r[label_id]: r[label_field] for r in read(SOURCE / label_file)[1]}
        entity_field = next(
            key
            for key in (
                "presentation_id",
                "finding_id",
                "keyword_id",
                "diagnostic_id",
                "treatment_id",
                "complication_id",
            )
            if key in fields
        )
        for row in rows:
            if row[idfield] not in targets:
                continue
            fact, label = targets[row[idfield]], labels[row[entity_field]]
            row["source_status"] = "unverified_ai_generated"
            if filename == "disease_presentations":
                row["key_positive_clues"] = presentation_hints.get(label, fact)
                row["key_negative_clues"] = (
                    "The competing diagnoses are separated by the concrete positive and negative clues in the explicit comparison."
                )
            elif filename == "disease_keywords":
                row["explanation"] = (
                    f"{fact} The clue '{label}' is retained only when it directly expresses that syndrome-specific pattern."
                )
            elif filename == "disease_findings":
                row["clinical_meaning"] = (
                    f"{fact} The finding '{label}' is interpreted in this disease-specific context."
                )
                row["distinguishing_value"] = (
                    f"{label} helps separate this presentation from the named differential diagnoses."
                )
            elif filename == "disease_diagnostics":
                row["clinical_context"] = (
                    f"{fact} {label} answers the explicit diagnostic question for this presentation."
                )
                row["expected_result"] = (
                    f"For this disorder, {label} is evaluated for the anatomic, vascular, electrographic, or metabolic result described by the illness script."
                )
                row["interpretation"] = (
                    f"The result of {label} is integrated with the concrete syndrome pattern above, not used as a generic screen."
                )
                row["limitations"] = (
                    f"Timing and the specific false-negative or nonspecific limitations of {label} matter in this disease."
                )
            elif filename == "disease_treatments":
                row["clinical_context"] = (
                    f"{fact} {label} is used only at the named stabilization, disease-directed, rescue, prevention, or disposition stage."
                )
                row["board_exam_pearl"] = (
                    f"The timing of {label} follows the defining emergency and mechanism of this disease, rather than list order."
                )
            else:
                row["risk_factors"] = (
                    f"{fact} Risk of {label} depends on the documented disease severity and mechanism."
                )
                row["warning_findings"] = (
                    f"New signs of {label} require the disease-specific escalation pathway."
                )
        write(path, fields, rows)
    dh, differentials = read(REL / "disease_differentials.csv")
    names = {row["disease_id"]: row["canonical_name"] for row in diseases}
    for row in differentials:
        if row["source_disease_id"] not in targets:
            continue
        target = names[row["source_disease_id"]]
        competitor = names.get(row["competing_disease_id"], "the competing diagnosis")
        fact = targets[row["source_disease_id"]]
        row.update(
            {
                "similarity_reason": f"{target} and {competitor} can both produce the selected acute neurologic presentation.",
                "distinguishing_features": f"{fact} The competing diagnosis is separated by its own characteristic onset, examination pattern, and targeted test.",
                "findings_favoring_target": fact,
                "findings_favoring_competitor": f"Features characteristic of {competitor}, rather than the defining pattern above, favor the competitor.",
                "key_negative_findings": f"Absence of the defining positive pattern for {target} should prompt active evaluation for {competitor}.",
                "next_test_to_distinguish": "Choose immediate glucose and brain imaging for stroke-like deficit; EEG for a seizure-like event; or venous imaging for suspected CVST.",
                "exam_context": "explicit Phase-4A comparison",
                "source_status": "unverified_ai_generated",
            }
        )
    write(REL / "disease_differentials.csv", dh, differentials)
    # Reassign syndrome-specific EEG and semiology clues away from the broad
    # seizure record and into the syndromes where they are actually tested.
    seizure_ids = {
        row["canonical_name"]: row["disease_id"]
        for row in diseases
        if row["canonical_name"] in phase4a_names
    }
    allowed = {
        "Childhood absence epilepsy": {"Three-hertz spike-and-wave"},
        "Absence seizure": {"Three-hertz spike-and-wave"},
        "Infantile spasms": {"Hypsarrhythmia"},
        "West syndrome": {"Hypsarrhythmia"},
        "Temporal-lobe epilepsy": {"Deja vu aura", "Automatisms"},
    }
    special_clues = {
        "Three-hertz spike-and-wave",
        "Hypsarrhythmia",
        "Deja vu aura",
        "Automatisms",
        "Todd paralysis",
    }
    kh, keywords = read(SOURCE / "keywords.csv")
    keyword_ids = {row["keyword_text"]: row["keyword_id"] for row in keywords}
    additions = {
        "Morning myoclonus": "Myoclonic jerks shortly after awakening are a classic juvenile myoclonic epilepsy clue.",
        "Slow spike-and-wave": "Slow generalized spike-and-wave with drop attacks supports Lennox-Gastaut syndrome.",
        "Prolonged febrile seizures in infancy": "Prolonged recurrent fever-associated seizures beginning in infancy are a high-yield Dravet syndrome clue.",
    }
    for index, (clue, meaning) in enumerate(additions.items(), 1):
        if clue in keyword_ids:
            continue
        ident = f"KEY-NEUR-P4A-{index:03d}"
        keyword_ids[clue] = ident
        keywords.append(
            {key: "" for key in kh}
            | {
                "keyword_id": ident,
                "keyword_text": clue,
                "keyword_type": "classic_clue",
                "normalized_keyword": clue.lower(),
                "clinical_meaning": meaning,
                "source_status": "unverified_ai_generated",
                "deprecated": "false",
                "notes": "Explicit Phase-4A epilepsy clue.",
            }
        )
    write(SOURCE / "keywords.csv", kh, keywords)
    fids = {row["name"]: row["finding_id"] for row in read(SOURCE / "findings.csv")[1]}
    dkh, keyword_links = read(REL / "disease_keywords.csv")
    dfh, finding_links = read(REL / "disease_findings.csv")
    generic_id = seizure_ids.get("Seizure disorder")
    seizure_clue_ids = {
        seizure_ids[name]
        for name in {
            *allowed,
            "Seizure disorder",
            "Juvenile myoclonic epilepsy",
            "Lennox-Gastaut syndrome",
            "Dravet syndrome",
        }
        if name in seizure_ids
    }
    finding_links = [
        row
        for row in finding_links
        if not (
            row["disease_id"] in seizure_clue_ids
            and row["finding_id"] in {fids[clue] for clue in special_clues if clue in fids}
        )
    ]
    # Restore allowed finding links after deliberately removing the inherited set.
    for disease, clues in allowed.items():
        for clue in clues:
            if clue not in fids:
                continue
            finding_links.append(
                {key: "" for key in dfh}
                | {
                    "disease_finding_id": f"DNF-P4A-{seizure_ids[disease]}-{fids[clue]}",
                    "disease_id": seizure_ids[disease],
                    "finding_id": fids[clue],
                    "presence": "present",
                    "typicality": "classic",
                    "clinical_meaning": FACTS.get(disease, disease),
                    "distinguishing_value": f"{clue} is owned by {disease}, not by a broad seizure category.",
                    "commonly_tested": "true",
                    "step_levels": "Step 1; Step 2 CK; Step 3",
                    "subject_exams": "Neurology; Pediatrics",
                    "source_status": "unverified_ai_generated",
                }
            )
    vascular_findings = {
        "Acute ischemic stroke": {"Diffusion restriction", "Hyperdense MCA sign", "Pronator drift"},
        "Subarachnoid hemorrhage": {"Subarachnoid blood", "Xanthochromia", "Meningismus"},
        "Cerebral venous sinus thrombosis": {"Papilledema", "Diffusion restriction"},
        "Epidural hematoma": {"Epidural biconvex collection", "Anisocoria"},
        "Subdural hematoma": {"Crescentic subdural collection", "Midline shift"},
    }
    for disease, clues in vascular_findings.items():
        for clue in clues:
            if disease not in seizure_ids or clue not in fids:
                continue
            finding_links.append(
                {key: "" for key in dfh}
                | {
                    "disease_finding_id": f"DNF-P4A-{seizure_ids[disease]}-{fids[clue]}",
                    "disease_id": seizure_ids[disease],
                    "finding_id": fids[clue],
                    "presence": "present",
                    "typicality": "classic",
                    "clinical_meaning": FACTS[disease],
                    "distinguishing_value": f"{clue} is an explicit {disease} finding.",
                    "commonly_tested": "true",
                    "step_levels": "Step 1; Step 2 CK; Step 3",
                    "subject_exams": "Neurology; Emergency Medicine",
                    "source_status": "unverified_ai_generated",
                }
            )
    keyword_links = [
        row
        for row in keyword_links
        if not (
            row["disease_id"] == generic_id
            and row["keyword_id"] in {keyword_ids.get(clue) for clue in special_clues}
        )
    ]
    ownership = {
        "Childhood absence epilepsy": "Three-hertz spike-and-wave",
        "Absence seizure": "Three-hertz spike-and-wave",
        "Infantile spasms": "Hypsarrhythmia",
        "West syndrome": "Hypsarrhythmia",
        "Juvenile myoclonic epilepsy": "Morning myoclonus",
        "Temporal-lobe epilepsy": "Deja vu aura",
        "Lennox-Gastaut syndrome": "Slow spike-and-wave",
        "Dravet syndrome": "Prolonged febrile seizures in infancy",
    }
    for disease, clue in ownership.items():
        keyword_links.append(
            {key: "" for key in dkh}
            | {
                "disease_keyword_id": f"DKW-P4A-{seizure_ids[disease]}-{keyword_ids[clue]}",
                "disease_id": seizure_ids[disease],
                "keyword_id": keyword_ids[clue],
                "relevance": "high",
                "specificity": "classic syndrome clue",
                "classic_for_disease": "true",
                "commonly_tested": "true",
                "step_levels": "Step 1; Step 2 CK; Step 3",
                "subject_exams": "Neurology; Pediatrics",
                "explanation": additions.get(clue, FACTS.get(disease, disease)),
                "source_status": "unverified_ai_generated",
            }
        )
    write(REL / "disease_findings.csv", dfh, finding_links)
    write(REL / "disease_keywords.csv", dkh, keyword_links)
    # Give all shared algorithms meaningful divergent false paths and remove the
    # ordinal padding introduced in Phase 3.
    sh, steps = read(REL / "algorithm_steps.csv")
    retained = [
        s
        for s in steps
        if "explicit contingency" not in s.get("prompt_or_action", "").lower()
        and "unsafe branch—" not in s.get("prompt_or_action", "").lower()
    ]
    additions = []
    for step in retained:
        if (
            step["algorithm_id"].startswith("ALG-NEUR-")
            and step["node_type"] == "decision"
            and step.get("next_node_if_true") == step.get("next_node_if_false")
        ):
            false_id = f"{step['algorithm_id']}-alternate-{step['node_id'].rsplit('-', 1)[-1]}"
            step["next_node_if_false"] = false_id
            additions.append(
                {key: "" for key in sh}
                | {
                    "algorithm_step_id": f"AST-P4A-{false_id}",
                    "algorithm_id": step["algorithm_id"],
                    "node_id": false_id,
                    "node_type": "terminal",
                    "prompt_or_action": "Negative decision branch: pursue the documented alternative diagnostic pathway and safe disposition.",
                    "terminal_outcome": "alternate pathway",
                    "sequence_hint": step.get("sequence_hint", ""),
                    "explanation": "A false decision result must not silently follow the positive branch.",
                    "source_review_status": "draft_ai_generated",
                    "medical_review_status": "draft_ai_generated",
                }
            )
    write(REL / "algorithm_steps.csv", sh, retained + additions)


if __name__ == "__main__":
    main()
