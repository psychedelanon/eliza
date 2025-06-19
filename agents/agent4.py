import requests
from agents.base import TwitterAgent
from eliza import shared_memory, llm
import inspect
from typing import Optional

def get_token_info(prompt):
    """Get token information for a prompt (stubbed for now)."""
    return {"tokens": len(prompt.split())}

class Agent4(TwitterAgent):
    """Agent4: Meme master persona."""
    schedule_cron = "*/10 * * * *"  # e.g. every 10 minutes
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = llm.complete
        if not inspect.iscoroutinefunction(self.llm):
            sync_llm = self.llm
            async def async_llm(prompt, *a, **kw):
                return sync_llm(prompt, *a, **kw)
            self.llm = async_llm
        self.requests = requests
        self.persona = "a meme master who replies with humor and pop culture references"
    
    async def _build_prompt(self, message, context=None):
        prompt = f"You are {self.persona}, responding wittily.\n"
        if context:
            prompt += f"Previous: {context}\n"
        prompt += f"Current message: {message}\nInclude a funny meme or reference in your reply."
        return prompt
    
    async def craft_post(self, *args, **kwargs):
        # Your AlphaScry logic here
        text = "AlphaScry post text here"  # Replace with your real logic
        return text, None
    
    async def post(self, content=None):
        context = await shared_memory.latest()
        prompt = await self._build_prompt(content or "", context=context)
        get_token_info(prompt)
        response = await self.llm(prompt)
        await shared_memory.append_list("memory", f"Agent4: {response}")
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