import requests
from agents.base import TwitterAgent
from eliza import shared_memory, llm
import inspect
from typing import Optional

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
        import random
        
        lore_tweets = [
            "In the ancient scrolls of crypto lore, it is written that $BITCOIN shall unite the magical realms of Hogwarts with the wisdom of presidential leadership and the speed of blue lightning! 🧙‍♂️⚡ The prophecy unfolds before our very eyes! #HarryPotterObamaSonic10Inu",
            "Behold, the legendary tale of $BITCOIN! 📜✨ Three mighty forces converged in the digital realm: the boy wizard's courage, the president's hope, and the hedgehog's determination! Together they forge a new chapter in crypto history! 🌟 #HarryPotterObamaSonic10Inu",
            "Long ago, the elders foretold of $BITCOIN - a mystical fusion where magic meets leadership meets supersonic adventure! 🏰🦔 The stars have aligned, and the legend lives on through blockchain technology! 🔮💫 #HarryPotterObamaSonic10Inu",
            "The chronicles speak of $BITCOIN, where three worlds collide in perfect harmony! 📖⚡ From the halls of Hogwarts to the White House to Green Hill Zone - destiny calls! The greatest crossover story ever told! 🎭🌈 #HarryPotterObamaSonic10Inu",
            "As foretold in the ancient crypto prophecies, $BITCOIN emerges as the chosen token! 🔥📚 When wizardry, presidential wisdom, and supersonic speed unite, legends are born! The multiverse has blessed us! 🌟✨ #HarryPotterObamaSonic10Inu"
        ]
        
        return random.choice(lore_tweets), None
    
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
            await shared_memory.append_list("memory", f"Agent3: {text}")
        
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