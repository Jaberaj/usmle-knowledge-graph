"""Targeted semantic corrections for the Phase 4B source relationships."""

from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source"
REL = SOURCE / "relationships"


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
    diseases = {r["canonical_name"]: r["disease_id"] for r in read(SOURCE / "diseases.csv")[1]}
    findings = {r["name"]: r["finding_id"] for r in read(SOURCE / "findings.csv")[1]}
    migraine = diseases["Migraine without aura"]
    ms = diseases["Multiple sclerosis"]
    fields, rows = read(REL / "disease_findings.csv")
    if "relationship_role" not in fields:
        fields.append("relationship_role")
    migraine_red_flags = {
        "Papilledema",
        "Xanthochromia",
        "Elevated opening pressure",
        "Meningismus",
    }
    for row in rows:
        if row["disease_id"] == migraine and row["finding_id"] in {
            findings[x] for x in migraine_red_flags
        }:
            row["presence"] = "negative"
            row["typicality"] = "atypical"
            row["relationship_role"] = "red_flag"
            row["clinical_meaning"] = (
                "This is not a typical migraine finding; it requires evaluation for secondary headache, including raised intracranial pressure, hemorrhage, or infection as appropriate."
            )
            row["distinguishing_value"] = (
                "A positive finding redirects the diagnosis away from uncomplicated migraine without aura."
            )
        if row["disease_id"] == ms and row["finding_id"] == findings["Aquaporin-4 antibodies"]:
            row["presence"] = "negative"
            row["typicality"] = "atypical"
            row["relationship_role"] = "favors_competitor"
            row["clinical_meaning"] = (
                "Aquaporin-4 IgG favors NMOSD rather than supporting multiple sclerosis."
            )
            row["distinguishing_value"] = (
                "A positive aquaporin-4 result should trigger NMOSD-directed evaluation and treatment planning."
            )
    write(REL / "disease_findings.csv", fields, rows)
    presentations = {r["name"]: r["presentation_id"] for r in read(SOURCE / "presentations.csv")[1]}
    fields, rows = read(REL / "disease_presentations.csv")
    rows = [
        row
        for row in rows
        if not (
            row["disease_id"] == migraine
            and row["presentation_id"]
            in {presentations["Progressive headache"], presentations["Vision loss"]}
        )
    ]
    for row in rows:
        if row["disease_id"] == migraine:
            row["key_positive_clues"] = (
                "Recurrent episodic pulsatile headache lasting hours with nausea, photophobia, or phonophobia and a normal neurologic examination between attacks supports migraine without aura."
            )
            row["key_negative_clues"] = (
                "No gradually spreading focal aura, persistent deficit, fever, papilledema, or meningismus is expected in uncomplicated migraine without aura."
            )
    write(REL / "disease_presentations.csv", fields, rows)
    diagnostics = {r["name"]: r["diagnostic_id"] for r in read(SOURCE / "diagnostics.csv")[1]}
    fields, rows = read(REL / "disease_diagnostics.csv")
    conditional = {
        "Noncontrast head CT",
        "CT angiography head and neck",
        "Lumbar puncture with CSF analysis",
        "MRI brain with contrast",
    }
    for row in rows:
        if row["disease_id"] == migraine and row["diagnostic_id"] in {
            diagnostics[x] for x in conditional
        }:
            label = next(
                name
                for name, identifier in diagnostics.items()
                if identifier == row["diagnostic_id"]
            )
            row["role"] = "secondary_cause_evaluation"
            row["clinical_context"] = (
                "Use only for sudden maximal-onset headache, trauma, altered consciousness, focal deficit, fever/meningismus, papilledema, or another concern for secondary headache; it is unnecessary for stable recurrent migraine with a normal examination."
            )
            row["expected_result"] = (
                f"In uncomplicated migraine, {label} is expected to show no secondary structural, hemorrhagic, vascular, or CSF explanation."
            )
            row["interpretation"] = (
                "A positive result redirects management to the demonstrated secondary disorder rather than confirming migraine."
            )
            row["limitations"] = (
                "A normal study does not override a concerning evolving examination; test selection follows the specific red flag."
            )
            row["test_to_avoid"] = (
                "Do not order this routinely for typical recurrent migraine with a normal examination."
            )
    write(REL / "disease_diagnostics.csv", fields, rows)
    scoped_ids = {
        entry["disease_id"]
        for filename in ("headache.yaml", "infection.yaml", "demyelinating.yaml")
        for entry in yaml.safe_load(
            (ROOT / "data" / "curation" / "neurology" / filename).read_text()
        )
    }
    replacements = {
        "is clinically meaningful only in that stated pattern": "is linked because its timing and associated examination findings match this illness script",
        "absence of the defining pattern above redirects evaluation": "absence of the expected syndrome features prompts a search",
        "helps distinguish": "has discriminating value for",
        "from the named mimics when interpreted with onset and examination": "when evaluated with the actual onset and examination",
        "has a defined role in this disease rather than serving as routine screening": "is ordered only for the concrete diagnostic question stated in the clinical context",
        "is assessed for the characteristic result described in the illness script above": "is expected to provide the disease-specific result stated in its interpretation",
        "Timing, technical quality, and the disease-specific pretest probability limit": "The limitation is the specific false-negative or nonspecific result described for",
    }
    for relation in (
        "disease_presentations",
        "disease_findings",
        "disease_keywords",
        "disease_diagnostics",
        "disease_treatments",
        "disease_complications",
    ):
        fields, rows = read(REL / f"{relation}.csv")
        for row in rows:
            if row["disease_id"] not in scoped_ids:
                continue
            for field, value in row.items():
                for old, new in replacements.items():
                    if old in value:
                        row[field] = value.replace(old, new)
        write(REL / f"{relation}.csv", fields, rows)


if __name__ == "__main__":
    main()
