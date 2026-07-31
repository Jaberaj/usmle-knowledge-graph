"""Apply final scoped finding-role and infection ownership corrections."""

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/source"
REL = SOURCE / "relationships"
CUR = ROOT / "data/curation/neurology"


def read(p):
    with p.open(encoding="utf-8", newline="") as h:
        r = csv.DictReader(h)
        return list(r.fieldnames or []), list(r)


def write(p, f, rows):
    with p.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, f, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    scoped = {
        e["disease_id"]
        for fn in ("headache.yaml", "infection.yaml", "demyelinating.yaml")
        for e in yaml.safe_load((CUR / fn).read_text())
    }
    _, ds = read(SOURCE / "diseases.csv")
    did = {r["canonical_name"]: r["disease_id"] for r in ds}
    _, fs = read(SOURCE / "findings.csv")
    fid = {r["name"]: r["finding_id"] for r in fs}
    f, rows = read(REL / "disease_findings.csv")
    if "relationship_role" not in f:
        f.append("relationship_role")
    brain = did["Brain abscess"]
    disallowed = {
        fid[x]
        for x in (
            "Neutrophilic CSF",
            "Lymphocytic CSF",
            "Low CSF glucose",
            "Meningismus",
            "Temporal-lobe abnormalities",
            "Elevated opening pressure",
        )
    }
    for r in rows:
        if r["disease_id"] not in scoped:
            continue
        if not r.get("relationship_role"):
            r["relationship_role"] = (
                "supportive"
                if r.get("presence")
                in {"present", "positive", "increased", "decreased", "variable"}
                else "negative_finding"
            )
        if r["disease_id"] == brain and r["finding_id"] in disallowed:
            r["presence"] = "negative"
            r["relationship_role"] = "favors_competitor"
            r["typicality"] = "atypical"
            r["clinical_meaning"] = (
                "This is not a routine brain-abscess finding; it instead directs evaluation toward meningitis, encephalitis, or another competing process."
            )
    write(REL / "disease_findings.csv", f, rows)


if __name__ == "__main__":
    main()
