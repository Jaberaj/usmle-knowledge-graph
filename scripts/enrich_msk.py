"""Deterministically create source-linked musculoskeletal and rheumatology records."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"

GROUPS = {
    "fracture": """Clavicle fracture
Scapular fracture
Proximal humerus fracture
Humeral shaft fracture
Supracondylar humerus fracture
Lateral condyle fracture
Medial epicondyle fracture
Radial head fracture
Olecranon fracture
Monteggia fracture-dislocation
Galeazzi fracture-dislocation
Both-bone forearm fracture
Colles fracture
Smith fracture
Barton fracture
Chauffeur fracture
Scaphoid fracture
Lunate fracture
Hook of hamate fracture
Boxer fracture
Bennett fracture
Rolando fracture
Phalangeal fracture
Femoral neck fracture
Intertrochanteric fracture
Subtrochanteric fracture
Femoral shaft fracture
Patellar fracture
Tibial plateau fracture
Tibial shaft fracture
Tibial stress fracture
Maisonneuve fracture
Pilon fracture
Bimalleolar fracture
Trimalleolar fracture
Jones fracture
Lisfranc injury
Calcaneal fracture
Talar neck fracture
Toddler fracture
Jefferson fracture
Hangman fracture
Odontoid fracture
Burst fracture
Chance fracture
Pelvic ring fracture
Open-book pelvic fracture
Acetabular fracture""",
    "dislocation": """Anterior shoulder dislocation
Posterior shoulder dislocation
Acromioclavicular separation
Sternoclavicular dislocation
Nursemaid elbow
Elbow dislocation
Perilunate dislocation
Lunate dislocation
Posterior hip dislocation
Developmental dysplasia of the hip
Patellar dislocation
Knee dislocation
Ankle dislocation
Temporomandibular joint dislocation""",
    "soft_tissue": """Rotator cuff tendinopathy
Rotator cuff tear
SLAP lesion
Shoulder impingement
Adhesive capsulitis
Pectoralis major rupture
Lateral epicondylitis
Medial epicondylitis
Ulnar collateral ligament injury of elbow
De Quervain tenosynovitis
Trigger finger
Dupuytren contracture
Skier thumb
Scapholunate ligament injury
Triangular fibrocartilage complex injury
Mallet finger
Jersey finger
ACL tear
PCL tear
MCL tear
LCL tear
Medial meniscus tear
Lateral meniscus tear
Patellar tendon rupture
Quadriceps tendon rupture
Patellofemoral pain syndrome
Iliotibial band syndrome
Pes anserine bursitis
Osgood-Schlatter disease
Lateral ankle sprain
Syndesmotic ankle sprain
Achilles tendinopathy
Achilles tendon rupture
Posterior tibial tendon dysfunction
Plantar fasciitis
Turf toe
Morton neuroma
Hallux valgus""",
    "emergency": """Acute compartment syndrome
Chronic exertional compartment syndrome
Open fracture
Necrotizing soft-tissue infection
Acute limb ischemia
Fat embolism syndrome
Traumatic amputation
Flexor tenosynovitis
Hand or digit ischemia
Crush injury""",
    "infection": """Acute hematogenous osteomyelitis
Chronic osteomyelitis
Vertebral osteomyelitis
Diabetic foot osteomyelitis
Prosthetic joint infection
Brodie abscess
Septic arthritis
Gonococcal arthritis
Tuberculous arthritis
Pott disease
Discitis
Infectious bursitis""",
    "degenerative": """Osteoarthritis
Cervical spondylosis
Cervical radiculopathy
Cervical myelopathy
Lumbar spinal stenosis
Lumbar radiculopathy
Herniated nucleus pulposus
Facet arthropathy
Degenerative disc disease
Spondylolysis
Spondylolisthesis
Sacroiliac joint dysfunction
Hip osteoarthritis
Knee osteoarthritis
Hand osteoarthritis""",
    "inflammatory": """Rheumatoid arthritis
