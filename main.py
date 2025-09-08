# ========================================================================
# Imports
# ========================================================================
import streamlit as st
import time
import logging
import threading
import keyboard 

from listener import listen
from speaker import speak, beep
from brain import get_response, get_google_response
from task import solve_from_screenshot, type_solution
from memory import (
    add_to_history,
    get_context,
    extract_important_parts,
    should_store,
    store_long_term_memory,
    recall_long_term_memory,
    should_trigger_screen_mechanism,
)

# ========================================================================
# Logging Setup
# ========================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Jarvis")

if "logs" not in st.session_state:
    st.session_state.logs = []

def log_to_ui(message, level="INFO"):
    if level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.debug(message)

    st.session_state.logs.append(f"[{level}] {message}")
    # Cap logs to avoid unbounded growth in the UI/session
    if len(st.session_state.logs) > 1000:
        st.session_state.logs = st.session_state.logs[-1000:]

# ========================================================================
# Session State Initialization
# ========================================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False
if "waiting" not in st.session_state:
    st.session_state.waiting = False  # tracks if bot is replying

# ========================================================================
# Sidebar
# ========================================================================
st.sidebar.header("⚙️ Settings")
voice_mode = st.sidebar.checkbox("Enable Voice Mode", value=False)
speaker_mode = st.sidebar.toggle("🔊 Speaker Mode")
if st.sidebar.button("🔴 Toggle Live Mode"):
    st.session_state.live_mode = not st.session_state.live_mode

st.sidebar.markdown("### 📸 Screenshot Feature")
st.sidebar.markdown("Try saying:")
st.sidebar.markdown("- 'take a screenshot'")
st.sidebar.markdown("- 'what do you see?'")
st.sidebar.markdown("- 'analyze my screen'")
st.sidebar.markdown("- 'capture screen'")

# ========================================================================
# Layout
# ========================================================================
left, right = st.columns([3, 1])  # chat left, logs right

with left:
    st.title("Jarvis V0.0 🎙️ 📸")

    # --- Chat Display ---
    chat_container = st.container()
    with chat_container:
        for role, text in st.session_state.chat_history:
            with st.chat_message("user" if role == "user" else "assistant"):
                st.markdown(text)

    # --- Input Area pinned at bottom ---
    user_input = st.chat_input("Type here...")

with right:
    st.subheader("📜 Logs")
    log_text = "\n".join(st.session_state.logs[-200:])
    st.text_area("Logs", log_text, height=300, disabled=True, label_visibility="collapsed")

# ========================================================================
# Processing
# ========================================================================
def process_input(user_input):
    log_to_ui(f"Received input: {user_input}")
    st.session_state.waiting = True

    # Exit condition
    if any(x in user_input.lower() for x in ["bye", "goodbye", "exit"]):
        response = "Shutting down... but not because you told me to. Totally my own idea."
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", response))
        speak(response)
        st.session_state.waiting = False
        st.stop()

    # Short-term memory
    log_to_ui("Extracting important parts")
    important_user_text = extract_important_parts(user_input)
    add_to_history("user", important_user_text)

    # Long-term memory
    if should_store(user_input):
        log_to_ui("Storing input in long-term memory")
        store_long_term_memory(user_input, role="user")

    log_to_ui("Recalling memory")
    past_memories = recall_long_term_memory(user_input, top_k=3)
    memory_context = "\n".join(past_memories[0]) if past_memories else ""

    # Full context
    full_context = get_context()
    if memory_context:
        full_context.append({"role": "memory", "content": memory_context})

    # Response
    if not should_trigger_screen_mechanism(user_input):
        log_to_ui("LLM response")
        response = get_response(user_input, full_context)
    else:
        log_to_ui("Google response")
        response = get_google_response()

    add_to_history("assistant", response)
    st.session_state.chat_history.append(("user", user_input))

    # Typing effect
    with st.chat_message("assistant"):
        placeholder = st.empty()
        typed_text = ""
        for char in response:
            typed_text += char
            placeholder.markdown(typed_text)
            time.sleep(0.02)

    st.session_state.chat_history.append(("assistant", response))
    st.session_state.waiting = False

    if speaker_mode:
        speak(response)

# ========================================================================
# Handle Input
# ========================================================================
if user_input:
    process_input(user_input)

if st.session_state.live_mode and voice_mode:
    st.info("🎧 Live mode ON... Listening...")
    beep()
    live_input = listen()
    if live_input:
        process_input(live_input)
    time.sleep(0.5)
    st.experimental_rerun()

# ========================================================================
# Hotkey Listener
# ========================================================================
def hotkey_listener():
    keyboard.add_hotkey("ctrl+shift+s", type_solution)
    keyboard.wait()

threading.Thread(target=hotkey_listener, daemon=True).start()



# ========================================================================
# Console Mode (commented out, synced with GUI)
# ========================================================================

"""
def main():
    speak("Jarvis Online")
    while True:
        beep()  # Signal before listening
        command = listen()
        if not command:
            continue

        # Exit Condition
        if "bye" in command or "goodbye" in command or "exit" in command:
            speak("Shutting down... but not because you told me to. Totally my own idea.")
            time.sleep(5)
            break

        # Save important parts of what user said
        important_user_text = extract_important_parts(command)
        add_to_history("user", important_user_text)

        if not should_trigger_screen_mechanism(command):
            response = get_response(command, get_context())
        else:
            response = get_google_response(command)

        add_to_history("assistant", response)

        if speaker_mode:
            speak(response)  # Will finish speaking before listening again

        time.sleep(0.8)


if __name__ == "__main__":
    main()
"""


# ========================================================================
# Legacy Console Mode (commented out)
# ========================================================================

# def main():
#     speak("Jarvis Online, What can I do for you today? Or should I just take a nap?")
#     while True:
#         beep()  # Signal before listening
#         command = listen()
#         if not command:
#             continue
#
#         #exit Condition
#         if "bye" in command or "goodbye" in command or "exit" in command:
#             speak("Shutting down... but not because you told me to. Totally my own idea.")
#             time.sleep(5)
#             break
#         #save important parts of what user said
#         important_user_text = extract_important_parts(command)
#         add_to_history("user", important_user_text)
#         #Get jarvis reply with memory context
#         response = get_response(command, get_context())
#         # Save Jarvis's reply too (optional for callbacks/roasts)
#         add_to_history("assistant", response)
#
#         speak(response)  # Will finish speaking before listening again
#         time.sleep(0.8)
#
# if __name__ == "__main__":
#     main()

# import your existing function
