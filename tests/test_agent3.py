from agents import agent3

class DummyLLM:
    def __init__(self, reply="text"):
        self.reply = reply
        self.prompt = None
    def complete(self, prompt: str):
        self.prompt = prompt
        return self.reply

def test_resolve_metadata(monkeypatch):
    resp = {"pairs": [{
        "baseToken": {"address": "0x1", "name": "Token", "symbol": "TKN"},
        "quoteToken": {"address": "0x2", "name": "Base", "symbol": "BASE"},
        "info": {"socials": [{"platform": "twitter", "handle": "tokentw"}]}
    }]}
    class DummyResp:
        status_code = 200
        def json(self):
            return resp
    monkeypatch.setattr(agent3.requests, "get", lambda url, timeout=10: DummyResp())
    meta = agent3.resolve_metadata("0x1")
    assert meta["name"] == "Token"
    assert meta["symbol"] == "TKN"
    assert "tokentw" in meta["socials"]

def test_fetch_social_snippets(monkeypatch):
    html = '<p class="tweet-content media-body">cool $TKN moon</p>'
    class DummyResp:
        status_code = 200
        text = html
    monkeypatch.setattr(agent3.requests, "get", lambda url, timeout=5: DummyResp())
    snippets = agent3.fetch_social_snippets("TKN", "Token")
    assert snippets[0] == "cool $TKN moon"

def test_generate_narrative_uses_llm():
    snippets = ["one", "two"]
    llm = DummyLLM("narrative")
    out = agent3.generate_narrative("Token", "TKN", snippets, llm)
    assert out == "narrative"
    assert "one" in llm.prompt
