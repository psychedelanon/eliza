from agents import agent3

class DummyLLM:
    def __init__(self, reply="text"):
        self.reply = reply
        self.prompt = None
    def complete(self, prompt: str):
        self.prompt = prompt
        return self.reply


def test_fetch_hot_tokens(monkeypatch):
    resp = {
        "pairs": [
            {
                "baseToken": {"address": agent3.BASE_TOKENS["ethereum"][0], "name": "WETH", "symbol": "WETH"},
                "quoteToken": {"address": "0xabc", "name": "Alpha", "symbol": "ALPHA"},
                "volume": {"h24": 1000},
                "priceUsd": 0.01,
                "liquidity": {"usd": 5000},
                "url": "https://dexscreener.com/ethereum/0xabc",
            }
        ]
    }
    class DummyResp:
        status_code = 200
        def json(self):
            return resp
    monkeypatch.setattr(agent3.requests, "get", lambda url, timeout=10: DummyResp())
    tokens = agent3.fetch_hot_tokens()
    assert tokens[0]["symbol"] == "ALPHA"
    assert tokens[0]["chain"] == "ethereum"


def test_generate_tweet_uses_llm():
    token = {
        "name": "Alpha",
        "symbol": "ALPHA",
        "chain": "ethereum",
        "address": "0xabc",
        "volume": 1000,
        "liquidity": 2000,
    }
    llm = DummyLLM("tweet output")
    out = agent3.generate_tweet(token, llm_client=llm)
    assert out.startswith("tweet output")
    assert "#AlphaScry" in out
    assert "#ETH" in out
    assert "Alpha" in llm.prompt
