import random
from agents.base import TwitterAgent
from eliza import shared_memory, llm

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
        self.requests = None  # requests library (or stub)
        self.persona = "an overly excited, chaotic hype gremlin who hypes everything enthusiastically"
    
    async def _build_prompt(self, message, context=None):
        """Build prompt including persona and latest context."""
        prompt = f"You are {self.persona}. "
        if context:
            prompt += f"Previous message: {context}\n"
        prompt += f"Current message: {message}"
        return prompt
    
    async def craft_post(self, *args, **kwargs):
        """Craft a new post using the agent's persona."""
        context = await shared_memory.latest()
        prompt = await self._build_prompt("Create an exciting post about crypto", context=context)
        get_token_info(prompt)  # integrate token count check (stubbed for now)
        response = await self.llm(prompt)   # asynchronous call to LLM
        # Record the post in shared memory for other agents
        await shared_memory.append_list("memory", f"Agent1: {response}")
        return response
    
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
    
    async def reply(self, message):
        """Reply to a given message (from another agent or user)."""
        context = await shared_memory.latest()
        prompt = await self._build_prompt(message, context=context)
        get_token_info(prompt)
        response = await self.llm(prompt)
        await shared_memory.append_list("memory", f"Agent1: {response}")
        return response 