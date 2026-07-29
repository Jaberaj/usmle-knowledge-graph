# Agent instructions

Read `README.md` and relevant documentation before editing. `data/source` and
`data/reference` are canonical; never manually edit `data/generated`,
`database/generated`, or `dist`. Preserve stable entity IDs, use normalized
relationship tables, and never duplicate a clinical fact across canonical
tables. Never fabricate citations or references, copy proprietary question-bank
wording, or describe draft content as medically validated.

Mark generated medical content `draft_ai_generated`. Update schemas and
migration notes when fields change, preserve backward compatibility where
practical, and increment the appropriate version for application-contract
changes. Before finishing run validation, tests, linting, type checking,
database builds, and contract tests. Summarize changed files, data counts,
schema changes, and commands run.
