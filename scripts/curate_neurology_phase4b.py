"""Explicit Phase 4B curation for headache, CNS infection, and inflammation."""

from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"
CURATION = ROOT / "data" / "curation" / "neurology"
MODULES = ("headache.yaml", "infection.yaml", "demyelinating.yaml")

FACTS = {
    "Migraine without aura": "Recurrent attacks of pulsatile disabling headache with nausea and photo- or phonophobia occur without a preceding focal aura.",
    "Migraine with aura": "Gradually spreading positive visual, sensory, or language symptoms that evolve over minutes and may precede headache support migraine aura rather than abrupt negative TIA symptoms.",
    "Hemiplegic migraine": "Reversible unilateral motor weakness evolving with migraine aura requires exclusion of acute stroke at a first or atypical presentation.",
    "Cluster headache": "Short attacks of severe unilateral orbital or temporal pain with ipsilateral lacrimation, nasal congestion, and restlessness define a trigeminal autonomic cephalalgia.",
    "Trigeminal neuralgia": "Brief electric shock-like unilateral facial pain triggered by light touch, chewing, or brushing teeth follows a trigeminal distribution.",
    "Intracranial hypotension": "Orthostatic headache that improves when supine after CSF loss is typical of spontaneous intracranial hypotension.",
    "Post-dural-puncture headache": "A positional headache after neuraxial puncture reflects persistent CSF leakage and may require epidural blood patch when conservative measures fail.",
    "Medication-overuse headache": "Frequent use of acute analgesic or migraine medication can perpetuate chronic daily headache and requires withdrawal planning.",
    "Tension-type headache": "Bilateral pressing or tightening headache without prominent nausea or focal neurologic findings supports tension-type headache.",
    "Vestibular migraine": "Episodic vertigo with migrainous features and no fixed focal vestibular deficit supports vestibular migraine.",
    "Chronic migraine": "Headache on at least fifteen days each month with migrainous features on a subset requires attention to medication overuse and prevention.",
    "Occipital neuralgia": "Paroxysmal stabbing pain in the occipital nerve distribution with local tenderness or trigger points supports occipital neuralgia.",
    "Glossopharyngeal neuralgia": "Brief electric pain in the throat, tonsillar fossa, or deep ear triggered by swallowing or coughing supports glossopharyngeal neuralgia.",
    "Meningitis": "Headache, fever, neck stiffness, and photophobia raise concern for meningeal inflammation; altered consciousness or focal deficit changes testing sequence.",
    "Posterior reversible encephalopathy syndrome": "Acute hypertension, eclampsia, renal disease, or immunosuppression with seizures and posterior vasogenic edema supports PRES.",
    "Acute bacterial meningitis": "Acute fever, meningismus, and altered mental status with neutrophilic CSF, high protein, and low glucose require immediate empiric antimicrobial therapy.",
    "Viral meningitis": "Headache, fever, and lymphocytic CSF with relatively preserved glucose favor viral meningitis after bacterial disease is addressed.",
    "Tuberculous meningitis": "Subacute basilar meningitis with cranial neuropathies, lymphocytic CSF, high protein, and low glucose suggests tuberculous meningitis.",
    "Cryptococcal meningitis": "Subacute headache in advanced immunocompromise with markedly elevated opening pressure and cryptococcal antigen requires antifungal treatment and pressure control.",
    "Encephalitis": "Altered behavior or consciousness with seizures or focal deficits reflects brain parenchymal inflammation and requires urgent infectious and autoimmune evaluation.",
    "HSV encephalitis": "Fever, behavioral change, focal seizures, and temporal-lobe MRI abnormality support HSV encephalitis; acyclovir begins before PCR confirmation.",
    "Brain abscess": "A ring-enhancing lesion with central diffusion restriction and systemic or contiguous infection suggests brain abscess; routine lumbar puncture can be unsafe and low yield.",
    "Neurosyphilis": "Subacute cognitive, psychiatric, tabetic, or meningovascular neurologic disease with reactive CSF serology supports neurosyphilis.",
    "Progressive multifocal leukoencephalopathy": "Progressive focal deficits in severe cellular immunosuppression with nonenhancing white-matter lesions and JC-virus evidence support PML.",
    "Acute disseminated encephalomyelitis": "Multifocal deficits and encephalopathy after infection, often in children, with widespread demyelinating lesions support ADEM.",
    "Autoimmune encephalitis": "Subacute memory or behavioral change, seizures, dyskinesias, or autonomic instability requires paired infectious exclusion and neural-antibody evaluation.",
    "Anti-NMDA receptor encephalitis": "Psychiatric symptoms followed by dyskinesias, seizures, autonomic instability, or hypoventilation suggest anti-NMDA receptor encephalitis and prompt tumor search.",
    "Wernicke encephalopathy": "Confusion, gait ataxia, and ocular motor dysfunction in malnutrition require immediate parenteral thiamine before glucose.",
    "Meningioma": "A slowly progressive focal deficit or seizure with a dural-based enhancing lesion suggests meningioma rather than CNS infection.",
    "Hepatic encephalopathy": "Fluctuating attention and asterixis in liver failure support hepatic encephalopathy as a toxic-metabolic encephalopathy mimic.",
    "Hyponatremic encephalopathy": "Acute symptomatic hyponatremia can cause seizure or encephalopathy and requires controlled correction to avoid osmotic demyelination.",
    "Neuroborreliosis": "Painful radiculopathy, facial palsy, or aseptic meningitis with compatible exposure and intrathecal antibody evidence supports neuroborreliosis.",
    "Rabies encephalitis": "Encephalitis with hydrophobia, aerophobia, and autonomic instability after a mammal exposure is a public-health emergency.",
    "Multiple sclerosis": "Dissemination of CNS deficits in time and space with typical periventricular lesions, Dawson fingers, or CSF oligoclonal bands supports multiple sclerosis.",
    "Neuromyelitis optica spectrum disorder": "Severe optic neuritis, longitudinally extensive myelitis, or area-postrema syndrome with aquaporin-4 antibody supports NMOSD.",
    "MOG antibody-associated disease": "Optic neuritis, myelitis, or ADEM-like disease with serum MOG antibody, often bilateral optic neuritis in children, supports MOG-associated disease.",
    "Transverse myelitis": "Subacute bilateral motor, sensory, and autonomic deficits with a spinal sensory level require urgent MRI to exclude compression before inflammatory treatment.",
    "Optic neuritis": "Painful monocular visual loss with an afferent pupillary defect and impaired color vision supports optic neuritis.",
    "Chronic inflammatory demyelinating polyneuropathy": "Progressive or relapsing symmetric weakness and sensory loss beyond eight weeks with areflexia suggests CIDP rather than acute GBS.",
    "Amyotrophic lateral sclerosis": "Combined upper- and lower-motor-neuron signs without sensory loss support ALS, an important motor-predominant mimic of inflammatory neuropathy.",
    "Tuberous sclerosis": "Cortical tubers, seizures, and multisystem hamartomas suggest tuberous sclerosis rather than acquired CNS inflammation.",
    "Osmotic demyelination syndrome": "Delayed dysarthria, dysphagia, quadriparesis, or altered consciousness after overly rapid correction of chronic hyponatremia suggests osmotic demyelination.",
    "Acute flaccid myelitis": "Acute asymmetric flaccid limb weakness with anterior-horn-cell spinal MRI abnormalities, often after viral illness, supports acute flaccid myelitis.",
}


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write(path: Path, fields: list[str], data: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    diseases = read(SOURCE / "diseases.csv")[1]
    module_names = {
        item["canonical_name"]
        for filename in MODULES
        for item in yaml.safe_load((CURATION / filename).read_text(encoding="utf-8"))
    }
    targets = {
        row["disease_id"]: FACTS[row["canonical_name"]]
        for row in diseases
        if row["canonical_name"] in module_names
    }
    names = {row["disease_id"]: row["canonical_name"] for row in diseases}
    catalogues = {
        "disease_presentations": ("presentations.csv", "presentation_id", "name"),
        "disease_findings": ("findings.csv", "finding_id", "name"),
        "disease_keywords": ("keywords.csv", "keyword_id", "keyword_text"),
        "disease_diagnostics": ("diagnostics.csv", "diagnostic_id", "name"),
        "disease_treatments": ("treatments.csv", "treatment_id", "name"),
        "disease_complications": ("complications.csv", "entity_id", "name"),
    }
    for relation, (catalogue, entity_id, label_field) in catalogues.items():
        fields, data = read(REL / f"{relation}.csv")
        labels = {row[entity_id]: row[label_field] for row in read(SOURCE / catalogue)[1]}
        foreign = "complication_id" if relation == "disease_complications" else entity_id
        for row in data:
            if row["disease_id"] not in targets:
                continue
            fact, label = targets[row["disease_id"]], labels[row[foreign]]
            row["source_status"] = "unverified_ai_generated"
            if "source_review_status" in row:
                row["source_review_status"] = "draft_ai_generated"
            if relation == "disease_presentations":
                row["key_positive_clues"] = (
                    f"{fact} The linked presentation '{label}' is clinically meaningful only in that stated pattern."
                )
                row["key_negative_clues"] = (
                    f"For {names[row['disease_id']]}, absence of the defining pattern above redirects evaluation to its documented alternatives."
                )
            elif relation == "disease_findings":
                row["clinical_meaning"] = (
                    f"{fact} Here, '{label}' is interpreted as an explicit disease-level finding."
                )
                row["distinguishing_value"] = (
                    f"'{label}' helps distinguish {names[row['disease_id']]} from the named mimics when interpreted with onset and examination."
                )
            elif relation == "disease_keywords":
                row["explanation"] = (
                    f"{fact} '{label}' is retained only for this stated clinical association."
                )
            elif relation == "disease_diagnostics":
                row["clinical_context"] = (
                    f"{fact} '{label}' has a defined role in this disease rather than serving as routine screening."
                )
                row["expected_result"] = (
                    f"For {names[row['disease_id']]}, '{label}' is assessed for the characteristic result described in the illness script above."
                )
                row["interpretation"] = fact
                row["limitations"] = (
                    f"Timing, technical quality, and the disease-specific pretest probability limit '{label}'; urgent treatment is not delayed when indicated."
                )
            elif relation == "disease_treatments":
                row["clinical_context"] = (
                    f"{fact} '{label}' is assigned to acute stabilization, disease-directed treatment, prevention, or escalation as appropriate."
                )
                row["board_exam_pearl"] = (
                    f"For {names[row['disease_id']]}, the timing and contraindications of '{label}' follow this illness script, not a generic treatment sequence."
                )
            else:
                row["risk_factors"] = (
                    f"{fact} Risk of '{label}' depends on the identified mechanism and severity."
                )
                row["warning_findings"] = (
                    f"New evidence of '{label}' requires reassessment in the specific clinical context of {names[row['disease_id']]}."
                )
        write(REL / f"{relation}.csv", fields, data)
    fields, data = read(REL / "disease_differentials.csv")
    for row in data:
        did = row["source_disease_id"]
        if did not in targets:
            continue
        disease, competitor, fact = (
            names[did],
            names.get(row["competing_disease_id"], "the competing diagnosis"),
            targets[did],
        )
        row.update(
            {
                "similarity_reason": f"{disease} and {competitor} can both produce the linked neurologic presentation.",
                "distinguishing_features": f"{fact} {competitor} is favored by its own characteristic tempo, examination findings, and targeted testing.",
                "findings_favoring_target": fact,
                "findings_favoring_competitor": f"Findings characteristic of {competitor}, rather than the pattern stated for {disease}, favor the competitor.",
                "key_negative_findings": f"Absence of the defining {disease} pattern warrants active evaluation for {competitor}.",
                "next_test_to_distinguish": "Choose urgent neuroimaging for focal or pressure features, CSF studies when safe for suspected infection/inflammation, and targeted serology or electrophysiology when indicated.",
                "exam_context": "explicit Phase-4B comparison",
                "source_status": "unverified_ai_generated",
                "source_review_status": "draft_ai_generated",
            }
        )
    write(REL / "disease_differentials.csv", fields, data)
    # Remove inherited emergency-red-flag keywords from primary headache diseases.
    _, keywords = read(SOURCE / "keywords.csv")
    keyword_ids = {row["keyword_text"]: row["keyword_id"] for row in keywords}
    headache_clues = {
        "Migraine without aura": "Photophobia with nausea",
        "Migraine with aura": "Gradually spreading positive aura",
        "Hemiplegic migraine": "Reversible unilateral weakness with aura",
        "Cluster headache": "Unilateral autonomic headache with restlessness",
        "Trigeminal neuralgia": "Touch-triggered electric facial pain",
        "Tension-type headache": "Bilateral pressing headache",
        "Vestibular migraine": "Episodic vertigo with migrainous features",
        "Chronic migraine": "Headache on fifteen or more days monthly",
        "Occipital neuralgia": "Occipital nerve trigger-point pain",
        "Glossopharyngeal neuralgia": "Swallowing-triggered throat pain",
        "Progressive multifocal leukoencephalopathy": "JC virus in advanced immunocompromise",
        "Osmotic demyelination syndrome": "Rapid correction of chronic hyponatremia",
    }
    keyword_fields, keyword_rows = read(SOURCE / "keywords.csv")
    for index, (disease, clue) in enumerate(headache_clues.items(), 1):
        if clue in keyword_ids:
            continue
        identifier = f"KEY-NEUR-P4B-{index:03d}"
        keyword_ids[clue] = identifier
        keyword_rows.append(
            {field: "" for field in keyword_fields}
            | {
                "keyword_id": identifier,
                "keyword_text": clue,
                "keyword_type": "classic_clue",
                "normalized_keyword": clue.lower(),
                "clinical_meaning": FACTS[disease],
                "source_status": "unverified_ai_generated",
                "deprecated": "false",
                "notes": "Explicit Phase-4B headache clue.",
            }
        )
    write(SOURCE / "keywords.csv", keyword_fields, keyword_rows)
    red_flags = {
        keyword_ids.get(name)
        for name in ("Worst headache of life", "Thunderclap headache", "Sentinel headache")
    }
    fields, data = read(REL / "disease_keywords.csv")
    primary_headache = {
        did
        for did, fact in targets.items()
        if names[did]
        in {
            "Migraine without aura",
            "Migraine with aura",
            "Hemiplegic migraine",
            "Cluster headache",
            "Tension-type headache",
            "Vestibular migraine",
            "Chronic migraine",
            "Trigeminal neuralgia",
            "Occipital neuralgia",
            "Glossopharyngeal neuralgia",
        }
    }
    data = [
        row
        for row in data
        if not (row["disease_id"] in primary_headache and row["keyword_id"] in red_flags)
    ]
    data = [row for row in data if not row["disease_keyword_id"].startswith("DKW-P4B-")]
    for disease, clue in headache_clues.items():
        did = next(identifier for identifier, name in names.items() if name == disease)
        data.append(
            {field: "" for field in fields}
            | {
                "disease_keyword_id": f"DKW-P4B-{did}-{keyword_ids[clue]}",
                "disease_id": did,
                "keyword_id": keyword_ids[clue],
                "relevance": "high",
                "specificity": "classic disease clue",
                "classic_for_disease": "true",
                "commonly_tested": "true",
                "step_levels": "Step 1; Step 2 CK; Step 3",
                "subject_exams": "Neurology; Emergency Medicine",
                "explanation": FACTS[disease],
                "source_status": "unverified_ai_generated",
            }
        )
    write(REL / "disease_keywords.csv", fields, data)
    # Make the post-dural-puncture rescue relationship explicit rather than
    # expecting a general headache-treatment record to imply a blood patch.
    treatment_fields, treatment_rows = read(SOURCE / "treatments.csv")
    treatment_id = "TRT-NEUR-P4B-001"
    if not any(row["treatment_id"] == treatment_id for row in treatment_rows):
        treatment_rows.append(
            {field: "" for field in treatment_fields}
            | {
                "treatment_id": treatment_id,
                "name": "Epidural blood patch",
                "treatment_type": "procedure",
                "treatment_category": "rescue",
                "general_description": "Autologous epidural blood seals a persistent dural CSF leak after dural puncture.",
                "mechanism_summary": "Restores CSF pressure by sealing the leak.",
                "major_contraindications": "Active infection, uncorrected coagulopathy, or refusal require reassessment.",
                "monitoring_summary": "Reassess positional pain and new neurologic symptoms after the procedure.",
                "emergency_role": "Not a substitute for evaluating fever, focal deficit, or other secondary-headache red flags.",
                "source_status": "unverified_ai_generated",
                "source_review_status": "draft_ai_generated",
                "medical_review_status": "draft_ai_generated",
                "human_review_status": "not_requested",
                "deprecated": "false",
                "content_tier": "disease_specific",
                "notes": "Explicit Phase-4B post-dural-puncture rescue treatment.",
            }
        )
    write(SOURCE / "treatments.csv", treatment_fields, treatment_rows)
    treatment_link_fields, treatment_links = read(REL / "disease_treatments.csv")
    treatment_links = [
        row for row in treatment_links if row["disease_treatment_id"] != "DTR-P4B-PDP-BLOODPATCH"
    ]
    pdp_id = next(
        identifier for identifier, name in names.items() if name == "Post-dural-puncture headache"
    )
    treatment_links.append(
        {field: "" for field in treatment_link_fields}
        | {
            "disease_treatment_id": "DTR-P4B-PDP-BLOODPATCH",
            "disease_id": pdp_id,
            "treatment_id": treatment_id,
            "role": "rescue",
            "clinical_context": FACTS["Post-dural-puncture headache"],
            "sequence_order": "after conservative treatment when symptoms persist or are disabling",
            "rescue_or_escalation": "true",
            "board_exam_pearl": "Persistent post-dural-puncture headache can improve with epidural blood patch after unsafe secondary causes are assessed.",
            "source_status": "unverified_ai_generated",
            "source_review_status": "draft_ai_generated",
            "medical_review_status": "draft_ai_generated",
            "patient_stability": "stable after red-flag assessment",
            "step_levels": "Step 1; Step 2 CK; Step 3",
            "subject_exams": "Neurology; Anesthesiology; Emergency Medicine",
        }
    )
    write(REL / "disease_treatments.csv", treatment_link_fields, treatment_links)


if __name__ == "__main__":
    main()
