"""Scaffold a new agent module and scheduler entry."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml


TEMPLATE = Path("agents/agent_template.py")
SCHED_PATH = Path("config/scheduler.yaml")


def create_agent(name: str) -> None:
    dest = Path("agents") / f"{name}.py"
    if dest.exists():
        raise SystemExit(f"{dest} already exists")
    shutil.copy(TEMPLATE, dest)

    sched = yaml.safe_load(SCHED_PATH.read_text()) or {"jobs": []}
    sched.setdefault("jobs", []).append(
        {
            "id": f"{name}_daily",
            "func": f"agents.{name}:run_once",
            "trigger": "cron",
            "hour": 0,
            "minute": 0,
        }
    )
    SCHED_PATH.write_text(yaml.safe_dump(sched))
    print(f"Created {dest} and updated scheduler.yaml")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="New agent module name (e.g. agent3)")
    args = ap.parse_args()
    create_agent(args.name)


if __name__ == "__main__":
    main()
