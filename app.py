import dash
import redis
import os

app = dash.Dash(__name__, suppress_callback_exceptions=True)
redis_instance = redis.StrictRedis.from_url(
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
)
