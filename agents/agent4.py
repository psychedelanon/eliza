from agents.base import TwitterAgent

class Agent4(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def craft_post(self, *args, **kwargs):
        return "Agent4's crafted post" 