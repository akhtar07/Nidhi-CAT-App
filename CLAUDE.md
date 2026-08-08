# Project: Ascent — CAT 2026 prep app

## Before doing ANYTHING
1. Read SPEC.md in full. It is the authoritative spec.
2. Read PROGRESS.md to see what is already built.
3. Do not start work until I name a specific milestone from SPEC.md §15.

## Hard rules (from SPEC.md §1)
- Static build only. Deploys to GitHub Pages.
- All learner state behind the StorageAdapter interface. IndexedDB is v1.
- Content is JSON in /content. Never hardcode questions in components.
- No API keys in client code, ever.
- No placeholder or fake questions. Missing content is fine; fake content is not.
- Ask before adding a dependency not listed in SPEC.md §7.

## End of every milestone
Update PROGRESS.md with: what was built, what was deferred, any schema
changes, and the commands to run it locally. Then stop.