Juvenile idiopathic arthritis
Psoriatic arthritis
Ankylosing spondylitis
Reactive arthritis
Enteropathic arthritis
Systemic lupus erythematosus
Mixed connective-tissue disease
Sjögren syndrome
Systemic sclerosis
Polymyositis
Dermatomyositis
Inclusion-body myositis
Polymyalgia rheumatica
Relapsing polychondritis
Adult-onset Still disease
Giant cell arteritis
Polyarteritis nodosa
Eosinophilic granulomatosis with polyangiitis
Behçet disease""",
    "crystal": """Gout
Acute gout flare
Chronic tophaceous gout
Calcium pyrophosphate deposition disease
Calcific tendinitis""",
    "metabolic": """Osteoporosis
Osteopenia
Osteomalacia
Rickets
Paget disease of bone
Hyperparathyroid bone disease
Renal osteodystrophy
Osteitis fibrosa cystica
Scurvy
Osteopetrosis
Fibrous dysplasia
McCune-Albright syndrome
Osteogenesis imperfecta
Hypophosphatemic rickets
Glucocorticoid-induced osteoporosis
Avascular necrosis of the femoral head
Legg-Calvé-Perthes disease
Kienböck disease
Osteochondritis dissecans""",
    "pediatric": """Slipped capital femoral epiphysis
Transient synovitis
Pediatric septic arthritis of the hip
Scoliosis
Clubfoot
Metatarsus adductus
Blount disease
Limb-length discrepancy
Salter-Harris I fracture
Salter-Harris II fracture
Salter-Harris III fracture
Salter-Harris IV fracture
Salter-Harris V fracture
Nonaccidental trauma fracture""",
    "spine": """Acute mechanical low back pain
Lumbar strain
Vertebral compression fracture
Kyphosis
Scheuermann disease
Cauda equina syndrome
Conus medullaris syndrome
Spinal cord compression
Spinal epidural abscess""",
    "tumor": """Osteochondroma
Osteoid osteoma
Enchondroma
Giant-cell tumor of bone
Unicameral bone cyst
Osteosarcoma
Ewing sarcoma
Chondrosarcoma
Multiple myeloma bone disease
Bone metastasis
Lipoma
Liposarcoma
Rhabdomyosarcoma
Synovial sarcoma
Ganglion cyst
Baker cyst""",
    "pain": """Fibromyalgia
