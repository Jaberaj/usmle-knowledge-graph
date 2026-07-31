"""Generate exact review views from the canonical infection manifest and mapping."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/curation/neurology"


def main():
    entries = yaml.safe_load((BASE / "infection.yaml").read_text())
    mapping = yaml.safe_load((BASE / "infection_view_mapping.yaml").read_text())
    for view in ("meningitis", "encephalitis", "focal_opportunistic", "other"):
        selected = [e for e in entries if mapping[e["disease_id"]]["view"] == view]
        p = BASE / f"infection_{view}.yaml"
        if selected:
            p.write_text(yaml.safe_dump(selected, allow_unicode=True, sort_keys=False))
        elif p.exists():
            p.unlink()


if __name__ == "__main__":
    main()
