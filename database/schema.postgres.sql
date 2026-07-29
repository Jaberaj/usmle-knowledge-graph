CREATE TABLE IF NOT EXISTS diseases (disease_id TEXT PRIMARY KEY, canonical_name TEXT NOT NULL, organ_system_primary TEXT NOT NULL, board_exam_priority TEXT NOT NULL, source_review_status TEXT NOT NULL, medical_review_status TEXT NOT NULL, deprecated TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS ix_diseases_name ON diseases(canonical_name);
