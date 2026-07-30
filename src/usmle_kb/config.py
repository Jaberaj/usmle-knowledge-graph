from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "source"
REFERENCE = ROOT / "data" / "reference"
GENERATED = ROOT / "data" / "generated"
DATABASE = ROOT / "database"
DATABASE_GENERATED = DATABASE / "generated"
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"
LEGACY_REVIEW_STATUSES = {
    "draft_ai_generated",
    "source_checked",
    "needs_medical_review",
    "medically_reviewed",
}
SOURCE_STATUSES = {
    "unverified_ai_generated",
    "partially_source_supported",
    "source_supported",
    "conflicting_sources",
    "deprecated",
}
HUMAN_REVIEW_STATUSES = {"not_requested", "optional_review", "reviewed"}
REQUIRED_TABLES = {
    "diseases": [
        "disease_id",
        "canonical_name",
        "organ_system_primary",
        "board_exam_priority",
        "source_review_status",
        "medical_review_status",
        "deprecated",
    ],
    "presentations": [
        "presentation_id",
        "name",
        "emergency_priority",
        "source_review_status",
        "medical_review_status",
        "deprecated",
    ],
    "treatments": [
        "treatment_id",
        "name",
        "treatment_type",
        "source_review_status",
        "medical_review_status",
        "deprecated",
    ],
    "medications": [
        "medication_id",
        "generic_name",
        "medication_class",
        "source_review_status",
        "medical_review_status",
        "deprecated",
    ],
    "diagnostics": [
        "diagnostic_id",
        "name",
        "diagnostic_type",
        "source_review_status",
        "medical_review_status",
        "deprecated",
    ],
    "algorithms": [
        "algorithm_id",
        "name",
        "triggering_presentation_id",
        "starting_node_id",
        "source_review_status",
        "medical_review_status",
        "deprecated",
    ],
    "references": ["reference_id", "title", "verification_status"],
    "keywords": [
        "keyword_id",
        "keyword_text",
        "keyword_type",
        "normalized_keyword",
        "source_status",
        "deprecated",
    ],
    "complications": [
        "entity_id",
        "name",
        "source_review_status",
        "medical_review_status",
        "deprecated",
    ],
}
RELATIONSHIP_TABLES = [
    "disease_presentations",
    "disease_treatments",
    "disease_differentials",
    "disease_diagnostics",
    "algorithm_steps",
    "entity_references",
    "disease_keywords",
    "presentation_keywords",
    "disease_complications",
]
