import random
from agents.base import TwitterAgent
from eliza import shared_memory, llm
import inspect
from typing import Optional

def get_token_info(prompt):
    """Get token information for a prompt (stubbed for now)."""
    return {"tokens": len(prompt.split())}

class Agent1(TwitterAgent):
    """Agent1: Chaotic hype gremlin persona."""
    schedule_cron = "*/5 * * * *"  # e.g. every 5 minutes
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dummy interfaces (can be overridden in tests)
        self.llm = llm.complete  # default LLM function or stub
        if not inspect.iscoroutinefunction(self.llm):
            # Wrap sync llm.complete in an async function
            sync_llm = self.llm
            async def async_llm(prompt, *a, **kw):
                return sync_llm(prompt, *a, **kw)
            self.llm = async_llm
        self.requests = None  # requests library (or stub)
        self.persona = "an overly excited, chaotic hype gremlin who hypes everything enthusiastically"
    
    async def _build_prompt(self, message, context=None):
        """Build prompt including persona and latest context."""
        prompt = f"You are {self.persona}. "
        if context:
            prompt += f"Previous message: {context}\n"
        prompt += f"Current message: {message}"
        return prompt
    
    async def craft_post(self):
        """Generate lore-style tweet; no price logic."""
        text = self._generate_lore_tweet()
        return text, None
    
    async def post(self, content=None):
        """Post a new message (possibly using latest context)."""
        # Get latest context from shared memory (cross-engagement awareness)
        context = await shared_memory.latest()
        prompt = await self._build_prompt(content or "", context=context)
        get_token_info(prompt)  # integrate token count check (stubbed for now)
        response = await self.llm(prompt)   # asynchronous call to LLM
        # Record the post in shared memory for other agents
        await shared_memory.append_list("memory", f"Agent1: {response}")
        return response
    
    async def reply(
        self,
        tweet_id: int,
        text: str,
        *,
        dry_run: Optional[bool] = None,
    ) -> int:
        """Delegate to base but keep override for future persona flair."""
        return await super().reply(tweet_id, text, dry_run=dry_run)
    
    def _generate_lore_tweet(self):
        """Generate a simple Sproto-style meme line."""
        return "lol #HarryPotterObamaSonic10Inu" 