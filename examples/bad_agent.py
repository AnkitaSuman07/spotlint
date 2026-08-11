import requests

API_KEY = "sk-production-example-secret-123456"

def customer_agent(user_input):
    while True:
        result = search_tool(user_input)
        response = requests.get("https://example.com/customer")
        return response.json()


def search_tool(query):
    return invoke_agent(query)
