from prometheus_client import Counter, start_http_server

TWEETS_POSTED = Counter('tweets_posted_total', 'Total tweets posted')
REPLIES_POSTED = Counter('replies_posted_total', 'Total replies posted')
OPENAI_CALLS = Counter('openai_calls_total', 'Total OpenAI text generation calls')


def init_metrics(port: int = 8000) -> None:
    start_http_server(port)
