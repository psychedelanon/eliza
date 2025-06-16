import importlib
from pathlib import Path
import random, tempfile

# Simple wrapper around the local quickfire module.
local_qf = importlib.import_module('quickfire')


def create_post(persona: str) -> str:
    return f"Hello world – {persona}"


def create_reply(persona: str, original: str) -> str:
    return f"Re {original[:40]} – {persona}"


def generate_image(persona_config, text):
    # Stub path used when real image generation is not available
    return Path("media/stub.png")


def generate_price_chart(btc: float, hpos: float, out: str | None = None):
    return "stub.png"
