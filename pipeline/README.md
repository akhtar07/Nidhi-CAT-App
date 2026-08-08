# /pipeline

Offline Python pipeline that ingests source material and emits validated
JSON into `/content`. Never runs in the browser. See SPEC.md §6.

`schemas.py` (pydantic v2, added in Milestone 1) is the single source of
truth for content types — see PROGRESS.md for the generation flow into
`/content/schemas/` and `/app/src/types/content.ts`.

`/pipeline/raw/` holds raw ingested source material (PDFs, scraped HTML,
etc.) and is gitignored — see SPEC.md §6 and CLAUDE.md. Never commit
anything from it.
