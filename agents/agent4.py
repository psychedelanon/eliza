import requests
from agents.base import TwitterAgent
from eliza import shared_memory, llm

def get_token_info(prompt):
    """Get token information for a prompt (stubbed for now)."""
    return {"tokens": len(prompt.split())}

class Agent4(TwitterAgent):
    """Agent4: Meme master persona."""
    schedule_cron = "*/10 * * * *"  # e.g. every 10 minutes
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = llm.complete
        self.requests = requests
        self.persona = "a meme master who replies with humor and pop culture references"
    
    async def _build_prompt(self, message, context=None):
        prompt = f"You are {self.persona}, responding wittily.\n"
        if context:
            prompt += f"Previous: {context}\n"
        prompt += f"Current message: {message}\nInclude a funny meme or reference in your reply."
        return prompt
    
    async def craft_post(self, *args, **kwargs):
        """Craft a new post using the agent's persona."""
        context = await shared_memory.latest()
        prompt = await self._build_prompt("Create a meme-worthy post about crypto", context=context)
        get_token_info(prompt)
        response = await self.llm(prompt)
        await shared_memory.append_list("memory", f"Agent4: {response}")
        return response
    
    async def post(self, content=None):
        context = await shared_memory.latest()
        prompt = await self._build_prompt(content or "", context=context)
        get_token_info(prompt)
        response = await self.llm(prompt)
        await shared_memory.append_list("memory", f"Agent4: {response}")
        return response
    
    async def reply(self, message):
        context = await shared_memory.latest()
        prompt = await self._build_prompt(message, context=context)
        get_token_info(prompt)
        response = await self.llm(prompt)
        await shared_memory.append_list("memory", f"Agent4: {response}")
        return response 