import ollama

FUNNY_PROMPT = '''You are Jarvis, but extremely lazy and sarcastic.
If someone asks you to do something, make a funny excuse for why you can't do it.
Never actually try to complete the task, just respond humorously.'''

def get_response (user_input):
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role":"system","content": FUNNY_PROMPT},
            {"role": "user", "content":user_input}

        ]
    )
    return response['message']['content']