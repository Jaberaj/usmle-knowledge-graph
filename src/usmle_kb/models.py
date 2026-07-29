from pydantic import BaseModel, Field


class ReleaseManifest(BaseModel):
    knowledge_base_version: str
    schema_version: str
    application_contract_version: str
    build_timestamp: str
    git_commit: str
    record_counts: dict[str, int]
    included_bundles: list[str]
    checksums: dict[str, str]
    compatibility_notes: list[str] = Field(default_factory=list)
    disclaimer: str
