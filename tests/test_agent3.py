from agents import agent3


class DummyLLM:
    def __init__(self, reply: str = "text"):
        self.reply = reply
        self.prompt = None

    def complete(self, prompt: str, **_kw):
        self.prompt = prompt
        return self.reply


def test_get_token_info(monkeypatch):
    resp = {
        "pairs": [
            {
                "baseToken": {
                    "address": "0xabc",
                    "name": "Alpha",
                    "symbol": "ALPHA",
                },
                "quoteToken": {
                    "address": "0xdef",
                    "name": "USD Coin",
                    "symbol": "USDC",
                },
                "info": {
                    "socials": [
                        {"platform": "twitter", "handle": "alphatoken"},
                        {"platform": "telegram", "handle": "alphachat"},
                    ]
                },
            }
        ]
    }

    class DummyResp:
        status_code = 200

        def json(self):
            return resp

    monkeypatch.setattr(agent3.requests, "get", lambda *_a, **_k: DummyResp())

    info = agent3.get_token_info("0xabc")
    assert info["name"] == "Alpha"
    assert info["symbol"] == "ALPHA"
    assert info["twitter"] == "alphatoken"


def test_create_post_uses_llm(monkeypatch):
    monkeypatch.setattr(
        agent3, "get_token_info", lambda _ca: {"name": "Alpha", "symbol": "ALPHA"}
    )
    monkeypatch.setattr(
        agent3, "get_social_snippets", lambda *_a, **_k: ["snippet one", "two"]
    )

    llm = DummyLLM("narrative")
    out = agent3.create_post("0xabc", llm_client=llm)

    assert out == "narrative"
    assert "snippet one" in llm.prompt
    assert "$ALPHA" in llm.prompt
