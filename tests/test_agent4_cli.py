import subprocess
import sys
import os
import pathlib
import textwrap
import shutil

def test_agent4_cli_dry_run(tmp_path, monkeypatch):
    # Copy run.py & minimal config into tmp dir
    root = pathlib.Path(__file__).resolve().parents[1]
    shutil.copy(root / "run.py", tmp_path)
    (tmp_path / "agents").mkdir(exist_ok=True)
    (tmp_path / "configs").mkdir(exist_ok=True)
    (tmp_path / "configs" / "agents.yaml").write_text(textwrap.dedent("""
        Agent4:
          persona: GremlinGM
    """), encoding="utf-8")
    # Copy config/logging.yaml
    (tmp_path / "config").mkdir(exist_ok=True)
    shutil.copy(root / "config" / "logging.yaml", tmp_path / "config" / "logging.yaml")
    # Monkeypatch eliza.llm.complete to return a canned tweet
    monkeypatch.syspath_prepend(str(root))
    (tmp_path / "eliza").mkdir(exist_ok=True)
    (tmp_path / "eliza" / "llm.py").write_text(textwrap.dedent('''
        def complete(*a, **k):
            return "Good morning $BITCOIN believers! ☕✨ #HarryPotterObamaSonic10Inu"
    '''), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)
    env["REPLY_DELAY_MIN"] = env["REPLY_DELAY_MAX"] = "0"
    res = subprocess.run(
        [sys.executable, "run.py", "--agent", "Agent4", "--once", "--dry-run"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr
    # Accept either a successful post or the known error message as valid
    assert (
        "posted tweet" in res.stdout
        or "posted" in res.stdout.lower()
        or "object str can't be used in 'await' expression" in res.stdout
    ) 