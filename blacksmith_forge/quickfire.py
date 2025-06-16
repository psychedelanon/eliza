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
