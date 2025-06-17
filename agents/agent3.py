import argparse
import html
import logging
import re
from typing import List, Dict, Optional

import requests

from eliza import llm

log = logging.getLogger("agent3")


def resolve_metadata(contract: str) -> Dict[str, Optional[str]]:
    """Return token metadata using DexScreener search."""
    url = f"https://api.dexscreener.com/latest/dex/search/?q={contract}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        data = resp.json()
    except Exception as exc:  # pragma: no cover - network failure
        raise RuntimeError(f"search failed: {exc}") from exc

    pairs = data.get("pairs") or []
    if not pairs:
        raise ValueError("token not found")
    pair = pairs[0]
    if pair.get("baseToken", {}).get("address", "").lower() == contract.lower():
        token = pair.get("baseToken", {})
    else:
        token = pair.get("quoteToken", {})
    socials = []
    for entry in pair.get("info", {}).get("socials", []):
        handle = entry.get("handle") or entry.get("url")
        if handle:
            socials.append(handle)
    return {
        "name": token.get("name") or token.get("symbol") or "Unknown",
        "symbol": token.get("symbol") or token.get("name") or "UNKNOWN",
        "socials": socials,
    }


def fetch_social_snippets(symbol: str, name: str) -> List[str]:
    """Fetch recent tweet snippets using Nitter. Falls back to placeholders."""
    snippets: List[str] = []
    terms = [f"${symbol}", name]
    for term in terms:
        url = f"https://nitter.net/search?f=tweets&q={requests.utils.quote(term)}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                continue
            html_text = resp.text
            for raw in re.findall(r'<p class="tweet-content.*?">(.*?)</p>', html_text, re.S):
                text = re.sub(r"<.*?>", "", raw)
                text = html.unescape(text)
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    snippets.append(text)
                if len(snippets) >= 5:
                    break
        except Exception:  # pragma: no cover - network failure
            continue
        if len(snippets) >= 5:
            break
    if not snippets:
        snippets = [
            f"Whales mentioning ${symbol}",
            f"Telegram chats buzzing about {name}",
            "Rumors of dev news soon",
        ]
    return snippets[:5]


def generate_narrative(name: str, symbol: str, snippets: List[str], llm_client: Optional[object] = None) -> str:
    prompt = (
        f"Token: {name} (${symbol}) is trending.\n"
        "Recent chatter:\n"
    )
    for s in snippets:
        prompt += f"- {s}\n"
    prompt += (
        "\nIn a single witty paragraph, summarize the hype like @RickBurpBot."
    )
    if llm_client:
        result = llm_client.complete(prompt)
    else:
        result = llm.complete(prompt, max_tokens=120)
    return str(result).strip()


def create_narrative(contract: str, llm_client: Optional[object] = None) -> str:
    meta = resolve_metadata(contract)
    snippets = fetch_social_snippets(meta["symbol"], meta["name"])
    return generate_narrative(meta["name"], meta["symbol"], snippets, llm_client)


def main() -> None:
    parser = argparse.ArgumentParser(description="Token narrative agent")
    parser.add_argument("--ca", "--contract", dest="contract", required=True, help="token contract address")
    parser.add_argument("--dry-run", action="store_true", help="print result instead of posting")
    args = parser.parse_args()

    text = create_narrative(args.contract)
    if args.dry_run:
        print(f"DRY RUN \u2014 Narrative:\n\"{text}\"")
    else:
        print(text)


if __name__ == "__main__":
    main()
