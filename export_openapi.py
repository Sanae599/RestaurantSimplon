# scripts/export_openapi.py
import json
import os

from app.main import app

out = os.environ.get("OPENAPI_OUT", "openapi.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(app.openapi(), f, ensure_ascii=False, indent=2)
print(f"Wrote {out}")
