import types
from agents import agent3

class DummyLLM:
    def __init__(self, reply="tweet"):
        self.reply = reply
        self.prompt = None
    def complete(self, prompt):
        self.prompt = prompt
        return self.reply

def test_generate_tweet_appends_hashtags():
    token = {
        "name": "Token",
        "symbol": "TKN",
        "chain": "ethereum",
        "address": "0x1",
        "volume": 100,
        "price": 0.1,
        "liquidity": 1000,
        "holders": 10,
        "age": "1h",
        "chart": "http://chart",
    }
    tweet = agent3.generate_tweet(token, DummyLLM("alpha"))
    assert "#AlphaScry" in tweet
    assert "#ETH" in tweet

def test_fetch_hot_tokens_sort(monkeypatch):
    resp_eth = {
        "pairs": [
            {
                "baseToken": {"address": agent3.ETH_BASES[0]},
                "quoteToken": {"address": "0xAAA", "name": "A", "symbol": "A"},
                "volume": {"h24": 200},
                "priceUsd": "0.1",
                "liquidity": {"usd": 1000},
                "url": "http://chart1",
            },
            {
                "baseToken": {"address": agent3.ETH_BASES[0]},
                "quoteToken": {"address": "0xBBB", "name": "B", "symbol": "B"},
                "volume": {"h24": 100},
                "priceUsd": "0.05",
                "liquidity": {"usd": 500},
                "url": "http://chart2",
            },
        ]
    }
    def dummy_get(url, timeout=10):
        class Resp:
            status_code = 200
            def json(self_inner):
                return resp_eth
        return Resp()
    monkeypatch.setattr(agent3.requests, "get", dummy_get)
    tokens = agent3.fetch_hot_tokens()
    assert tokens[0]["symbol"] == "A"
    assert tokens[0]["volume"] == 200
