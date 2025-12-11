import json

import requests

url = "http://localhost:11434/api/chat"

messages = []

while True:
    user_input = input("You: ")
    messages.append({"role": "user", "content": user_input})

    response = requests.post(url, json={
        "model": "gemma2:2b",
        "messages": messages
    }, stream=True)

    print("AI: ", end="")
    ai_msg = ""

    for line in response.iter_lines():
        if line:
            content = json.loads(line.decode()).get("message", {}).get("content", "")
            print(content, end="", flush=True)
            ai_msg += content

    print("\n")
    messages.append({"role": "assistant", "content": ai_msg})
