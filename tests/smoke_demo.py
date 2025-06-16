import os
import sys
import pytest
import subprocess

@pytest.mark.skipif(
    not os.environ.get("TWITTER_AGENT1_API_KEY"),
    reason="TWITTER_AGENT1_API_KEY not set"
)
def test_demo_smoke(monkeypatch, tmp_path, caplog):
    """
    Run `python run.py --demo` twice in a row with env vars tweaked
    and assert the behaviour via log capture.
    """
    # Set required environment variables
    env = os.environ.copy()
    env["TWITTER_ENABLE_POST_GENERATION"] = "false"
    env["REPLY_DELAY_MIN"] = "1"
    env["REPLY_DELAY_MAX"] = "2"
    env["TWEET_DEDUP_WINDOW"] = "1"
    env.pop("OPENAI_API_KEY", None)  # Unset OpenAI key to test fallback

    # Patch asyncio.sleep to record delays
    sleep_calls = []
    def fake_sleep(secs):
        sleep_calls.append(secs)
        return None
    monkeypatch.setattr("asyncio.sleep", fake_sleep)

    # Run the script the first time
    result1 = subprocess.run(
        [sys.executable, "run.py", "--demo"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    log1 = result1.stdout + result1.stderr

    # Run the script the second time (should trigger duplicate guard)
    result2 = subprocess.run(
        [sys.executable, "run.py", "--demo"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    log2 = result2.stdout + result2.stderr

    # 1. Duplicate guard: Only one post, then duplicate avoided
    assert any("posted tweet" in line.lower() for line in log1.splitlines())
    assert "duplicate avoided" in log2

    # 2. OpenAI fallback stub is used
    expected = "OPENAI_API_KEY not set; using OpenAI fallback stub"
    assert expected in log1 or expected in log2

    # 3. Reply delay is between 1 and 2 seconds
    assert any(1 <= float(secs) <= 2 for secs in sleep_calls), f"Delays: {sleep_calls}"

    # 4. Script exits cleanly in demo mode
    assert result1.returncode == 0
    assert result2.returncode == 0 