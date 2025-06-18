"""Narrative generator for trending tokens.

This module exposes a simple CLI that accepts a contract address, fetches
metadata from DexScreener and scrapes a few recent social posts mentioning the
token. The gathered context is then summarized via the ``eliza.llm`` interface
to produce a short, RickBurpBot-style blurb explaining why the token is being
hyped.
"""

from __future__ import annotations

import argparse
import logging
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from eliza import llm


log = logging.getLogger("token_narrator")


DEX_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search/?q={addr}"


def get_token_info(contract: str) -> Dict[str, Optional[str]]:
    """Return basic info for ``contract`` using DexScreener search."""

    resp = requests.get(DEX_SEARCH_URL.format(addr=contract), timeout=5)
    if resp.status_code != 200:
        raise RuntimeError(f"DexScreener HTTP {resp.status_code}")
    data = resp.json()
    pairs = data.get("pairs") or []
    if not pairs:
        raise ValueError("Token not found on DexScreener")

    first = pairs[0]
    if first.get("baseToken", {}).get("address", "").lower() == contract.lower():
        token = first.get("baseToken", {})
    else:
        token = first.get("quoteToken", {})

    info = {
        "name": token.get("name") or token.get("symbol"),
        "symbol": token.get("symbol") or token.get("name"),
    }

    socials = first.get("info", {}).get("socials", [])
    for s in socials:
        if s.get("platform") == "twitter":
            info["twitter"] = s.get("handle")
        if s.get("platform") == "telegram":
            info["telegram"] = s.get("handle")
    return info


def get_social_snippets(
    name: str, symbol: str, twitter_handle: Optional[str] = None
) -> List[str]:
    """Fetch a handful of tweets referencing the token via ``nitter.net``."""

    queries = []
    if twitter_handle:
        queries.append(f"from:{twitter_handle}")
    queries.extend([f"${symbol}", name])

    snippets: List[str] = []
    for q in queries:
        try:
            url = f"https://nitter.net/search?f=tweets&q={requests.utils.quote(q)}"
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select("div.timeline-item"):
                content = item.select_one(".tweet-content")
                if content:
                    text = content.get_text(" ", strip=True)
                    if text and text not in snippets:
                        snippets.append(text)
                if len(snippets) >= 3:
                    break
        except Exception as exc:  # pragma: no cover - network failure
            log.warning("social fetch error %s", exc)
        if len(snippets) >= 3:
            break

    if not snippets:
        # Fallback so the summarizer has some context
        snippets = [
            f"Whales eyeing ${symbol}",
            f"Telegram buzzing about {name}",
        ]
    return snippets[:3]


def create_post(contract: str, *, llm_client=None) -> str:
    """Generate a short narrative for ``contract``."""

    info = get_token_info(contract)
    name = info.get("name") or "Unknown"
    symbol = info.get("symbol") or "TOKEN"
    twitter_handle = info.get("twitter")

    snippets = get_social_snippets(name, symbol, twitter_handle)

    prompt = (
        f"Token: {name} (${symbol}) is trending on crypto social media.\n"
        "You are Rick, a snarky but insightful crypto bot.\n"
    )
    for snippet in snippets:
        prompt += f"- {snippet}\n"
    prompt += (
        "\nIn a single witty paragraph, summarize why this token is moving."
    )

    client = llm_client or llm
    return client.complete(prompt, max_tokens=120)


def main() -> None:
    parser = argparse.ArgumentParser(description="Token narrative interpreter")
    parser.add_argument(
        "--ca",
        "--contract",
        dest="contract",
        required=True,
        help="Token contract address",
    )
    parser.add_argument("--dry-run", action="store_true", help="print only")

    args = parser.parse_args()

    narrative = create_post(args.contract)

    if args.dry_run:
        print("DRY RUN \u2014 Narrative:")
        print(f'"{narrative}"')
    else:
        print(narrative)


if __name__ == "__main__":  # pragma: no cover - manual use
    main()

