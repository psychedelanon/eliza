import importlib
from pathlib import Path

# Simple wrapper around the local quickfire module.
local_qf = importlib.import_module('quickfire')


def create_post(persona_config):
    # persona_config is currently a string persona
    return local_qf.create_post(persona_config)


def generate_image(persona_config, text):
    # Stub path used when real image generation is not available
    return Path("media/stub.png")


def generate_price_chart(btc: float, hpos: float, out: str | None = None):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        import logging

        logging.getLogger("quickfire").warning(
            "matplotlib unavailable: %s", exc
        )
        return None

    from tempfile import mkstemp

    out_path = Path(out) if out else Path(mkstemp(suffix=".png")[1])

    fig, ax = plt.subplots()
    ax.bar(["BTC", "HPOS10I"], [btc, hpos], color=["blue", "orange"])
    ax.set_ylabel("USD")
    fig.tight_layout()
    plt.savefig(out_path)
    plt.close(fig)
    return out_path
