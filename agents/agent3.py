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
            token = {}
            if base_addr in [a.lower() for a in bases]:
                t = pair.get("quoteToken", {})
            elif quote_addr in [a.lower() for a in bases]:
                t = pair.get("baseToken", {})
            else:
                continue
            token["address"] = t.get("address")
            if not token["address"] or token["address"].lower() in [a.lower() for a in bases]:
                continue
            token["name"] = t.get("name") or t.get("symbol") or "Unknown"
            token["symbol"] = t.get("symbol") or t.get("name") or "UNKNOWN"
            token["chain"] = chain
            volume_data = pair.get("volume", {})
            token["volume"] = volume_data.get("h24", 0)
            price_usd = pair.get("priceUsd") or pair.get("price")
            try:
                token["price"] = float(price_usd) if price_usd is not None else None
            except Exception:
                token["price"] = None
            liquidity_data = pair.get("liquidity", {})
            token["liquidity"] = liquidity_data.get("usd")
            token["holders"] = None
            token["age"] = None
            token["chart"] = pair.get("url", f"https://dexscreener.com/{chain}/{token['address']}")
            tokens.append(token)
    unique = {}
    for t in tokens:
        key = (t["chain"], t["address"].lower())
        if key not in unique or (t.get("volume") or 0) > (unique[key].get("volume") or 0):
            unique[key] = t
    return sorted(unique.values(), key=lambda x: x.get("volume", 0), reverse=True)


def generate_tweet(token: Dict, llm_client: Optional[object] = None) -> str:
    name = token.get("name", "")
    symbol = token.get("symbol", "")
    chain = token.get("chain", "")
    addr = token.get("address", "")
    volume = token.get("volume", 0)
    price = token.get("price")
    liquidity = token.get("liquidity")
    holders = token.get("holders")
    age = token.get("age")
    chart = token.get("chart", "")
    prompt = (
        "Here is a token's data:\n"
        f"Name: {name}\nSymbol: {symbol}\nChain: {chain}\nContract: {addr}\n"
        f"24h Volume: {volume}\n"
    )
    if price is not None:
        prompt += f"Price: ${price}\n"
    if liquidity is not None:
        prompt += f"Liquidity: ${liquidity}\n"
    if holders is not None:
        prompt += f"Holders: {holders}\n"
    if age is not None:
        prompt += f"Launched: {age} ago\n"
    prompt += f"Chart: {chart}\n\n"
    prompt += (
        "Write a short tweet (one paragraph, under 280 chars) about this token. "
        "Capture its vibe and sentiment (hype or caution). If it's a meme/meta token, mention it. "
        "Include liquidity or notable buys if relevant. Use an influencer tone with emojis. "
        "Include the token's ticker (e.g. $" + symbol + ") and a partial contract address. "
        "End with hashtags #AlphaScry and the chain (e.g. #ETH, #BSC)."
    )
    if llm_client:
        result = llm_client.complete(prompt)
    else:
        result = llm.complete(prompt, max_tokens=120)
    tweet = str(result).strip()
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    chain_tag = CHAIN_TAGS.get(chain.lower(), chain.title())
    hashtags = []
    if "#AlphaScry" not in tweet:
        hashtags.append("#AlphaScry")
    if chain_tag and f"#{chain_tag}" not in tweet:
        hashtags.append(f"#{chain_tag}")
    if hashtags:
        tweet = tweet.rstrip() + " " + " ".join(hashtags)
    return tweet


def run_once(*, dry_run: bool = False, test: bool = False) -> None:
    if test:
        hot_tokens = [
            {
                "name": "TestToken",
                "symbol": "TST",
                "chain": "ethereum",
                "address": "0xTEST",
                "volume": 12345,
                "price": 0.001,
                "liquidity": 50000,
                "holders": 300,
                "age": "2 days",
                "chart": "https://dexscreener.com/ethereum/0xTEST",
            }
        ]
    else:
        hot_tokens = fetch_hot_tokens()
    if not hot_tokens:
        log.info(json.dumps({"event": "no_signals", "agent": AGENT_NAME}))
        return
    agent = TwitterAgent(idx=3, name=AGENT_NAME, personality="AlphaScry", dry_run=dry_run)
    for token in hot_tokens:
        try:
            if test:
                tweet_text = (
                    f"[TEST] ${token['symbol']} vol ${token['volume']:.0f} liq ${token['liquidity']:.0f} #AlphaScry #{CHAIN_TAGS.get(token['chain'], token['chain'].upper())}"
                )
            else:
                tweet_text = generate_tweet(token)
        except Exception as exc:
            log.error(
                json.dumps(
                    {
                        "event": "error_generate",
                        "agent": AGENT_NAME,
                        "text": str(exc),
                    }
                )
            )
            continue
        log.info(json.dumps({"event": "tweet_content", "agent": AGENT_NAME, "text": tweet_text}))
        if dry_run:
            print(f"[DRY RUN] {tweet_text}")
        else:
            try:
                agent.post((tweet_text, None), dry_run=False)
                log.info(json.dumps({"event": "posted", "agent": AGENT_NAME, "text": tweet_text}))
            except Exception as exc:  # pragma: no cover - network failure
                log.error(
                    json.dumps(
                        {
                            "event": "error_post",
                            "agent": AGENT_NAME,
                            "text": str(exc),
                        }
                    )
                )


def main() -> None:
    parser = argparse.ArgumentParser(description="AlphaScry token monitor")
    parser.add_argument("--once", action="store_true", help="run one cycle and exit")
    parser.add_argument("--dry-run", action="store_true", help="do not post to twitter")
    parser.add_argument("--test", action="store_true", help="use mocked data")
    args = parser.parse_args()
    if args.once or args.test:
        run_once(dry_run=args.dry_run, test=args.test)
        return
    while True:
        run_once(dry_run=args.dry_run)
        time.sleep(300)


if __name__ == "__main__":
    main()
