import argparse
import json
import logging
import time
from typing import Dict, List, Optional

import requests

from agents.base import TwitterAgent
from eliza import llm

log = logging.getLogger("alpha_scry")

AGENT_NAME = "AlphaScry"
CHAIN_TAGS = {
    "ethereum": "ETH",
    "bsc": "BSC",
    "polygon": "Polygon",
    "arbitrum": "Arbitrum",
    "optimism": "Optimism",
    "avalanche": "AVAX",
    "fantom": "Fantom",
    "harmony": "Harmony",
    "cronos": "Cronos",
    "solana": "Solana",
    "pulse": "Pulse",
}


BASE_TOKENS = {
    "ethereum": [
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
    ],
    "bsc": [
        "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
        "0xe9e7cea3dedca5984780bafc599bd69add087d56",  # BUSD
    ],
}


def fetch_hot_tokens() -> List[Dict[str, Optional[str]]]:
    """Return hot tokens across chains using DexScreener."""

    tokens: List[Dict[str, Optional[str]]] = []
    for chain, bases in BASE_TOKENS.items():
        url = f"https://api.dexscreener.com/latest/dex/tokens/{','.join(bases)}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                log.error(json.dumps({
                    "event": "fetch_fail",
                    "agent": AGENT_NAME,
                    "text": f"{chain} HTTP {resp.status_code}",
                }))
                continue
            data = resp.json()
        except Exception as exc:  # pragma: no cover - network
            log.error(json.dumps({
                "event": "fetch_fail",
                "agent": AGENT_NAME,
                "text": f"{chain} exception {exc}",
            }))
            continue
        for pair in data.get("pairs", []):
            base_addr = pair.get("baseToken", {}).get("address", "").lower()
            quote_addr = pair.get("quoteToken", {}).get("address", "").lower()
            base_set = {addr.lower() for addr in bases}
            if base_addr in base_set:
                token = pair.get("quoteToken", {})
            elif quote_addr in base_set:
                token = pair.get("baseToken", {})
            else:
                continue
            address = token.get("address")
            if not address or address.lower() in base_set:
                continue
            info = {
                "name": token.get("name") or token.get("symbol"),
                "symbol": token.get("symbol") or token.get("name"),
                "chain": chain,
                "address": address,
                "volume": pair.get("volume", {}).get("h24"),
                "price": pair.get("priceUsd") or pair.get("price"),
                "liquidity": pair.get("liquidity", {}).get("usd"),
                "chart": pair.get("url", f"https://dexscreener.com/{chain}/{address}"),
            }
            tokens.append(info)
    # dedupe by chain/address keep highest volume
    dedup: Dict[tuple, Dict[str, Optional[str]]] = {}
    for t in tokens:
        key = (t["chain"], t["address"].lower())
        if key not in dedup or (t.get("volume") or 0) > (dedup[key].get("volume") or 0):
            dedup[key] = t
    return sorted(dedup.values(), key=lambda x: x.get("volume", 0) or 0, reverse=True)


def generate_tweet(token: Dict[str, Optional[str]], llm_client=None) -> str:
    """Create a short narrative tweet about a token."""

    chain = token.get("chain", "")
    tag = CHAIN_TAGS.get(chain.lower(), chain.upper())
    prompt = (
        "Here is a token's data:\n"
        f"Name: {token.get('name')}\n"
        f"Symbol: {token.get('symbol')}\n"
        f"Chain: {chain}\n"
        f"Address: {token.get('address')}\n"
        f"Volume24h: {token.get('volume')}\n"
    )
    if token.get("liquidity"):
        prompt += f"Liquidity: {token['liquidity']}\n"
    if token.get("price"):
        prompt += f"Price: {token['price']}\n"
    prompt += (
        "\nWrite one tweet under 280 chars capturing why this token is buzzing. "
        "Mention liquidity or volume if notable. Use an influencer tone with emojis. "
        "Include $" + str(token.get("symbol")) + " and a short contract like " + token.get("address", "")[:6] + "..." + token.get("address", "")[-4:] + "."
        " End with #AlphaScry and #" + tag
    )

    if llm_client:
        out = llm_client.complete(prompt)
    else:
        out = llm.complete(prompt)
    tweet = str(out).strip()
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    if "#AlphaScry" not in tweet:
        tweet = tweet.rstrip() + " #AlphaScry"
    if f"#{tag}" not in tweet:
        tweet = tweet.rstrip() + f" #{tag}"
    return tweet


def main() -> None:
    ap = argparse.ArgumentParser(description="AlphaScry trending token agent")
    ap.add_argument("--once", action="store_true", help="run one cycle and exit")
    ap.add_argument("--dry-run", action="store_true", help="print instead of posting")
    ap.add_argument("--test", action="store_true", help="run with mocked data")
    args = ap.parse_args()

    if args.test:
        args.dry_run = True
        tokens = [
            {
                "name": "TestToken",
                "symbol": "TST",
                "chain": "ethereum",
                "address": "0xTEST",
                "volume": 12345,
                "price": 0.0001,
                "liquidity": 50000,
                "chart": "https://dexscreener.com/eth/0xTEST",
            }
        ]
    else:
        tokens = fetch_hot_tokens()

    agent = TwitterAgent(idx=3, name=AGENT_NAME, personality=AGENT_NAME, dry_run=args.dry_run)

    for token in tokens:
        try:
            tweet = generate_tweet(token)
        except Exception as exc:  # pragma: no cover - unexpected
            log.error(json.dumps({
                "event": "generate_fail",
                "agent": AGENT_NAME,
                "text": str(exc),
            }))
            continue
        log.info(json.dumps({"event": "tweet", "agent": AGENT_NAME, "text": tweet}))
        if args.dry_run:
            print("[DRY RUN]", tweet)
        else:
            try:
                agent.post((tweet, None))
            except Exception as exc:  # pragma: no cover - post failure
                log.error(json.dumps({
                    "event": "post_fail",
                    "agent": AGENT_NAME,
                    "text": str(exc),
                }))
    if not args.once and not args.test:
        time.sleep(300)


if __name__ == "__main__":
    main()
