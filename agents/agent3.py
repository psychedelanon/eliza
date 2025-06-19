import requests
from agents.base import TwitterAgent
from eliza import shared_memory, llm
import inspect

def get_token_info(prompt):
    """Get token information for a prompt (stubbed for now)."""
    return {"tokens": len(prompt.split())}

class Agent3(TwitterAgent):
    """Agent3: Lore-teller persona."""
    schedule_cron = "*/15 * * * *"  # e.g. every 15 minutes
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = llm.complete
        if not inspect.iscoroutinefunction(self.llm):
            sync_llm = self.llm
            async def async_llm(prompt, *a, **kw):
                return sync_llm(prompt, *a, **kw)
            self.llm = async_llm
        self.requests = requests
        self.persona = "a wise lore-teller who speaks in rich, narrative descriptions"
    
    async def _build_prompt(self, message, context=None):
        prompt = f"You are {self.persona}, weaving context into a story.\n"
        if context:
            prompt += f"(Previously: {context})\n"
        prompt += f"Message to respond to: \"{message}\""
        return prompt
    
    async def craft_post(self, *args, **kwargs):
        """Craft a new post using the agent's persona."""
        context = await shared_memory.latest()
        prompt = await self._build_prompt("Create a lore-rich post about crypto", context=context)
        get_token_info(prompt)
        response = await self.llm(prompt)
        await shared_memory.append_list("memory", f"Agent3: {response}")
        return response, None
    
    async def post(self, content=None):
        context = await shared_memory.latest()
        prompt = await self._build_prompt(content or "", context=context)
        get_token_info(prompt)
        response = await self.llm(prompt)
        await shared_memory.append_list("memory", f"Agent3: {response}")
        return response
    
    async def reply(self, message):
        context = await shared_memory.latest()
        prompt = await self._build_prompt(message, context=context)
        get_token_info(prompt)
        response = await self.llm(prompt)
        await shared_memory.append_list("memory", f"Agent3: {response}")
        return response
    
    async def react_to_event(self, tweet_id: str, delay: float = 0.0) -> None:
        """Use the base class implementation for consistent engagement."""
        return await super().react_to_event(tweet_id, delay) 