import time
import logging
from typing import Tuple

import requests

log = logging.getLogger("prices")

_URL = "https://api.coingecko.com/api/v3/simple/price"
_PARAMS = {"ids": "bitcoin,harrypotterobamasonic10inu", "vs_currencies": "usd"}


def get_prices() -> Tuple[float, float]:
    for attempt in range(3):
        try:
            resp = requests.get(_URL, params=_PARAMS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            btc = float(data["bitcoin"]["usd"])
            hpos = float(data["harrypotterobamasonic10inu"]["usd"])
            return btc, hpos
        except Exception as exc:
            log.warning("price fetch failed: %s", exc)
            if attempt == 2:
                raise
            time.sleep(1)
    raise RuntimeError("unable to fetch prices")
