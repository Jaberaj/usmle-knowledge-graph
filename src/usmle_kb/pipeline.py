"""Deterministic validation and export pipeline for canonical CSV data."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import (
    DATABASE_GENERATED,
    DIST,
    GENERATED,
    HUMAN_REVIEW_STATUSES,
    LEGACY_REVIEW_STATUSES,
    RELATIONSHIP_TABLES,
    REPORTS,
    REQUIRED_TABLES,
    SOURCE,
    SOURCE_STATUSES,
)
from .models import ReleaseManifest

DISCLAIMER = "Educational content only; not clinical decision support. Source status is topic-specific and human review is optional."

_NEUROLOGY_GENERIC_PHRASES = (
    "defined neurologic finding",
    "affected neural structure or disease process",
    "use with timing and the rest of the neurologic examination",
    "conditions linked in the canonical graph",
    "other disorders with a similar pattern",
    "no isolated finding independently establishes a diagnosis",
)


def _normalized_sentence_similarity(left: str, right: str) -> float:
    """Return token-set similarity for detecting copy/pasted explanatory prose."""
    left_terms = set(re.findall(r"[a-z0-9]+", left.lower()))
    right_terms = set(re.findall(r"[a-z0-9]+", right.lower()))
    if not left_terms or not right_terms:
        return 0.0
    return len(left_terms & right_terms) / len(left_terms | right_terms)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load() -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    for name in REQUIRED_TABLES:
        tables[name] = _read_csv(SOURCE / f"{name}.csv")
    for name in RELATIONSHIP_TABLES:
        tables[name] = _read_csv(SOURCE / "relationships" / f"{name}.csv")
    return tables


def validate(tables: dict[str, list[dict[str, str]]] | None = None) -> list[str]:
    tables = tables or load()
    errors: list[str] = []
    ids: dict[str, set[str]] = {}
    for table, columns in REQUIRED_TABLES.items():
        rows = tables[table]
        if not rows and table != "references":
            errors.append(f"{table}: no records")
        found = set(rows[0]) if rows else set(columns)
        missing = set(columns) - found
        if missing:
            errors.append(f"{table}: missing columns {sorted(missing)}")
        key = columns[0]
        values = [row.get(key, "") for row in rows]
        if "" in values:
            errors.append(f"{table}: blank stable ID")
        if len(values) != len(set(values)):
            errors.append(f"{table}: duplicate stable ID")
        ids[table] = set(values)
        for row in rows:
            for field in ("source_review_status", "medical_review_status"):
                if field in row and row[field] not in LEGACY_REVIEW_STATUSES:
                    errors.append(f"{table}: invalid {field}")
            if "source_status" in row and row["source_status"] not in SOURCE_STATUSES:
                errors.append(f"{table}: invalid source_status")
            if (
                "human_review_status" in row
                and row["human_review_status"] not in HUMAN_REVIEW_STATUSES
            ):
                errors.append(f"{table}: invalid human_review_status")
            if "deprecated" in row and row["deprecated"] not in {"true", "false"}:
                errors.append(f"{table}: invalid deprecated flag")
            if "board_exam_priority" in row and not row["board_exam_priority"].isdigit():
                errors.append(f"{table}: invalid priority")
    foreign = {
        "disease_presentations": ("disease_id", "diseases", "presentation_id", "presentations"),
        "disease_treatments": ("disease_id", "diseases", "treatment_id", "treatments"),
        "disease_diagnostics": ("disease_id", "diseases", "diagnostic_id", "diagnostics"),
        "disease_differentials": (
            "source_disease_id",
            "diseases",
            "competing_disease_id",
            "diseases",
        ),
        "algorithm_steps": ("algorithm_id", "algorithms", "node_id", None),
        "disease_keywords": ("disease_id", "diseases", "keyword_id", "keywords"),
        "presentation_keywords": ("presentation_id", "presentations", "keyword_id", "keywords"),
        "disease_complications": ("disease_id", "diseases", "complication_id", "complications"),
        "disease_findings": ("disease_id", "diseases", "finding_id", "findings"),
        "finding_localizations": ("finding_id", "findings", "localization_id", "localizations"),
    }
    for table, rows in tables.items():
        if table not in foreign:
            continue
        left, left_table, right, right_table = foreign[table]
        seen: set[tuple[str, ...]] = set()
        for row in rows:
            if row.get(left, "") not in ids[left_table]:
                errors.append(f"{table}: orphan {left}")
            if right_table and row.get(right, "") not in ids[right_table]:
                errors.append(f"{table}: orphan {right}")
            if table == "disease_differentials" and row.get(left) == row.get(right):
                errors.append("disease_differentials: self link")
            signature = tuple(row.values())
            if signature in seen:
                errors.append(f"{table}: duplicate relationship")
            seen.add(signature)
    for algorithm in tables["algorithms"]:
        nodes = {
            r["node_id"]
            for r in tables["algorithm_steps"]
            if r["algorithm_id"] == algorithm["algorithm_id"]
        }
        if algorithm["starting_node_id"] not in nodes:
            errors.append("algorithms: broken starting node")
    completed_system_records = [
        row
        for row in tables["diseases"]
        if row.get("organ_system_primary")
        in {
            "Cardiology",
            "Neurology",
            "Renal and Genitourinary",
            "Musculoskeletal and Rheumatology",
        }
    ]
    blocked = (
        "draft content pending review",
        "placeholder pending human review",
        "review required",
        "tbd",
        "todo",
        "lorem ipsum",
        "unknown",
        "depends on presentation",
        "depends on severity",
        "further testing is needed",
        "use clinical judgment",
    )
    required = (
        "concise_definition",
        "epidemiology_summary",
        "risk_factors_summary",
        "pathophysiology_summary",
        "classic_presentation_summary",
        "key_distinguishing_features",
        "emergency_red_flags",
        "disposition_summary",
        "prognosis_summary",
    )
    for row in completed_system_records:
        for field in required:
            value = row.get(field, "").lower()
            if not value or any(term in value for term in blocked):
                errors.append(f"{row['disease_id']}: placeholder {field}")
        if not any(
            link["disease_id"] == row["disease_id"] for link in tables["disease_presentations"]
        ):
            errors.append(f"{row['disease_id']}: no presentation")
        if not any(
            link["disease_id"] == row["disease_id"] for link in tables["disease_treatments"]
        ):
            errors.append(f"{row['disease_id']}: no treatment")
        if not any(
            link["disease_id"] == row["disease_id"] for link in tables["disease_diagnostics"]
        ):
            errors.append(f"{row['disease_id']}: no diagnostic")
        if not any(
            link["source_disease_id"] == row["disease_id"]
            for link in tables["disease_differentials"]
        ):
            errors.append(f"{row['disease_id']}: no differential")
        if row.get("source_status") != "unverified_ai_generated" and not any(
            link["entity_type"] == "disease" and link["entity_id"] == row["disease_id"]
            for link in tables["entity_references"]
        ):
            errors.append(f"{row['disease_id']}: no source link")
    neurology_findings = [
        row for row in tables["findings"] if row.get("finding_id", "").startswith("FND-NEUR")
    ]
    for finding in neurology_findings:
        explanatory_text = " ".join(
            finding.get(field, "")
            for field in (
                "concise_definition",
                "mechanism",
                "clinical_meaning",
                "localization_value",
                "major_associated_diseases",
                "important_mimics",
                "limitations",
            )
        ).lower()
        if any(phrase in explanatory_text for phrase in _NEUROLOGY_GENERIC_PHRASES):
            errors.append(f"{finding['finding_id']}: generic neurology finding prose")
    for index, finding in enumerate(neurology_findings):
        for comparison in neurology_findings[index + 1 :]:
            if (
                _normalized_sentence_similarity(
                    finding.get("clinical_meaning", ""), comparison.get("clinical_meaning", "")
                )
                >= 0.97
            ):
                errors.append(
                    f"{finding['finding_id']}: repeated neurology finding explanation with "
                    f"{comparison['finding_id']}"
                )
    return sorted(set(errors))


def _mkdirs() -> None:
    for path in (
        GENERATED,
        DATABASE_GENERATED,
        DIST / "json",
        DIST / "sql",
        DIST / "sqlite",
        DIST / "manifests",
        REPORTS,
    ):
        path.mkdir(parents=True, exist_ok=True)


def _sql_type(_: str) -> str:
    return "TEXT"


def build_sqlite(tables: dict[str, list[dict[str, str]]] | None = None) -> Path:
    tables = tables or load()
    errors = validate(tables)
    if errors:
        raise ValueError("; ".join(errors))
    _mkdirs()
    path = DATABASE_GENERATED / "usmle_kb.sqlite"
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        for table, rows in tables.items():
            columns = list(rows[0]) if rows else [REQUIRED_TABLES.get(table, ["id"])[0]]
            connection.execute(
                f'CREATE TABLE "{table}" ({", ".join(f'"{c}" {_sql_type(c)}' for c in columns)})'
            )
            if rows:
                keys = list(rows[0])
                marks = ",".join("?" for _ in keys)
                connection.executemany(
                    f'INSERT INTO "{table}" VALUES ({marks})',
                    [[row[k] for k in keys] for row in rows],
                )
        connection.executescript("""
        CREATE INDEX ix_diseases_name ON diseases(canonical_name);
        CREATE INDEX ix_diseases_organ ON diseases(organ_system_primary);
        CREATE INDEX ix_disease_treatment ON disease_treatments(disease_id);
        CREATE INDEX ix_disease_diagnostic ON disease_diagnostics(disease_id);
        CREATE INDEX ix_cannot_miss ON disease_differentials(cannot_miss);
        CREATE VIEW vw_disease_summary AS SELECT disease_id,canonical_name,organ_system_primary,board_exam_priority,medical_review_status FROM diseases;
        CREATE VIEW vw_presentation_differential AS SELECT dp.presentation_id,d.canonical_name FROM disease_presentations dp JOIN diseases d ON d.disease_id=dp.disease_id;
        CREATE VIEW vw_cannot_miss_differentials AS SELECT * FROM disease_differentials WHERE cannot_miss='true';
        CREATE VIEW vw_disease_treatment_pathway AS SELECT * FROM disease_treatments;
        CREATE VIEW vw_disease_diagnostic_pathway AS SELECT * FROM disease_diagnostics;
        CREATE VIEW vw_unreviewed_content AS SELECT disease_id,canonical_name FROM diseases WHERE human_review_status!='reviewed';
        CREATE VIEW vw_source_coverage AS SELECT disease_id,canonical_name,source_status,content_tier FROM diseases;
        CREATE VIEW vw_missing_content AS SELECT d.disease_id FROM diseases d LEFT JOIN disease_treatments t ON d.disease_id=t.disease_id WHERE t.disease_id IS NULL;
        CREATE VIEW vw_algorithm_nodes AS SELECT * FROM algorithm_steps;
        CREATE VIEW vw_disease_by_rotation AS SELECT disease_id,organ_system_primary FROM diseases;
        CREATE VIEW vw_disease_by_block AS SELECT disease_id,organ_system_primary FROM diseases;
        CREATE VIEW vw_disease_by_exam AS SELECT disease_id,board_exam_priority FROM diseases;
        """)
        connection.commit()
    finally:
        connection.close()
    target = DIST / "sqlite" / path.name
    target.write_bytes(path.read_bytes())
    return path


def build_postgres(tables: dict[str, list[dict[str, str]]] | None = None) -> tuple[Path, Path]:
    tables = tables or load()
    _mkdirs()
    schema = DIST / "sql" / "postgres_schema.sql"
    seed = DIST / "sql" / "postgres_seed.sql"
    schema.write_text(
        "\n".join(
            f"CREATE TABLE IF NOT EXISTS {name} ({', '.join(f'{c} TEXT' for c in (list(rows[0]) if rows else ['id']))});"
            for name, rows in tables.items()
        )
        + "\n",
        encoding="utf-8",
    )
    statements: list[str] = []
    for name, rows in tables.items():
        for row in rows:
            vals = ", ".join("'" + value.replace("'", "''") + "'" for value in row.values())
            statements.append(f"INSERT INTO {name} ({', '.join(row)}) VALUES ({vals});")
    seed.write_text("\n".join(statements) + "\n", encoding="utf-8")
    return schema, seed


def _json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def build_bundles(tables: dict[str, list[dict[str, str]]] | None = None) -> dict[str, Path]:
    tables = tables or load()
    errors = validate(tables)
    if errors:
        raise ValueError("; ".join(errors))
    _mkdirs()
    out = DIST / "json"
    files: dict[str, Path] = {}
    entities = {k: v for k, v in tables.items() if k in REQUIRED_TABLES}
    relationships = {k: tables[k] for k in RELATIONSHIP_TABLES}
    files["entities.json"] = out / "entities.json"
    _json(files["entities.json"], {"schema_version": "1.1.0", "entities": entities})
    files["relationships.json"] = out / "relationships.json"
    _json(files["relationships.json"], {"schema_version": "1.1.0", "relationships": relationships})
    pres: defaultdict[str, list[str]] = defaultdict(list)
    trts: defaultdict[str, list[str]] = defaultdict(list)
    diags: defaultdict[str, list[str]] = defaultdict(list)
    diffs: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    keywords: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    findings: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tables["disease_presentations"]:
        pres[row["disease_id"]].append(row["presentation_id"])
    for row in tables["disease_treatments"]:
        trts[row["disease_id"]].append(row["treatment_id"])
    for row in tables["disease_diagnostics"]:
        diags[row["disease_id"]].append(row["diagnostic_id"])
    for row in tables["disease_differentials"]:
        diffs[row["source_disease_id"]].append(row)
    keyword_by_id = {row["keyword_id"]: row for row in tables["keywords"]}
    finding_by_id = {row["finding_id"]: row for row in tables["findings"]}
    localized_finding_ids = {row["finding_id"] for row in tables["finding_localizations"]}
    source_by_disease = {row["disease_id"]: row["source_status"] for row in tables["diseases"]}
    for row in tables["disease_keywords"]:
        keywords[row["disease_id"]].append(keyword_by_id[row["keyword_id"]])
    for row in tables["disease_findings"]:
        findings[row["disease_id"]].append(finding_by_id[row["finding_id"]])
    disease_records = [
        {
            **d,
            "presentation_ids": sorted(pres[d["disease_id"]]),
            "treatment_ids": sorted(trts[d["disease_id"]]),
            "diagnostic_ids": sorted(diags[d["disease_id"]]),
            "differentials": diffs[d["disease_id"]],
            "keywords": keywords[d["disease_id"]],
            "findings": findings[d["disease_id"]],
            "eligibility": {
                "eligible_for_differential_game": bool(
                    pres[d["disease_id"]] and diffs[d["disease_id"]]
                ),
                "eligible_for_keyword_game": bool(keywords[d["disease_id"]]),
                "eligible_for_treatment_game": bool(trts[d["disease_id"]]),
                "eligible_for_next_best_step": any(
                    a["triggering_presentation_id"] in pres[d["disease_id"]]
                    for a in tables["algorithms"]
                ),
                "eligible_for_finding_game": bool(findings[d["disease_id"]]),
                "eligible_for_imaging_game": any(
                    finding["finding_type"] == "imaging" for finding in findings[d["disease_id"]]
                ),
                "eligible_for_pathology_game": any(
                    finding["finding_type"] == "pathology" for finding in findings[d["disease_id"]]
                ),
                "eligible_for_localization_game": any(
                    finding["finding_id"] in localized_finding_ids
                    for finding in findings[d["disease_id"]]
                ),
            },
        }
        for d in tables["diseases"]
    ]
    files["diseases.json"] = out / "diseases.json"
    _json(files["diseases.json"], {"schema_version": "1.1.0", "records": disease_records})
    p_records = [
        {
            **p,
            "common_differential_disease_ids": sorted(
                [d for d, pids in pres.items() if p["presentation_id"] in pids]
            ),
        }
        for p in tables["presentations"]
    ]
    files["presentations.json"] = out / "presentations.json"
    _json(files["presentations.json"], {"schema_version": "1.1.0", "records": p_records})
    for key in ("treatments", "medications"):
        files[f"{key}.json"] = out / f"{key}.json"
        _json(files[f"{key}.json"], {"schema_version": "1.1.0", "records": tables[key]})
    algs = [
        {
            **a,
            "nodes": [
                s for s in tables["algorithm_steps"] if s["algorithm_id"] == a["algorithm_id"]
            ],
        }
        for a in tables["algorithms"]
    ]
    files["algorithms.json"] = out / "algorithms.json"
    _json(files["algorithms.json"], {"schema_version": "1.1.0", "records": algs})
    games = {
        "differential_diagnosis": [
            {
                "presentation_id": p,
                "target_disease_id": d,
                "competing_disease_ids": [],
                "cannot_miss_disease_ids": [],
                "source_status": source_by_disease[d],
            }
            for d, ps in pres.items()
            for p in ps
        ],
        "treatment_selection": [
            {
                "disease_id": d,
                "correct_treatment_ids": sorted(v),
                "source_status": source_by_disease[d],
            }
            for d, v in trts.items()
        ],
        "next_best_step": [
            {
                "algorithm_id": a["algorithm_id"],
                "source_status": a["source_status"],
                "human_review_status": a["human_review_status"],
            }
            for a in tables["algorithms"]
        ],
        "keyword_recognition": [
            {
                "disease_id": disease_id,
                "keyword_ids": [row["keyword_id"] for row in rows],
                "source_status": source_by_disease[disease_id],
            }
            for disease_id, rows in sorted(keywords.items())
        ],
    }
    files["game_content.json"] = out / "game_content.json"
    _json(files["game_content.json"], games)
    index = [
        {
            "entity_id": d["disease_id"],
            "entity_type": "disease",
            "canonical_name": d["canonical_name"],
            "aliases": [],
            "organ_systems": [d["organ_system_primary"]],
            "search_keywords": [
                d["canonical_name"].lower(),
                *[k["normalized_keyword"] for k in keywords[d["disease_id"]]],
            ],
            "priority": int(d["board_exam_priority"]),
            "content_tier": d["content_tier"],
            "source_status": d["source_status"],
        }
        for d in tables["diseases"]
    ]
    files["search_index.json"] = out / "search_index.json"
    _json(files["search_index.json"], {"schema_version": "1.0.0", "records": index})
    return files


def _version(name: str) -> str:
    return (Path(__file__).resolve().parents[2] / name).read_text(encoding="utf-8").strip()


def _commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "uncommitted"


def build_release(tables: dict[str, list[dict[str, str]]] | None = None) -> Path:
    tables = tables or load()
    files = build_bundles(tables)
    build_sqlite(tables)
    build_postgres(tables)
    _mkdirs()
    manifest = ReleaseManifest(
        knowledge_base_version=_version("VERSION"),
        schema_version=_version("SCHEMA_VERSION"),
        application_contract_version=_version("APPLICATION_CONTRACT_VERSION"),
        build_timestamp=datetime.now(UTC).replace(microsecond=0).isoformat(),
        git_commit=_commit(),
        record_counts={k: len(v) for k, v in tables.items()},
        included_bundles=sorted(files),
        checksums={
            name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files.items()
        },
        compatibility_notes=[
            "Initial application contract; additive changes are backward compatible."
        ],
        disclaimer=DISCLAIMER,
    )
    path = DIST / "json" / "manifest.json"
    _json(path, manifest.model_dump())
    _json(DIST / "manifests" / "manifest.json", manifest.model_dump())
    return path


def quality_report(tables: dict[str, list[dict[str, str]]] | None = None) -> Path:
    tables = tables or load()
    _mkdirs()
    counts = {k: len(v) for k, v in tables.items()}
    organ = Counter(d["organ_system_primary"] for d in tables["diseases"])
    review = Counter(d["medical_review_status"] for d in tables["diseases"])
    report = {
        "row_counts": counts,
        "disease_counts_by_organ_system": dict(sorted(organ.items())),
        "review_status_distribution": dict(review),
        "diseases_without_presentations": sorted(
            {d["disease_id"] for d in tables["diseases"]}
            - {r["disease_id"] for r in tables["disease_presentations"]}
        ),
        "diseases_without_treatments": sorted(
            {d["disease_id"] for d in tables["diseases"]}
            - {r["disease_id"] for r in tables["disease_treatments"]}
        ),
        "validation_errors": validate(tables),
    }
    _json(REPORTS / "quality_report.json", report)
    (REPORTS / "quality_report.md").write_text(
        "# Quality report\n\n" + "\n".join(f"- {k}: {v}" for k, v in counts.items()) + "\n",
        encoding="utf-8",
    )
    coverage = {
        "diseases_by_system": dict(sorted(organ.items())),
        "source_status_distribution": dict(
            sorted(Counter(d["source_status"] for d in tables["diseases"]).items())
        ),
        "content_tier_distribution": dict(
            sorted(Counter(d["content_tier"] for d in tables["diseases"]).items())
        ),
        "presentations_per_disease": dict(
            sorted(Counter(row["disease_id"] for row in tables["disease_presentations"]).items())
        ),
        "differentials_per_disease": dict(
            sorted(
                Counter(row["source_disease_id"] for row in tables["disease_differentials"]).items()
            )
        ),
        "treatments_per_disease": dict(
            sorted(Counter(row["disease_id"] for row in tables["disease_treatments"]).items())
        ),
        "diagnostics_per_disease": dict(
            sorted(Counter(row["disease_id"] for row in tables["disease_diagnostics"]).items())
        ),
        "keywords_per_disease": dict(
            sorted(Counter(row["disease_id"] for row in tables["disease_keywords"]).items())
        ),
        "complications_per_disease": dict(
            sorted(Counter(row["disease_id"] for row in tables["disease_complications"]).items())
        ),
    }
    _json(REPORTS / "usmle_coverage_matrix.json", coverage)
    (REPORTS / "usmle_coverage_matrix.md").write_text(
        "# USMLE coverage matrix\n\n"
        + "\n".join(f"- {system}: {count}" for system, count in sorted(organ.items()))
        + "\n",
        encoding="utf-8",
    )
    report_files = {
        "presentation_coverage.md": coverage["presentations_per_disease"],
        "differential_coverage.md": coverage["differentials_per_disease"],
        "treatment_coverage.md": coverage["treatments_per_disease"],
        "finding_coverage.md": {"keyword_linked_diseases": len(coverage["keywords_per_disease"])},
        "keyword_coverage.md": coverage["keywords_per_disease"],
        "source_coverage.md": coverage["source_status_distribution"],
        "gap_analysis.md": {
            "diseases_without_keywords": len(tables["diseases"])
            - len(coverage["keywords_per_disease"]),
            "diseases_without_complications": len(tables["diseases"])
            - len(coverage["complications_per_disease"]),
            "diseases_without_differentials": len(tables["diseases"])
            - len(coverage["differentials_per_disease"]),
        },
    }
    for filename, values in report_files.items():
        (REPORTS / filename).write_text(
            "# "
            + filename.removesuffix(".md").replace("_", " ").title()
            + "\n\n"
            + "\n".join(f"- {key}: {value}" for key, value in sorted(values.items()))
            + "\n",
            encoding="utf-8",
        )
    return REPORTS / "quality_report.json"
