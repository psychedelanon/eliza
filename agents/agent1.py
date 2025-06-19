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
        """Post a new message using the base class posting logic."""
        # If content is provided, use it; otherwise generate new content
        if content is None:
            text, img = await self.craft_post()
            content = (text, img)
        
        # Use the base class posting logic which handles v2 API, rate limits, etc.
        tweet_id = await super().post(content)
        
        # Record the post in shared memory for other agents if successful
        if tweet_id and tweet_id != -1:
            if isinstance(content, tuple):
                text = content[0]
            else:
                text = str(content)
            await shared_memory.append_list("memory", f"Agent1: {text}")
        
        return tweet_id
    
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
        """Generate a quality-compliant chaotic hype tweet."""
        import random
        
        hype_phrases = [
            "OMG, HAVE YOU HEARD ABOUT $BITCOIN?! 🎉🎉 It's like the ultimate mashup of all the epicness! I mean, we're talking about wizards, former presidents, and speedy blue hedgehogs ALL IN ONE! 🤯💥 #HarryPotterObamaSonic10Inu",
            "YOOO $BITCOIN is absolutely INSANE! 🚀🚀 Picture this: Harry Potter casting spells while Obama gives speeches and Sonic collects rings! The chaos is REAL and I'm HERE FOR IT! 🧙‍♂️⚡ #HarryPotterObamaSonic10Inu",
            "GUYS. GUYS. $BITCOIN is the most chaotic energy I've ever witnessed! 🔥🔥 It's like someone threw Harry Potter, Obama, and Sonic into a blender and created PURE MAGIC! WHO EVEN THINKS OF THIS?! 🤪✨ #HarryPotterObamaSonic10Inu",
            "I CANNOT EVEN with $BITCOIN right now! 🤯🎭 We've got presidential wisdom, magical spells, and supersonic speed all wrapped into one beautiful disaster! This is peak internet culture! 🌟💫 #HarryPotterObamaSonic10Inu",
            "BREAKING: $BITCOIN has officially broken my brain! 🧠💥 How do you even combine Harry Potter, Obama, and Sonic?! It's like the universe's greatest crossover event! I'm LIVING for this chaos! 🎪🎨 #HarryPotterObamaSonic10Inu"
        ]
        
        return random.choice(hype_phrases) 