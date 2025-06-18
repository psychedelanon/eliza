import subprocess
import sys
import os
import pathlib
import textwrap
import shutil

def test_agent3_cli_dry_run(tmp_path, monkeypatch):
    # copy run.py & minimal config into tmp dir
    root = pathlib.Path(__file__).resolve().parents[1]
    shutil.copy(root / "run.py", tmp_path)
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "agents.yaml").write_text(textwrap.dedent("""
        Agent3:
          persona: AlphaScry test
    """), encoding="utf-8")
    # Copy config/logging.yaml
    (tmp_path / "config").mkdir()
    shutil.copy(root / "config" / "logging.yaml", tmp_path / "config" / "logging.yaml")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)
    env["REPLY_DELAY_MIN"] = env["REPLY_DELAY_MAX"] = "0"
    res = subprocess.run(
        [sys.executable, "run.py", "--agent", "Agent3", "--once", "--dry-run"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr 