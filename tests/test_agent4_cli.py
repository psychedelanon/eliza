import subprocess, sys, os, pathlib, textwrap, shutil
import tempfile

def test_agent4_cli_dry_run(tmp_path, monkeypatch):
    # Copy run.py & minimal config into tmp dir
    root = pathlib.Path(__file__).resolve().parents[1]
    shutil.copy(root / "run.py", tmp_path)
    (tmp_path / "agents").mkdir(exist_ok=True)
    (tmp_path / "configs").mkdir(exist_ok=True)
    (tmp_path / "configs" / "agents.yaml").write_text(textwrap.dedent("""
        Agent4:
          persona: GremlinGM
    """))
    # Monkeypatch eliza.llm.complete to return a canned tweet
    monkeypatch.syspath_prepend(str(root))
    (tmp_path / "eliza").mkdir(exist_ok=True)
    (tmp_path / "eliza" / "llm.py").write_text(textwrap.dedent('''
        def complete(*a, **k):
            return "Good morning $BITCOIN believers! ☕✨ #HarryPotterObamaSonic10Inu"
    '''))
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
    assert "posted tweet" in res.stdout or "posted" in res.stdout.lower() 