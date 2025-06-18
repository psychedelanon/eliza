import pytest
from agents import agent3


class DummyLLM:
    def __init__(self, reply: str = "text"):
        self.reply = reply
        self.prompt = None

    def complete(self, prompt: str, **_kw):
        self.prompt = prompt
        return self.reply


@pytest.mark.asyncio
async def test_get_token_info(monkeypatch):
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

    # Create agent instance and monkeypatch requests
    agent = agent3.Agent3(name="test", personality="test", dry_run=True)
    monkeypatch.setattr(agent, "requests", type('MockRequests', (), {
        'get': lambda *_a, **_k: DummyResp()
    })())
    
    # Test get_token_info function
    result = agent3.get_token_info("test prompt")
    assert "tokens" in result
    assert result["tokens"] > 0


@pytest.mark.asyncio
async def test_create_post_uses_llm(monkeypatch):
    # Create agent instance and monkeypatch llm
    agent = agent3.Agent3(name="test", personality="test", dry_run=True)
    monkeypatch.setattr(agent, "llm", lambda prompt: "Test response")
    monkeypatch.setattr(agent3, "get_token_info", lambda _ca: {"name": "Alpha", "symbol": "ALPHA"})
    
    # Mock the llm to be async
    async def mock_llm(prompt):
        return "Test response"
    
    monkeypatch.setattr(agent, "llm", mock_llm)
    
    result = await agent.craft_post()
    assert "Test response" in result
