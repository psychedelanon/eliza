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
        """Generate alpha-focused market analysis tweets."""
        import random
        
        alpha_tweets = [
            "🚨 ALPHA ALERT: $BITCOIN technical analysis shows massive convergence patterns! 📊⚡ Three legendary forces (wizard magic, presidential leadership, sonic speed) creating unprecedented market dynamics! This is not financial advice! 🔥 #HarryPotterObamaSonic10Inu",
            "📈 MARKET SIGNAL: $BITCOIN showing unusual correlation patterns! 🎯💫 When you combine Hogwarts mysticism with White House strategy and Green Hill momentum, you get pure alpha! Chart patterns looking spicy! 🌶️ #HarryPotterObamaSonic10Inu",
            "⚡ ALPHA INSIGHT: $BITCOIN momentum building across multiple timeframes! 📊🔮 The trinity of magic, leadership, and speed creates unique market positioning! Always DYOR but the signs are everywhere! 🚀 #HarryPotterObamaSonic10Inu",
            "🎯 SIGNAL UPDATE: $BITCOIN showing breakout potential! 📈✨ Three-way convergence of wizard energy, presidential wisdom, and supersonic velocity! The charts don't lie - something big is brewing! 🌊 #HarryPotterObamaSonic10Inu",
            "🔥 ALPHA DROP: $BITCOIN technical setup looking absolutely wild! 📊⚡ When Hogwarts meets the Oval Office meets Mobius loops, you get next-level market dynamics! Keep your eyes peeled! 👀 #HarryPotterObamaSonic10Inu"
        ]
        
        return random.choice(alpha_tweets), None
    
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
            await shared_memory.append_list("memory", f"Agent4: {text}")
        
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