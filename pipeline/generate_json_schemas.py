"""
Generate /content/schemas/*.json from the pydantic models in schemas.py.

Usage:
    python generate_json_schemas.py [--check]

--check: don't write files; exit non-zero if regenerated output would differ
from what's currently committed under /content/schemas/. Used by CI to catch
drift between schemas.py and the committed JSON Schemas (PROGRESS.md).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from schemas import CONTENT_MODELS

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "content" / "schemas"

# $id base for generated schemas; not a real hosted URL, just a stable
# namespace so refs are unambiguous if these are ever bundled together.
ID_BASE = "https://ascent.local/content/schemas"


def build_schema(key: str, model: type) -> dict:
    schema = model.model_json_schema()
    # Put $schema/$id first for readability; model_json_schema() doesn't set them.
    ordered = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{ID_BASE}/{key}.schema.json",
        "title": model.__name__,
        **schema,
    }
    return ordered


def generate() -> dict[str, str]:
    """Returns {relative_path: json_text} for every content model."""
    out = {}
    for key, model in sorted(CONTENT_MODELS.items()):
        schema = build_schema(key, model)
        text = json.dumps(schema, indent=2, sort_keys=False) + "\n"
        out[f"{key}.schema.json"] = text
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    generated = generate()

    if args.check:
        drift = []
        for filename, text in generated.items():
            path = OUT_DIR / filename
            if not path.exists() or path.read_text() != text:
                drift.append(filename)
        if drift:
            print("Drift detected between schemas.py and committed JSON Schemas:")
            for f in drift:
                print(f"  - content/schemas/{f}")
            print("Run: python pipeline/generate_json_schemas.py")
            return 1
        print(f"OK — {len(generated)} JSON Schemas match schemas.py.")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, text in generated.items():
        (OUT_DIR / filename).write_text(text)
    print(f"Wrote {len(generated)} JSON Schemas to {OUT_DIR.relative_to(REPO_ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
