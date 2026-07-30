# Source schema

Canonical entities use immutable IDs and CSV headers define fields. `source_status` records topic-level evidence confidence while `human_review_status` is independent and optional. `entity_references` links a disease, treatment, diagnostic, or algorithm to a reference without copying source text; it now includes verification date and notes. `keywords`, `disease_keywords`, `presentation_keywords`, and `disease_complications` are normalized coverage-first tables. Legacy review columns remain for backwards compatibility.
