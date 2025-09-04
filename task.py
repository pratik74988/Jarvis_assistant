import os 
import mss, base64
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash", tempature = 0, google_api_key = google_api_key)

def capture_screenshot(output_path="screen.png"):
    with mss.mss() as sct:
        sct.shot(output = output_path)
    return output_path

def screenshot_to_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode("utf-8")

def solve_from_screenshot():
    path = capture_screenshot()
    img_b64 = screenshot_to_base64(path)

    message = HumanMessage(
        content=[
        {"type": "text", "text": "User is solving a LeetCode problem in this screenshot. Read and solve."},
        {"type": "image_url", "image_url": f"data:image/png;base64,{img_b64}"},
    ]
    )
    response = llm.invoke([message])
    return response

solution = solve_from_screenshot()
print("Gemini Says\n", solution)

