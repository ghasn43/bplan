"""Regenerate the AquaPure demo JSON seed from the Python builder.

Run from the backend/ directory:

    python -m scripts.generate_demo

Re-run this whenever the Pydantic schemas change so the committed
``app/seeds/demo_aquapure_smart_filters.json`` stays in sync and valid.
"""
from __future__ import annotations

import json

from app.models import BusinessPlanProject
from app.services.demo import DEMO_JSON_PATH
from app.services.demo_builder import build_demo_project


def main() -> None:
    project = build_demo_project()
    payload = project.model_dump(mode="json")

    DEMO_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEMO_JSON_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Re-validate the written artifact to guarantee it matches the schema.
    data = json.loads(DEMO_JSON_PATH.read_text(encoding="utf-8"))
    BusinessPlanProject.model_validate(data)
    print(f"Wrote and validated {DEMO_JSON_PATH} ({DEMO_JSON_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