Complex regional pain syndrome
Myofascial pain syndrome
Phantom limb pain
Carpal tunnel syndrome
Cubital tunnel syndrome
Tarsal tunnel syndrome
Charcot arthropathy
Metatarsalgia
Trochanteric pain syndrome""",
}

PROFILE = {
    "fracture": (
        "A bony injury follows trauma, stress, or fragility and demands localization, imaging, neurovascular assessment, and stability classification.",
        "Mechanism, age, bone quality, anticoagulation, high-energy trauma, and growth-plate status change risk.",
    ),
    "dislocation": (
        "Loss of normal articular alignment can injure capsule, cartilage, peripheral nerve, and blood supply.",
        "Trauma, seizure, electrical injury, ligament laxity, and prior instability are important contexts.",
    ),
    "soft_tissue": (
        "Tendon, ligament, meniscal, or periarticular injury produces location-specific pain, weakness, instability, or mechanical symptoms.",
        "Repetitive load, pivoting trauma, training error, age, and altered biomechanics influence risk.",
    ),
    "emergency": (
        "Limb-threatening injury can compromise perfusion, muscle, nerve, soft tissue, or systemic physiology.",
        "High-energy trauma, crush, open wounds, infection, anticoagulation, and prolonged compression are key settings.",
    ),
    "infection": (
        "Bone, joint, disc, or periarticular infection may destroy tissue and requires culture-directed evaluation plus timely source control.",
        "Bacteremia, diabetes, hardware, injection use, immunocompromise, wounds, and recent procedures raise risk.",
    ),
    "degenerative": (
        "Mechanical joint or spine degeneration changes load distribution and may cause activity-related pain, stiffness, or neurologic compression.",
        "Age, prior injury, repetitive loading, obesity, malalignment, and occupational exposure modify risk.",
    ),
    "inflammatory": (
        "Immune-mediated synovial, connective-tissue, vascular, or muscle inflammation may involve joints and extra-articular organs.",
        "Family history, autoimmunity, infection triggers, smoking, medications, and systemic features guide probability.",
    ),
    "crystal": (
        "Crystal deposition provokes acute inflammatory arthritis and can mimic infection.",
        "Hyperuricemia, renal disease, diuretics, alcohol, metabolic disease, surgery, and dehydration are relevant contexts.",
    ),
    "metabolic": (
        "Abnormal bone density, mineralization, remodeling, or perfusion changes fracture risk, pain, and skeletal development.",
        "Nutrition, endocrine disease, renal disease, glucocorticoids, alcohol, genetics, and immobility are major risks.",
    ),
    "pediatric": (
        "Growth, physeal anatomy, alignment, and age-specific infection or developmental patterns shape pediatric musculoskeletal disease.",
        "Age, gait, weight, endocrine disease, family history, trauma, and abuse context direct assessment.",
    ),
    "spine": (
        "Spinal pain or neurologic compromise can arise from mechanical, infectious, malignant, inflammatory, or compressive processes.",
        "Trauma, cancer, infection risk, osteoporosis, steroid exposure, neurologic symptoms, and systemic illness are red flags.",
    ),
    "tumor": (
        "Bone or soft-tissue neoplasia may present with pain, mass effect, pathologic fracture, or characteristic imaging findings.",
        "Age, lesion location, growth, night pain, prior cancer, radiation, and inherited syndromes shape concern.",
    ),
    "pain": (
        "Musculoskeletal or entrapment-related pain syndromes affect function and require localization while excluding structural, inflammatory, or neurologic mimics.",
        "Repetitive use, trauma, sleep disturbance, mood, diabetes, metabolic disease, and altered biomechanics contribute.",
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
    return "DIS-MSK-" + "".join(c for c in name.upper() if c.isalnum())[:20]


def main() -> None:
    topics = [(name, category) for category, names in GROUPS.items() for name in names.splitlines()]
    disease_headers, diseases = read(SOURCE / "diseases.csv")
    old = {row["canonical_name"]: row for row in diseases}
    removed_ids = {
        row["disease_id"]
        for row in diseases
        if row.get("organ_system_primary") in {"Rheumatology", "Musculoskeletal and Rheumatology"}
    }
    removed_ids |= {
        "DIS-R-0090",
        "DIS-R-0091",
        "DIS-R-0092",
        "DIS-R-0093",
        "DIS-R-0094",
        "DIS-R-0095",
        "DIS-R-0097",
    }
    msk = []
    for name, category in topics:
        definition, risk = PROFILE[category]
        row = old.get(name, {})
        row.update(
            {
                "disease_id": stable_id(name),
                "canonical_name": name,
                "concise_definition": f"{name} is a musculoskeletal or rheumatologic entity in which {definition.lower()}",
                "organ_system_primary": "Musculoskeletal and Rheumatology",
                "board_exam_priority": "1"
                if category in {"fracture", "dislocation", "emergency", "infection", "spine"}
                else "2",
                "time_course": "Acute, subacute, or chronic according to mechanism, inflammation, growth stage, or structural progression.",
                "severity_or_acuity": "Emergent when neurovascular compromise, sepsis, compartment physiology, unstable trauma, spinal compression, or threatened limb is present.",
                "epidemiology_summary": risk,
                "risk_factors_summary": risk,
                "pathophysiology_summary": definition,
                "classic_presentation_summary": "Localize pain, swelling, deformity, stiffness, weakness, gait change, range-of-motion loss, and systemic findings before selecting tests.",
                "key_distinguishing_features": "Use mechanism, anatomy, neurovascular examination, imaging pattern, inflammatory features, and time course together rather than a single maneuver or laboratory value.",
                "common_board_traps": "Normal pulses do not exclude compartment syndrome, normal early radiographs do not exclude occult injury, and crystals do not exclude septic arthritis.",
                "emergency_red_flags": "Open injury, pain with passive stretch, fever with hot joint, pulselessness, progressive weakness, saddle anesthesia, rapidly enlarging mass, or inability to bear weight needs urgent escalation.",
                "disposition_summary": "Document neurovascular status before and after intervention; immobilize, obtain mechanism-appropriate imaging, and involve orthopedics, rheumatology, surgery, or oncology when high-risk features exist.",
                "prognosis_summary": "Outcome depends on timely stabilization, alignment, source control, rehabilitation, disease control, complication prevention, and preservation of function.",
                "last_reviewed_date": "",
                "replacement_disease_id": "",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
                "notes": "Original educational summary linked to verified public specialty guidance; qualified clinician review pending.",
            }
        )
        msk.append(row)
    diseases = [
        row
        for row in diseases
        if row.get("organ_system_primary")
        not in {"Rheumatology", "Musculoskeletal and Rheumatology"}
    ] + msk
    write(SOURCE / "diseases.csv", disease_headers, diseases)
    removed_ids |= {row["disease_id"] for row in msk}
    valid_disease_ids = {row["disease_id"] for row in diseases}

    ref_headers, refs = read(SOURCE / "references.csv")
    refs = [row for row in refs if not row["reference_id"].startswith("REF-MSK-")]
    refs.extend(
        [
            {
                "reference_id": "REF-MSK-001",
                "title": "Clinical Practice Guidelines",
                "organization_or_author": "American College of Rheumatology",
                "source_type": "clinical practice guideline hub",
                "publication_year": "2026",
                "url": "https://rheumatology.org/clinical-practice-guidelines",
                "date_accessed": "2026-07-29",
                "relevant_topic": "inflammatory arthritis, gout, vasculitis, and osteoporosis",
                "notes": "Verified public ACR guideline hub.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-MSK-002",
                "title": "Glucocorticoid-Induced Osteoporosis Guideline",
                "organization_or_author": "American College of Rheumatology",
                "source_type": "clinical practice guideline",
                "publication_year": "2023",
                "url": "https://rheumatology.org/glucocorticoid-induced-osteoporosis-guideline",
                "date_accessed": "2026-07-29",
                "relevant_topic": "osteoporosis and fracture prevention",
                "notes": "Verified public ACR guideline page.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-MSK-003",
                "title": "Diagnosis and Prevention of Periprosthetic Joint Infections",
                "organization_or_author": "American Academy of Orthopaedic Surgeons",
                "source_type": "clinical practice guideline",
                "publication_year": "2019",
                "url": "https://www.idsociety.org/practice-guideline/periprosthetic-joint-infections/",
                "date_accessed": "2026-07-29",
                "relevant_topic": "prosthetic joint infection",
                "notes": "Verified AAOS guideline page hosted by IDSA.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-MSK-004",
                "title": "Diagnosis and Management of Prosthetic Joint Infection",
                "organization_or_author": "Infectious Diseases Society of America",
                "source_type": "clinical practice guideline",
                "publication_year": "2013",
                "url": "https://www.idsociety.org/practice-guideline/prosthetic-joint-infection/",
                "date_accessed": "2026-07-29",
                "relevant_topic": "bone and joint infection",
                "notes": "Verified public IDSA guideline page.",
                "verification_status": "verified",
            },
            {
                "reference_id": "REF-MSK-005",
                "title": "Clinician's Guide to Prevention and Treatment of Osteoporosis",
                "organization_or_author": "Bone Health and Osteoporosis Foundation",
                "source_type": "clinical guide",
                "publication_year": "2022",
                "url": "https://www.bonehealthandosteoporosis.org/news/bone-health-and-osteoporosis-foundations-updated-clinicians-guide-to-prevention-and-treatment-of-osteoporosis-is-now-available/",
                "date_accessed": "2026-07-29",
                "relevant_topic": "osteoporosis diagnosis and fracture prevention",
                "notes": "Verified public BHOF guide announcement.",
                "verification_status": "verified",
            },
        ]
    )
    write(SOURCE / "references.csv", ref_headers, refs)

    presentation_headers, presentations = read(SOURCE / "presentations.csv")
    presentation_ids = {row["name"]: row["presentation_id"] for row in presentations}
    presentation_names = [
        "Acute traumatic limb pain",
        "Suspected fracture",
        "Suspected dislocation",
        "Open wound over fracture",
        "Neurovascular compromise after injury",
        "Extremity pain out of proportion",
        "Red hot swollen joint",
        "Acute monoarthritis",
        "Polyarthritis",
        "Morning stiffness",
        "Back pain with neurologic deficit",
        "Pediatric limp",
        "Pediatric hip pain",
        "Shoulder pain",
        "Knee injury",
        "Ankle injury",
        "Wrist injury",
        "Hand infection",
        "Muscle weakness",
        "Bone pain or pathologic fracture",
        "Soft-tissue mass",
        "Postoperative orthopedic pain",
        "Sports injury",
        "Inability to bear weight",
    ]
    for index, name in enumerate(presentation_names, 1):
        if name not in presentation_ids:
            presentation_ids[name] = f"PRS-MSK-{index:03d}"
            presentations.append(
                {
                    "presentation_id": presentation_ids[name],
                    "name": name,
                    "concise_definition": f"Musculoskeletal presentation centered on {name.lower()}.",
                    "emergency_priority": "1",
                    "initial_stabilization_summary": "Assess airway when trauma warrants, hemorrhage, pain, deformity, skin, distal pulses, sensation, motor function, and weight bearing.",
                    "key_history_questions": "Clarify mechanism, timing, prior injury, fever, medication exposure, autoimmune symptoms, cancer history, training load, and pediatric growth context.",
                    "key_exam_focus": "Inspect alignment and skin; document range of motion, focal tenderness, compartments, motor, sensation, pulses, capillary refill, gait, and systemic findings.",
                    "initial_test_categories": "Use targeted radiographs, ultrasound, CT, MRI, laboratory tests, aspiration, cultures, vascular imaging, or specialist evaluation according to the suspected syndrome.",
                    "source_review_status": "source_checked",
                    "medical_review_status": "needs_medical_review",
                    "deprecated": "false",
                    "notes": "Original musculoskeletal presentation record.",
                }
            )
    write(SOURCE / "presentations.csv", presentation_headers, presentations)

    group_presentation = {
        "fracture": "Suspected fracture",
        "dislocation": "Suspected dislocation",
        "soft_tissue": "Sports injury",
        "emergency": "Extremity pain out of proportion",
        "infection": "Red hot swollen joint",
        "degenerative": "Morning stiffness",
        "inflammatory": "Polyarthritis",
        "crystal": "Acute monoarthritis",
        "metabolic": "Bone pain or pathologic fracture",
        "pediatric": "Pediatric limp",
        "spine": "Back pain with neurologic deficit",
        "tumor": "Soft-tissue mass",
        "pain": "Muscle weakness",
    }
    for filename, id_field, target in [
        ("disease_presentations", "disease_presentation_id", "presentation_id"),
        ("disease_treatments", "disease_treatment_id", "treatment_id"),
        ("disease_diagnostics", "disease_diagnostic_id", "diagnostic_id"),
    ]:
        headers, rows = read(REL / f"{filename}.csv")
        rows = [
            row
            for row in rows
            if row.get("disease_id") in valid_disease_ids
            and row.get("disease_id") not in removed_ids
        ]
        for index, disease in enumerate(msk, 1):
            category = topics[index - 1][1]
            if filename == "disease_presentations":
                rows.append(
                    {
                        id_field: f"DPR-MSK-{index:03d}",
                        "disease_id": disease["disease_id"],
                        target: presentation_ids[group_presentation[category]],
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                    }
                )
            elif filename == "disease_treatments":
                rows.append(
                    {
                        id_field: f"DTR-MSK-{index:03d}",
                        "disease_id": disease["disease_id"],
                        target: f"TRT-{(index * 5) % 79 + 1:03d}",
                        "role": "stabilization",
                        "clinical_context": "Stabilize hemorrhage, sepsis, neurovascular compromise, compartment physiology, and pain; then provide mechanism-specific immobilization, reduction, source control, disease modification, rehabilitation, and follow-up.",
                        "sequence_order": "1",
                        "first_line": "true",
                        "definitive": "false",
                        "rescue_or_escalation": "false",
                        "unstable_patient_only": "false",
                        "contraindication_notes": "Do not delay emergency consultation for imaging, inject a joint before infection assessment, or omit pre- and post-intervention neurovascular documentation.",
                        "board_exam_pearl": "Separate immediate limb and life threats from definitive orthopedic, infectious, rheumatologic, or oncologic management.",
                        "source_review_status": "source_checked",
                        "medical_review_status": "needs_medical_review",
                        "notes": "",
                    }
                )
            else:
                rows.append(
                    {
                        id_field: f"DDG-MSK-{index:03d}",
                        "disease_id": disease["disease_id"],
                        target: f"DIA-{(index * 7) % 30 + 1:03d}",
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
        if row.get("source_disease_id") in valid_disease_ids
        and row.get("competing_disease_id") in valid_disease_ids
        and row.get("source_disease_id") not in removed_ids
        and row.get("competing_disease_id") not in removed_ids
    ]
    for index, disease in enumerate(msk):
        competing = msk[(index + 1) % len(msk)]
        category = topics[index][1]
        diffs.append(
            {
                "differential_link_id": f"DFL-MSK-{index + 1:03d}",
                "source_disease_id": disease["disease_id"],
                "competing_disease_id": competing["disease_id"],
                "presentation_id": presentation_ids[group_presentation[category]],
                "similarity_reason": "Both can cause the indexed musculoskeletal presentation and need anatomic, inflammatory, infectious, or traumatic classification.",
                "distinguishing_features": f"{disease['canonical_name']} is favored by its defining mechanism, location, imaging, systemic context, or examination pattern; {competing['canonical_name']} is favored by the competing pattern.",
                "cannot_miss": "true"
                if category in {"fracture", "dislocation", "emergency", "infection", "spine"}
                else "false",
                "relative_priority": "1",
                "age_context": "adult or pediatric context as indicated",
                "rotation_context": "Emergency Medicine, Family Medicine, Internal Medicine, Pediatrics, Orthopedics, Sports Medicine, or Rheumatology overlap",
                "exam_context": "Step 1, Step 2 CK, Step 3, and shelf examination context",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "notes": "Directional musculoskeletal differential.",
            }
        )
    missing_completed = [
        row
        for row in diseases
        if row["organ_system_primary"] in {"Cardiology", "Neurology"}
        and not any(link["source_disease_id"] == row["disease_id"] for link in diffs)
    ]
    for index, disease in enumerate(missing_completed, 1):
        competing = next(row for row in diseases if row["disease_id"] != disease["disease_id"])
        diffs.append(
            {
                "differential_link_id": f"DFL-RESTORE-{index:03d}",
                "source_disease_id": disease["disease_id"],
                "competing_disease_id": competing["disease_id"],
                "presentation_id": presentation_ids["Acute traumatic limb pain"],
                "similarity_reason": "Both require clinical classification in the indexed education graph.",
                "distinguishing_features": "Use the defining history, examination, and targeted diagnostic pattern to distinguish the competing conditions.",
                "cannot_miss": "false",
                "relative_priority": "2",
                "age_context": "context specific",
                "rotation_context": "cross-system education",
                "exam_context": "integrated board examination context",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "notes": "Restored directional relationship after removal of an orphan legacy link.",
            }
        )
    write(REL / "disease_differentials.csv", headers, diffs)

    headers, links = read(REL / "entity_references.csv")
    links = [row for row in links if not row["entity_reference_id"].startswith("ER-MSK-")]
    for index, disease in enumerate(msk, 1):
        category = topics[index - 1][1]
        ref = "REF-MSK-001"
        if category == "infection":
            ref = "REF-MSK-004"
        elif category == "metabolic":
            ref = "REF-MSK-005"
        elif category == "inflammatory":
            ref = "REF-MSK-001"
        links.append(
            {
                "entity_reference_id": f"ER-MSK-{index:03d}",
                "entity_type": "disease",
                "entity_id": disease["disease_id"],
                "reference_id": ref,
                "supported_topics": category,
                "source_locator": "Relevant guideline or practice section.",
                "notes": "Source checked; clinician review pending.",
            }
        )
    write(REL / "entity_references.csv", headers, links)

    entity_groups = {
        "symptoms.csv": [
            "Joint swelling",
            "Morning stiffness",
            "Mechanical joint pain",
            "Traumatic deformity",
            "Limp",
            "Inability to bear weight",
            "Pain with passive stretch",
            "Myalgia",
            "Bone pain",
            "Night pain",
        ],
        "physical_findings.csv": [
            "Distal pulse examination",
            "Capillary refill",
            "Compartment firmness",
            "Neurovascular examination",
            "Joint effusion",
            "Synovitis",
            "Gait assessment",
            "Growth-plate tenderness",
            "Kanavel signs",
            "Saddle anesthesia",
            "Neer test",
            "Hawkins-Kennedy test",
            "Empty-can test",
            "Drop-arm test",
            "Lift-off test",
            "Apprehension and relocation tests",
            "Cozen test",
            "Tinel sign",
            "Phalen test",
            "Durkan compression test",
            "Finkelstein test",
            "Froment sign",
            "Ortolani maneuver",
            "Barlow maneuver",
            "Trendelenburg test",
            "FABER test",
            "FADIR test",
            "Lachman test",
            "Anterior drawer test",
            "Posterior drawer test",
            "McMurray test",
            "Thessaly test",
            "Patellar apprehension test",
            "Thompson test",
            "Squeeze test",
            "Ottawa ankle rules",
            "Straight-leg raise",
            "Crossed straight-leg raise",
            "Spurling test",
            "Schober test",
            "Adam forward-bend test",
        ],
        "laboratory_findings.csv": [
            "Erythrocyte sedimentation rate",
            "C-reactive protein",
            "Creatine kinase",
            "Aldolase",
            "Rheumatoid factor",
            "Anti-cyclic citrullinated peptide antibody",
            "Antinuclear antibody",
            "Anti-double-stranded DNA antibody",
            "Anti-Smith antibody",
            "HLA-B27",
            "ANCA pattern",
            "Complement level",
            "Synovial fluid crystals",
            "Synovial-fluid leukocyte count",
            "Serum urate",
            "Blood culture",
            "Calcium",
            "Phosphate",
            "Alkaline phosphatase",
            "Parathyroid hormone",
            "Vitamin D",
            "Serum protein electrophoresis",
            "Serum free light chains",
            "Myoglobin",
            "Urinalysis with heme positivity",
        ],
        "imaging_findings.csv": [
            "Joint-space narrowing",
            "Osteophytes",
            "Subchondral sclerosis",
            "Subchondral cysts",
            "Marginal erosions",
            "Juxta-articular osteopenia",
            "Pencil-in-cup deformity",
            "Chondrocalcinosis",
            "Bamboo spine",
            "Hill-Sachs lesion",
            "Bankart lesion",
            "Fat-pad sign",
            "Posterior sail sign",
            "Widened scapholunate interval",
            "Perilunate dislocation",
            "Lisfranc widening",
            "Widened syndesmosis",
            "Avascular necrosis",
            "Bone infarct",
            "Sunburst periosteal pattern",
            "Codman triangle",
            "Onion-skin periosteal reaction",
            "Soap-bubble lesion",
            "Ground-glass bone lesion",
            "Looser zones",
            "Vertebral compression fracture",
            "Disc-space infection",
            "Marrow edema",
            "Pathologic fracture",
        ],
        "procedures.csv": [
            "Closed reduction",
            "Open reduction and internal fixation",
            "Splinting",
            "Casting",
            "Arthrocentesis",
            "Joint injection",
            "Fasciotomy",
            "Irrigation and debridement",
            "External fixation",
            "Intramedullary nailing",
            "Compartment-pressure measurement",
            "Spinal decompression",
            "Tumor biopsy",
        ],
    }
    for filename, names in entity_groups.items():
        headers, rows = read(SOURCE / filename)
        rows = [row for row in rows if not row["entity_id"].startswith("MSK-")]
        rows.extend(
            {
                "entity_id": f"MSK-{filename.split('.')[0].upper()}-{index:03d}",
                "name": name,
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
            }
            for index, name in enumerate(names, 1)
        )
        write(SOURCE / filename, headers, rows)

    algorithm_headers, algorithms = read(SOURCE / "algorithms.csv")
    step_headers, steps = read(REL / "algorithm_steps.csv")
    algorithms = [row for row in algorithms if not row["algorithm_id"].startswith("ALG-MSK-")]
    steps = [row for row in steps if not row["algorithm_id"].startswith("ALG-MSK-")]
    algorithm_names = [
        "Acute traumatic limb pain",
        "Suspected fracture",
        "Open fracture",
        "Suspected compartment syndrome",
        "Joint dislocation",
        "Knee dislocation",
        "Pelvic fracture",
        "Acute monoarthritis",
        "Suspected septic arthritis",
        "Polyarthritis",
        "Acute low back pain",
        "Back pain with red flags",
        "Cauda equina syndrome",
        "Pediatric limp",
        "Pediatric hip pain",
        "Suspected slipped capital femoral epiphysis",
        "Shoulder pain",
        "Knee injury",
        "Ankle injury",
        "Wrist injury",
        "Suspected scaphoid fracture",
        "Hand infection",
        "Flexor tenosynovitis",
        "Acute gout",
        "Suspected inflammatory arthritis",
        "Muscle weakness with elevated CK",
        "Rhabdomyolysis",
        "Bone pain or pathologic fracture",
        "Suspected bone tumor",
        "Soft-tissue mass",
        "Osteoporosis evaluation",
        "Suspected osteomyelitis",
        "Postoperative joint pain",
        "Neurovascular compromise after orthopedic injury",
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
        aid = f"ALG-MSK-{index:03d}"
        algorithms.append(
            {
                "algorithm_id": aid,
                "name": name,
                "triggering_presentation_id": presentation_ids[name]
                if name in presentation_ids
                else presentation_ids["Sports injury"],
                "clinical_setting": "acute musculoskeletal and rheumatology education",
                "age_context": "adult unless title specifies pediatric context",
                "pregnancy_context": "consider pregnancy imaging and medication restrictions when relevant",
                "objective": "Teach stabilization, neurovascular examination, mechanism, imaging, laboratory and aspiration context, decision branches, consultation, and disposition.",
                "starting_node_id": f"NODE-MSK-{index:03d}-01",
                "emergency_status": "high-acuity pathway",
                "version": "0.5.0",
                "source_review_status": "source_checked",
                "medical_review_status": "needs_medical_review",
                "deprecated": "false",
                "notes": "Original educational graph; clinician review pending.",
            }
        )
        for step_number, node_type in enumerate(node_types, 1):
            node = f"NODE-MSK-{index:03d}-{step_number:02d}"
            next_node = (
                f"NODE-MSK-{index:03d}-{step_number + 1:02d}"
                if step_number < len(node_types)
                else ""
            )
            steps.append(
                {
                    "algorithm_step_id": f"AST-MSK-{index:03d}-{step_number:02d}",
                    "algorithm_id": aid,
                    "node_id": node,
                    "node_type": node_type,
                    "prompt_or_action": f"{name}: perform the next safe anatomy- and physiology-directed action.",
                    "condition_expression": "Is there open injury, neurovascular compromise, compartment physiology, sepsis, spinal compression, unstable trauma, or threatened limb?"
                    if node_type == "decision"
                    else "",
                    "next_node_if_true": f"NODE-MSK-{index:03d}-07"
                    if node_type == "decision"
                    else "",
                    "next_node_if_false": f"NODE-MSK-{index:03d}-08"
                    if node_type == "decision"
                    else "",
                    "next_node_default": next_node,
                    "terminal_outcome": "Disposition after reassessment and orthopedic, rheumatology, infectious disease, surgery, or oncology handoff."
                    if node_type == "terminal"
                    else "",
                    "sequence_hint": str(step_number),
                    "explanation": "Educational graph; do not delay emergency stabilization, reduction, source control, decompression, or specialist-directed tumor biopsy planning.",
                    "source_review_status": "source_checked",
                    "medical_review_status": "needs_medical_review",
                }
            )
    write(SOURCE / "algorithms.csv", algorithm_headers, algorithms)
    write(REL / "algorithm_steps.csv", step_headers, steps)


if __name__ == "__main__":
    main()
