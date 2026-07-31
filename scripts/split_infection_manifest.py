"""Create reviewable, non-overlapping views of the canonical infection manifest."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "curation" / "neurology"
GROUPS = {
    "infection_meningitis.yaml": ("mening", "neurosyphilis", "neuroborreliosis"),
    "infection_encephalitis.yaml": ("encephal", "leukoencephalopathy", "rabies"),
    "infection_focal_opportunistic.yaml": ("abscess",),
}


def main() -> None:
    entries = yaml.safe_load((BASE / "infection.yaml").read_text(encoding="utf-8"))
    assigned = set()
    for filename, terms in GROUPS.items():
        selected = [
            entry
            for entry in entries
            if any(term in entry["canonical_name"].lower() for term in terms)
        ]
        assigned.update(entry["disease_id"] for entry in selected)
        (BASE / filename).write_text(
            yaml.safe_dump(selected, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
    # Preserve remaining infection-scope records in the focal/opportunistic review view.
    path = BASE / "infection_focal_opportunistic.yaml"
    selected = yaml.safe_load(path.read_text(encoding="utf-8"))
    selected.extend(entry for entry in entries if entry["disease_id"] not in assigned)
    path.write_text(yaml.safe_dump(selected, allow_unicode=True, sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    main()
