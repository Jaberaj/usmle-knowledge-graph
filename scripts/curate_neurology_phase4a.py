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
            f"{row['canonical_name']} has its own mechanism, time course, and localizing pattern in the Phase 4A curation.",
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
            if "source_review_status" in row:
                row["source_review_status"] = "draft_ai_generated"
            if filename == "disease_presentations":
                row["key_positive_clues"] = presentation_hints.get(label, fact)
                row["key_negative_clues"] = (
                    f"For {label}, absence of the characteristic pattern described here requires active evaluation of the documented alternatives."
                )
            elif filename == "disease_keywords":
                row["explanation"] = (
                    f"{fact} In this record, '{label}' is used for the stated clinical association and not as a parent-syndrome label."
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
                    f"{fact} {label} is used at the clinically appropriate stage of this presentation."
                )
                row["expected_result"] = (
                    f"{label} supplies the result that confirms, excludes, or characterizes the specific pathology described for this disease."
                )
                row["interpretation"] = fact
                row["limitations"] = (
                    f"Availability, timing, and technical quality limit {label}; the limitation is considered before delaying the urgent care named in this record."
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
                    f"New signs of {label} during this illness require urgent reassessment because {fact}"
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
                "source_review_status": "draft_ai_generated",
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
        "Transient negative focal deficit": "A transient negative focal deficit that has resolved by examination is the defining TIA clinical clue.",
        "Recurrent unprovoked seizures": "Recurrent unprovoked seizures define epilepsy rather than an isolated provoked event.",
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
    fh, findings = read(SOURCE / "findings.csv")
    for finding in findings:
        if finding["finding_id"].startswith("FND-NEUR-P4A-"):
            finding["source_status"] = "unverified_ai_generated"
            finding["human_review_status"] = "not_requested"
    fids = {row["name"]: row["finding_id"] for row in findings}
    # Each high-priority record has an owned, discriminating finding.  These are
    # deliberately named observations, not a shared "seizure" or "stroke" filler.
    finding_additions = {
        "Leg-predominant weakness": "Contralateral leg-predominant weakness localizes to ACA territory.",
        "Bilateral motor loss below the lesion": "Abrupt bilateral weakness below a spinal level supports anterior spinal cord ischemia.",
        "Sudden loss of postural tone": "Abrupt loss of tone producing a head drop or fall is an atonic seizure clue.",
        "Quadriparesis with preserved consciousness": "Quadriparesis with preserved awareness and vertical eye movements suggests ventral pontine injury.",
        "Multiterritory cortical infarcts": "Infarcts in more than one arterial territory support an embolic source.",
        "Partial Horner syndrome": "Ipsilateral ptosis and miosis without anhidrosis support carotid dissection.",
        "Carotid bruit": "A carotid bruit supports turbulent flow from carotid stenosis but does not establish its severity.",
        "Limb ataxia": "Limb dysmetria and gait ataxia support cerebellar involvement.",
        "No identified stroke mechanism after standard evaluation": "Cryptogenic stroke remains after a standard vascular, cardiac, and rhythm evaluation is unrevealing.",
        "Prolonged febrile seizures in infancy": "Prolonged recurrent fever-associated seizures beginning in infancy are a high-yield Dravet syndrome clue.",
        "Fever-associated generalized convulsion": "A generalized convulsion with fever in the appropriate age range supports febrile seizure after CNS infection is considered.",
        "Unprovoked seizure": "An unprovoked event is distinguished from acute symptomatic seizure by evaluation for immediate provoking causes.",
        "Preserved awareness during focal event": "Preserved awareness during a stereotyped focal motor, sensory, autonomic, or psychic event supports focal aware seizure.",
        "Focal onset before bilateral convulsions": "An aura or unilateral focal onset before bilateral convulsions supports focal-to-bilateral tonic-clonic seizure.",
        "Deep basal ganglia hemorrhage": "Deep hemorrhage in basal ganglia, thalamus, pons, or cerebellum supports chronic hypertensive arteriopathy.",
        "Intracerebral blood": "Acute hyperdense blood within brain parenchyma establishes intracerebral hemorrhage on noncontrast CT.",
        "Intraventricular blood": "Hyperdense blood within the ventricular system indicates intraventricular hemorrhage or extension.",
        "Morning myoclonic jerks": "Brief bilateral myoclonic jerks shortly after awakening support juvenile myoclonic epilepsy.",
        "Pure motor stroke": "Isolated contralateral weakness without cortical signs supports a pure motor lacunar syndrome.",
        "Slow spike-and-wave": "Slow generalized spike-and-wave with multiple seizure types supports Lennox-Gastaut syndrome.",
        "Brief shock-like jerks": "Sudden brief shock-like movements without a prolonged postictal state support myoclonic seizure.",
        "Eyes closed during event": "Persistently closed eyes during a variable prolonged event favors psychogenic nonepileptic seizures over convulsive epilepsy.",
        "Failure to recover between seizures": "Failure to regain baseline consciousness between seizures defines an emergency status pattern.",
        "Transient focal neurologic deficit": "A resolved negative focal neurologic deficit is the defining clinical event of transient ischemic attack.",
        "Stepwise cognitive decline": "Stepwise loss of cognition with focal deficits supports vascular dementia.",
        "Occipital neck pain after cervical trauma": "Occipital neck pain after minor cervical trauma supports vertebral artery dissection.",
        "Puff-of-smoke collaterals": "Fragile basal collateral vessels on angiography support moyamoya disease.",
        "Automatisms with impaired awareness": "Behavioral arrest with impaired awareness and oral or manual automatisms supports focal impaired-awareness seizure.",
        "Deja vu aura": "A stereotyped déjà vu aura supports mesial temporal focal seizure onset.",
    }
    for index, (name, meaning) in enumerate(finding_additions.items(), 1):
        if name in fids:
            continue
        ident = f"FND-NEUR-P4A-{index:03d}"
        fids[name] = ident
        findings.append(
            {key: "" for key in fh}
            | {
                "finding_id": ident,
                "name": name,
                "clinical_meaning": meaning,
                "source_status": "unverified_ai_generated",
                "human_review_status": "not_requested",
                "deprecated": "false",
                "notes": "Explicit Phase-4A vascular or epilepsy finding.",
            }
        )
    write(SOURCE / "findings.csv", fh, findings)
    dkh, keyword_links = read(REL / "disease_keywords.csv")
    dfh, finding_links = read(REL / "disease_findings.csv")
    keyword_links = [
        row for row in keyword_links if not row["disease_keyword_id"].startswith("DKW-P4A-")
    ]
    finding_links = [
        row for row in finding_links if not row["disease_finding_id"].startswith("DNF-P4A-")
    ]
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
    priority_findings = {
        "Anterior cerebral artery syndrome": "Leg-predominant weakness",
        "Anterior spinal artery syndrome": "Bilateral motor loss below the lesion",
        "Atonic seizure": "Sudden loss of postural tone",
        "Basilar artery syndrome": "Quadriparesis with preserved consciousness",
        "Cardioembolic stroke": "Multiterritory cortical infarcts",
        "Carotid artery dissection": "Partial Horner syndrome",
        "Carotid artery stenosis": "Carotid bruit",
        "Cerebellar stroke": "Limb ataxia",
        "Cryptogenic stroke": "No identified stroke mechanism after standard evaluation",
        "Dravet syndrome": "Prolonged febrile seizures in infancy",
        "Febrile seizure": "Fever-associated generalized convulsion",
        "First unprovoked seizure": "Unprovoked seizure",
        "Focal aware seizure": "Preserved awareness during focal event",
        "Focal impaired-awareness seizure": "Automatisms with impaired awareness",
        "Focal to bilateral tonic-clonic seizure": "Focal onset before bilateral convulsions",
        "Generalized tonic-clonic seizure": "Lateral tongue biting",
        "Hypertensive cerebral hemorrhage": "Deep basal ganglia hemorrhage",
        "Intracerebral hemorrhage": "Intracerebral blood",
        "Intraventricular hemorrhage": "Intraventricular blood",
        "Juvenile myoclonic epilepsy": "Morning myoclonic jerks",
        "Lacunar stroke": "Pure motor stroke",
        "Large-vessel occlusion stroke": "Hyperdense MCA sign",
        "Lennox-Gastaut syndrome": "Slow spike-and-wave",
        "Middle cerebral artery syndrome": "Aphasia",
        "Moyamoya disease": "Puff-of-smoke collaterals",
        "Myoclonic seizure": "Brief shock-like jerks",
        "Nonconvulsive status epilepticus": "Altered mental status",
        "Posterior cerebral artery syndrome": "Visual field deficit",
        "Psychogenic nonepileptic seizures": "Eyes closed during event",
        "Seizure disorder": "Seizure",
        "Status epilepticus": "Failure to recover between seizures",
        "Temporal-lobe epilepsy": "Deja vu aura",
        "Transient ischemic attack": "Transient focal neurologic deficit",
        "Vascular dementia": "Stepwise cognitive decline",
        "Vertebral artery dissection": "Occipital neck pain after cervical trauma",
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
    for disease, clue in priority_findings.items():
        if disease not in seizure_ids or clue not in fids:
            continue
        if any(row["disease_id"] == seizure_ids[disease] for row in finding_links):
            continue
        finding_links.append(
            {key: "" for key in dfh}
            | {
                "disease_finding_id": f"DNF-P4A-{seizure_ids[disease]}-{fids[clue]}",
                "disease_id": seizure_ids[disease],
                "finding_id": fids[clue],
                "presence": "present",
                "typicality": "classic",
                "clinical_meaning": FACTS.get(disease, finding_additions.get(clue, clue)),
                "distinguishing_value": f"{clue} is an owned discriminating finding for {disease}.",
                "commonly_tested": "true",
                "step_levels": "Step 1; Step 2 CK; Step 3",
                "subject_exams": "Neurology; Emergency Medicine",
                "source_status": "unverified_ai_generated",
                "source_review_status": "draft_ai_generated",
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
    tia_id = seizure_ids.get("Transient ischemic attack")
    inappropriate_tia_keywords = {
        keyword_ids.get(clue)
        for clue in (
            "Diffusion restriction",
            "Hyperdense MCA sign",
            "Crossed neurologic findings",
            "Pure motor stroke",
            "Lateral medullary syndrome",
        )
    }
    keyword_links = [
        row
        for row in keyword_links
        if not (row["disease_id"] == tia_id and row["keyword_id"] in inappropriate_tia_keywords)
    ]
    ownership = {
        "Seizure disorder": "Recurrent unprovoked seizures",
        "Transient ischemic attack": "Transient negative focal deficit",
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
    # Shared compatibility rule: unverified generated records never retain the
    # legacy source-checked marker, including records outside this content scope.
    for filename in (
        "disease_presentations",
        "disease_findings",
        "disease_keywords",
        "disease_diagnostics",
        "disease_treatments",
        "disease_differentials",
        "disease_complications",
    ):
        path = REL / f"{filename}.csv"
        fields, rows = read(path)
        for row in rows:
            if (
                row.get("source_status") == "unverified_ai_generated"
                and row.get("source_review_status") == "source_checked"
            ):
                row["source_review_status"] = "draft_ai_generated"
        write(path, fields, rows)
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
