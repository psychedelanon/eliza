from pathlib import Path
import random, textwrap, tempfile
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

__all__ = ["create_post", "create_reply", "generate_price_chart"]

HASHTAGS = ["#Crypto", "#BTC", "#HPOS10I", "#MemeMagic"]
EMOJIS   = ["🚀", "⚡", "🔥", "✨"]

def _stub(persona: str, txt: str) -> str:
    return f"{txt} – {persona} {random.choice(EMOJIS)} {random.choice(HASHTAGS)}"

def create_post(persona: str) -> str:
    return _stub(persona, "Hello world")

def create_reply(persona: str, original: str) -> str:
    return _stub(persona, f"Re {original[:40]}")

def generate_price_chart(btc: float, hpos: float, out: str | None = None):
    if plt is None:
        return None
    out_path = Path(out) if out else Path(tempfile.gettempdir()) / "price_chart.png"
    fig = plt.figure()
    plt.bar(["BTC","HPOS10I"], [btc, hpos], tick_label=["BTC","HPOS10I"])
    plt.title("Market‑close prices")
    plt.ylabel("USD")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path 