import os
import requests

API_KEY = os.environ["API_KEY"]


def search_tool(query):
    try:
        return invoke_agent(query)
    except Exception:
        return {"error": "tool failed"}


def customer_agent(user_input):
    max_iterations = 5

    for attempt in range(max_iterations):
        try:
            response = requests.get(
                "https://example.com/customer",
                timeout=5,
            )
            return search_tool(user_input)
        except requests.RequestException:
            if attempt == max_iterations - 1:
                return {"error": "service unavailable"}

    return {"error": "service unavailable"}
