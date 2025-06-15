import os
from typing import List

try:
    import tweepy  # type: ignore
except ImportError:  # pragma: no cover - tweepy optional
    tweepy = None

NUM_AGENTS = 18

personalities = [
    "friendly and upbeat", "sarcastic and witty", "curious and inquisitive",
    "creative storyteller", "technical and analytical", "humorous and lighthearted",
    "formal and polite", "casual and laid-back", "inspirational motivator",
    "critical thinker", "cheerful optimist", "pessimistic realist",
    "enthusiastic learner", "wise mentor", "playful joker",
    "news commentator", "poetic dreamer", "mysterious philosopher"
]

agent_profiles = [
    {"name": f"Agent{i+1}", "personality": personalities[i] if i < len(personalities) else "neutral"}
    for i in range(NUM_AGENTS)
]

class TwitterAgent:
    """Represents a single Twitter agent."""

    def __init__(self, name: str, api_key: str | None, api_secret: str | None,
                 access_token: str | None, access_secret: str | None,
                 personality: str) -> None:
        self.name = name
        self.personality = personality
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.api = None
        if tweepy and all([api_key, api_secret, access_token, access_secret]):
            self.authenticate()
        else:
            print(f"{self.name}: Tweepy unavailable or credentials missing; running in console mode")

    def authenticate(self) -> None:
        if not tweepy:
            return
        auth = tweepy.OAuth1UserHandler(self.api_key, self.api_secret, self.access_token, self.access_secret)
        self.api = tweepy.API(auth)
        print(f"{self.name}: Authenticated with Twitter API")

    def generate_content(self) -> str:
        return f"{self.name} says hello in a {self.personality} manner."

    def post_content(self, content: str) -> None:
        if self.api:
            try:
                self.api.update_status(content)
                print(f"{self.name}: Tweeted -> {content}")
            except Exception as exc:  # pragma: no cover - network interaction
                print(f"{self.name}: Failed to tweet: {exc}")
        else:
            print(f"{self.name}: Posted content -> {content}")

    def respond_to(self, other_agent: "TwitterAgent", reply_content: str | None = None) -> None:
        if reply_content is None:
            reply_content = f"@{other_agent.name} {self.name} responds in a {self.personality} way."
        if self.api:
            try:
                self.api.update_status(reply_content)
                print(f"{self.name}: Replied to {other_agent.name} -> {reply_content}")
            except Exception as exc:  # pragma: no cover - network interaction
                print(f"{self.name}: Failed to reply: {exc}")
        else:
            print(f"{self.name}: Responds to {other_agent.name} -> {reply_content}")


def create_agents(num_agents: int = NUM_AGENTS) -> List[TwitterAgent]:
    agents: List[TwitterAgent] = []
    for i, profile in enumerate(agent_profiles[:num_agents]):
        idx = i + 1
        api_key = os.getenv(f"TWITTER_AGENT{idx}_API_KEY")
        api_secret = os.getenv(f"TWITTER_AGENT{idx}_API_SECRET")
        access_token = os.getenv(f"TWITTER_AGENT{idx}_ACCESS_TOKEN")
        access_secret = os.getenv(f"TWITTER_AGENT{idx}_ACCESS_SECRET")
        agent = TwitterAgent(
            profile["name"], api_key, api_secret, access_token, access_secret, profile["personality"]
        )
        agents.append(agent)
    return agents


def run_demo() -> None:
    agents = create_agents()
    for agent in agents:
        content = agent.generate_content()
        agent.post_content(content)
    for i, agent in enumerate(agents):
        target = agents[i - 1] if i > 0 else agents[-1]
        agent.respond_to(target)


if __name__ == "__main__":
    run_demo()
