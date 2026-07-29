# USMLE Clinical Knowledge Base

Structured, versioned educational data for a separate USMLE-learning
application. It contains no UI, API, authentication, cloud infrastructure, or
question-bank content.

> **Educational use only.** This is not clinical decision support or
> patient-specific medical advice. All initial clinical records are
> `draft_ai_generated` and require source and physician review before use in
> educational decision-making.

## Architecture

`data/source` and `data/reference` are the Git-friendly canonical tables.
Validation builds a SQLite development database, PostgreSQL-compatible schema
and seed SQL, deterministic JSON application bundles, a release manifest, and
quality reports. Consumers use `dist/json`, not source-table internals.

## Quick start

```bash
python -m pip install -e '.[dev]'
python -m usmle_kb all
make all
```

Common commands: `python -m usmle_kb validate`, `build sqlite`, `build
postgres`, `build bundles`, `quality-report`, `diff-release`, and `all`.

## Content workflow

Add or update entities in canonical CSV tables, preserving their stable IDs;
put multi-valued facts in `data/source/relationships`. Add original wording,
review metadata, and no invented citations. See [the documentation](docs/index.md)
for data definitions, application contract, reviews, release/version policy,
and contribution process.

Medical-content contributions must identify changed tables and entities,
reference and medical review, treatment/emergency/algorithm changes, contract
impact, migration need, and validation run. Airway, resuscitation,
anticoagulation, thrombolysis, insulin, electrolyte correction, pregnancy,
pediatrics, toxicology, antibiotics, dosing, and contraindications need extra
review.

MIT covers repository code only; contributed medical content must be original.
This project is not affiliated with NBME, USMLE, FSMB, UWorld, AMBOSS, or other
commercial study resources. Report suspected medical errors through the medical
content review issue template.
