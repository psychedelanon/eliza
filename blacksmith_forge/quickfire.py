import importlib
from pathlib import Path
import time
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
except Exception:
    plt = None

# Simple wrapper around the local quickfire module.
local_qf = importlib.import_module('quickfire')

__all__ = ["create_post", "create_reply", "generate_price_chart"]

MEDIA_ROOT = Path("media")
MEDIA_ROOT.mkdir(exist_ok=True)

def _stub(txt: str, persona: str) -> str:
    return f"{txt} – {persona}"

def create_post(persona: str) -> str:
    suffix = f" [{int(time.time()*1000)%1_000_000}]"
    return _stub("Hello world"+suffix, persona)

def create_reply(persona: str, original: str) -> str:
    return _stub(f"Re {original[:40]}", persona)

def _tiny_png(path: Path):
    # 1×1 transparent pixel
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xfc\xff"
        b"\xff?\x00\x05\xfe\x02\xfeA\xa8^\x97\x00\x00\x00\x00IEND\xaeB`\x82"
    )

def generate_price_chart(btc: float, hpos: float,
                         btc_pct: float = 0.0, hpos_pct: float = 0.0,
                         out: str | None = None):
    path = Path(out) if out else MEDIA_ROOT / f"chart_{int(time.time()*1e3)}.png"
    if plt is None:
        _tiny_png(path)
        return path
    try:
        # draw chart …
        # (simple two‑column green panel, no axis)
        fig, ax = plt.subplots(figsize=(10,5))
        ax.axis("off")
        ax.set_facecolor("#008000")
        
        # Use monospace font to avoid font issues
        font = FontProperties(family='monospace')
        
        # Left column (BTC)
        ax.text(0.25, 0.6, "BTC", color="white", ha="center", size=24, fontproperties=font)
        ax.text(0.25, 0.4, f"${btc:,.0f}", color="white", ha="center", size=20, fontproperties=font)
        ax.text(0.25, 0.2, f"{btc_pct:+.2f}%", color="white", ha="center", size=18, fontproperties=font)
        
        # Right column (HPOS)
        ax.text(0.75, 0.6, "HPOS10I", color="white", ha="center", size=24, fontproperties=font)
        ax.text(0.75, 0.4, f"${hpos:,.6f}", color="white", ha="center", size=20, fontproperties=font)
        ax.text(0.75, 0.2, f"{hpos_pct:+.2f}%", color="white", ha="center", size=18, fontproperties=font)
        
        fig.savefig(path, bbox_inches="tight", facecolor="#008000", dpi=100)
        plt.close(fig)
        return path
    except Exception as e:
        print(f"Chart generation failed: {e}")
        _tiny_png(path)
        return path

def generate_image(personality: str, text: str) -> Path:
    """Generate an image based on personality and text."""
    path = MEDIA_ROOT / f"image_{int(time.time()*1e3)}.png"
    if plt is None:
        _tiny_png(path)
        return path
    try:
        # Simple text-based image
        fig, ax = plt.subplots(figsize=(10,5))
        ax.axis("off")
        ax.set_facecolor("#008000")
        
        # Use monospace font to avoid font issues
        font = FontProperties(family='monospace')
        
        # Split text into lines to avoid wrapping issues
        lines = text[:50].split('\n')
        for i, line in enumerate(lines):
            y_pos = 0.5 - (i * 0.1)  # Space lines vertically
            ax.text(0.5, y_pos, line, color="white", ha="center", size=20, fontproperties=font)
        
        fig.savefig(path, bbox_inches="tight", facecolor="#008000", dpi=100)
        plt.close(fig)
        return path
    except Exception as e:
        print(f"Image generation failed: {e}")
        _tiny_png(path)
        return path
