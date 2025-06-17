"""
Agent 1 – Sproto ramblings
Usage:
    python agents/agent1.py --once --dry-run
    # scheduler will call run_once() daily
"""
from __future__ import annotations
import random, pathlib, datetime as dt
import yaml, textwrap
import sys
from pathlib import Path

# Patch sys.path so we can import TwitterAgent from base.py
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))
from base import TwitterAgent  # Use TwitterAgent as the base class
# from utils.moderation import safe_completion  # removed, now local
log = __import__("logging").getLogger(__name__)

THIS_DIR = pathlib.Path(__file__).parent
DIALOGUE_YAML = THIS_DIR / "sproto_corpus.yaml"

# --- Local OpenAI completion wrapper ---
def safe_completion(prompt, max_tokens=120, temperature=0.85):
    import logging, os
    log = logging.getLogger("agent1")
    try:
        import openai
    except ImportError:
        log.warning("openai package not installed; using stub response")
        return "[stub] OpenAI unavailable"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log.warning("OPENAI_API_KEY not set; using stub response")
        return "[stub] OpenAI unavailable"
    client = openai.OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:
        log.warning("openai completion failed: %s", exc)
        return "[stub] OpenAI error"

# ------------- Load dialogue snippets -------------
with DIALOGUE_YAML.open("r", encoding="utf-8") as fh:
    CORPUS: list[str] = yaml.safe_load(fh)

def _build_prompt() -> str:
    """Construct few‑shot prompt for OpenAI completion."""
    shots = random.sample(CORPUS, k=5)
    shots_txt = "\n".join(f"- {s}" for s in shots)
    today = dt.datetime.now(dt.timezone.utc).strftime("%b %d %Y")
    return textwrap.dedent(
        f"""
        You are Sproto, a chaotic but witty crypto commentator on X.
        Today is {today}. Generate one tweet:
        • Short, punchy, playful.
        • At most 240 characters.
        • Must include #SPROTO.
        • Optional extra hashtag from {{#BTC,#ETH,#Macro,#HarryPotterObamaSonic10Inu}}.
        • No profanity, slurs or disallowed content.

        Style examples:
        {shots_txt}

        Tweet:
        """
    ).strip()

def _generate_tweet() -> str:
    prompt = _build_prompt()
    tweet = safe_completion(prompt, max_tokens=120, temperature=0.85).strip()
    # Guard‑rails: ensure hashtag + length
    if "#SPROTO" not in tweet:
        tweet += " #SPROTO"
    return tweet[:280]

# ------------- Public API --------------------------
def create_post(persona="Sproto") -> tuple[str, None]:
    """Returns (text, img_path) — image path is None for this agent."""
    text = _generate_tweet()
    return text, None

def run_once(*, dry_run: bool = False) -> None:
    agent = TwitterAgent(
        idx=1,
        name="Agent1",
        personality="Sproto",
        dry_run=dry_run,
    )
    text, img = create_post()
    post_id = agent.post((text, img), dry_run=dry_run)
    if dry_run:
        print("DRY RUN TWEET:\n", text)
    log.info(
        "sproto_post",
        extra={"agent": "Agent1", "event": "posted", "post_id": post_id, "text": text},
    )

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.once:
        run_once(dry_run=args.dry_run) 