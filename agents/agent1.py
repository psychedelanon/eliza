"""
Agent 1 – Sproto ramblings
Usage:
    python agents/agent1.py --once --dry-run
    # scheduler will call run_once() daily
"""
from __future__ import annotations
import random, pathlib, datetime as dt
import yaml, textwrap
from agents.base import TwitterAgent  # Use TwitterAgent as the base class
from utils.moderation import safe_completion  # thin OpenAI wrapper you already use
log = __import__("logging").getLogger(__name__)

THIS_DIR = pathlib.Path(__file__).parent
DIALOGUE_YAML = THIS_DIR / "sproto_corpus.yaml"

# ------------- Load dialogue snippets -------------
with DIALOGUE_YAML.open("r", encoding="utf-8") as fh:
    CORPUS: list[str] = yaml.safe_load(fh)

def _build_prompt() -> str:
    """Construct few‑shot prompt for OpenAI completion."""
    shots = random.sample(CORPUS, k=5)
    shots_txt = "\n".join(f"- {s}" for s in shots)
    today = dt.datetime.utcnow().strftime("%b %d %Y")
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