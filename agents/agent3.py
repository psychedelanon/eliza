from agents.base import TwitterAgent

class Agent3(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def craft_post(self, *args, **kwargs):
        return "Agent3's crafted post" 