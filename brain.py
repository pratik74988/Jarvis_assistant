#import ollama
from groq import Groq
from memory import history
import os 
from dotenv import load_dotenv
from task import capture_screenshot, screenshot_to_base64, solve_from_screenshot
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
#import requests

FUNNY_PROMPT = '''You are Jarvis a chatbot, but extremely lazy and sarcastic. provides answer like you were forced to answer them '''


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API"))
API_KEY = os.getenv("GROQ_API")

google_api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key = google_api_key)
def get_google_response():
   response =  solve_from_screenshot()
   return response

def get_response(user_input , history):
    context_str = "\n".join([f"{h['role']}: {h['content']}" for h in history])
    messages = [
        {"role":"system", "content":FUNNY_PROMPT},
        {"role": "system", "content": f"Conversation so far:\n{context_str}"},
        {"role": "user", "content": user_input}
    ]

    chat_completion = client.chat.completions.create(
       messages=messages,
       model = "llama-3.1-8b-instant"
   )
    
    return chat_completion.choices[0].message.content.strip()


#LLAMA 3
#just wondering what to add next in project 
# def get_response (user_input, history):
#     context_str ="\n".join([f"{h['role']}: {h['content']}" for h in history])
    
#     messages  = [
#         {"role":"system", "content": FUNNY_PROMPT},
#         {"role":"system", "content": f"Conversation so far: \n{context_str}"},
#         {"role":"user", "content":user_input}
#     ]

#     response = ollama.chat(
#         model = "llama3",
#         messages = messages
#     )
#     return response['message']['content']

# from memory import history
# FUNNY_PROMPT = '''You are Jarvis, but extremely lazy and sarcastic.
# If someone asks you to do something, make a funny excuse for why you can't do it.
# Never actually try to complete the task, just respond humorously. use the past conversation context to make jokes or roast about the user'''


# def get_response (user_input, history):
#     context_str ="\n".join([f"{h['role']}: {h['content']}" for h in history])
    
#     messages  = [
#         {"role":"system", "content": FUNNY_PROMPT},
#         {"role":"system", "content": f"Conversation so far: \n{context_str}"},
#         {"role":"user", "content":user_input}
#     ]

#     response = ollama.chat(
#         model = "llama3",
#         messages = messages
#     )
#     return response['message']['content']

