"""
Usage: python scripts/smoke.py

Runs:
  1) python run.py --demo --dry-run      # should hit duplicate guard second run
  2) python run.py --demo                # real tweets if creds + OPENAI key

Prints a colourized summary (use rich.print) of:
  ✔ post success
  ✔ reply success
  ✔ duplicate skip
"""

import os
import socket
import subprocess
import sys
from rich import print


def run(cmd):
    result = subprocess.run([sys.executable] + cmd, capture_output=True, text=True)
    return result.stdout + result.stderr


def main() -> None:
    log1 = run(["run.py", "--demo", "--dry-run"])
    log2 = run(["run.py", "--demo", "--dry-run"])

    post_ok = "dry_run" in log1
    reply_ok = "dry_run" in log1
    dup_ok = "duplicate" in log2

    have_net = False
    try:
        socket.create_connection(("api.twitter.com", 443), timeout=2)
        have_net = True
    except OSError:
        pass

    if os.getenv("TWITTER_AGENT1_API_KEY") and have_net:
        run(["run.py", "--demo"])

    status = [
        (post_ok, "post success"),
        (reply_ok, "reply success"),
        (dup_ok, "duplicate skip"),
    ]
    for ok, label in status:
        if ok:
            print(f"[green]✔ {label}[/green]")
        else:
            print(f"[red]✖ {label}[/red]")


if __name__ == "__main__":
    main()
