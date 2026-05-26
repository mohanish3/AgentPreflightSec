from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

import jsonschema

DEFAULT_SCHEMA_URL = "https://json.schemastore.org/sarif-2.1.0.json"


def main() -> int:
    if len(sys.argv) not in {2, 3}:
        print("usage: python scripts/validate_sarif.py <sarif-file> [schema-url-or-path]", file=sys.stderr)
        return 2

    sarif_path = Path(sys.argv[1])
    schema_ref = sys.argv[2] if len(sys.argv) == 3 else DEFAULT_SCHEMA_URL
    sarif = json.loads(sarif_path.read_text(encoding="utf-8"))

    if schema_ref.startswith("http://") or schema_ref.startswith("https://"):
        with urllib.request.urlopen(schema_ref, timeout=20) as response:
            schema = json.loads(response.read().decode("utf-8"))
    else:
        schema = json.loads(Path(schema_ref).read_text(encoding="utf-8"))

    jsonschema.validate(instance=sarif, schema=schema)
    print(f"valid sarif={sarif_path} schema={schema_ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
