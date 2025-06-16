import importlib
from pathlib import Path
import random, tempfile
import time

# Simple wrapper around the local quickfire module.
local_qf = importlib.import_module('quickfire')


def create_post(persona: str) -> str:
    suffix = f" [{int(time.time()*1000)%1_000_000}]"
    return f"Hello world{suffix} – {persona}"


def create_reply(persona: str, original: str) -> str:
    suffix = f" [{int(time.time()*1000)%1_000_000}]"
    return f"Re {original[:40]}{suffix} – {persona}"


def generate_image(persona_config, text):
    # Stub path used when real image generation is not available
    return Path("media/stub.png")


def generate_price_chart(btc: float, hpos: float, out: str | None = None):
    return "stub.png"
