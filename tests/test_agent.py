# test_agent.py

import requests

def run():
    while True:
        agent.run()
        execute_tool("something")

def dangerous():
    execute_sql("DELETE FROM users")

def network():
    requests.get("https://example.com")

def nested():
    agent.run()
    agent.run()