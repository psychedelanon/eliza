class SimpleCounter:
    def __init__(self):
        self._value = 0

    def inc(self):
        self._value += 1

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

# Simple metrics for testing
TWEETS_POSTED = SimpleCounter()
REPLIES_POSTED = SimpleCounter()
OPENAI_CALLS = SimpleCounter()

def init_metrics(port=8000):
    """No-op for testing"""
    pass
