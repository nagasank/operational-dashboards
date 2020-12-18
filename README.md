# HNTS Daily Standup app

App to connect to the Snowflake database and allow drilldowns into internal data from HIS for use by Home Nursing and Therapy Services. 

## Running this application
1. In a terminal, run the following command:
```python
python index.py
```

This application stores data retrieved from the Snowflake database into a local Redis database for faster data retrieval. To run this app locally, you must also start a Redis server.

> Note:
> 1. If you get an error message like
> "`REDIS_URL` needs to be available as an environment variable."
> Then prepend the env variable `REDIS_URL=redis://127.0.0.1:6379` on every command: 
> REDIS_URL=redis://127.0.0.1:6379 python index.py
> REDIS_URL=redis://127.0.0.1:6379 celery -A index:celery_instance worker

## References
- [Dash Snapshot Engine documentation](dash-ide-internal.plotly.host/Docs/dash-snapshots)
- [Dash Design Kit documentation](dash-ide-internal.plotly.host/Docs/dash-design-kit)
- [More sample apps & templates](dash-ide-internal.plotly.host/Docs/templates)
