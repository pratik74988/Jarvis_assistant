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
from task import solve_from_screenshot
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

# Store logs in Streamlit session
if "logs" not in st.session_state:
    st.session_state.logs = []


def log_to_ui(message, level="INFO"):
    """Send logs to both console + Streamlit session."""
    if level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.debug(message)

    st.session_state.logs.append(f"[{level}] {message}")


# ========================================================================
# Streamlit Mode (GUI)
# ========================================================================

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False

st.title("Jarvis V0.0 🎙️ 📸")

# --- Sidebar ---
st.sidebar.header("wanna change me?")
voice_mode = st.sidebar.checkbox("Enable voice mode", value=False)
speaker_mode = st.toggle("Speaker mode")
if st.sidebar.button("🔴 Toggle Live Mode"):
    st.session_state.live_mode = not st.session_state.live_mode

# --- Screenshot Feature Info ---
st.sidebar.markdown("### 📸 Screenshot Feature")
st.sidebar.markdown("Try saying:")
st.sidebar.markdown("- 'take a screenshot'")
st.sidebar.markdown("- 'what do you see?'")
st.sidebar.markdown("- 'analyze my screen'")
st.sidebar.markdown("- 'capture screen'")

# --- Input Area ---
user_input = st.text_input("say something dont be shy:", "")


# --- Main Interaction ---
def process_input(user_input):
    log_to_ui(f"Received input: {user_input}")

    # Exit condition
    if any(x in user_input.lower() for x in ["bye", "goodbye", "exit"]):
        response = "Shutting down... but not because you told me to. Totally my own idea."
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", response))
        speak(response)
        st.write("#### Jarvis stopped")
        st.stop()

    # --- Short-term memory ---
    log_to_ui("Calling extract_important_parts")
    important_user_text = extract_important_parts(user_input)

    log_to_ui("Adding to history (user)")
    add_to_history("user", important_user_text)

    # --- Long-term memory storage ---
    log_to_ui("Checking if input should be stored")
    if should_store(user_input):
        log_to_ui("Storing input in long-term memory")
        store_long_term_memory(user_input, role="user")

    # --- Recall long-term memory ---
    log_to_ui("Recalling long-term memory")
    past_memories = recall_long_term_memory(user_input, top_k=3)
    memory_context = "\n".join(past_memories[0]) if past_memories else ""

    # --- Full context for LLM ---
    log_to_ui("Getting short-term context")
    full_context = get_context()
    if memory_context:
        full_context.append({"role": "memory", "content": memory_context})
        log_to_ui(f"[MEMORY USED] {memory_context}")

    # --- Decide how to respond ---
    if not should_trigger_screen_mechanism(user_input):
        log_to_ui("Getting response from LLM")
        response = get_response(user_input, full_context)
    else:
        log_to_ui("Triggering Google response")
        response = get_google_response()

    log_to_ui("Adding to history (assistant)")
    add_to_history("assistant", response)

    # --- Save in session state ---
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("assistant", response))

    # --- Typing effect ---
    with st.chat_message("assistant"):
        placeholder = st.empty()
        typed_text = ""
        for char in response:
            typed_text += char
            placeholder.markdown(f"🤖 **Jarvis:** {typed_text}")
            time.sleep(0.02)

    if speaker_mode:
        speak(response)


# --- Handle send button or live mode ---
if st.button("send") or (voice_mode and st.button("🎤 Speak")):
    if voice_mode and not user_input:
        beep()
        user_input = listen()
    if user_input:
        process_input(user_input)

# --- Live mode loop ---
if st.session_state.live_mode and voice_mode:
    st.info("🎧 Live mode ON... Listening...")
    beep()
    live_input = listen()
    if live_input:
        process_input(live_input)
    time.sleep(0.5)
    st.experimental_rerun()

# --- Display chat history ---
st.write("### Chat History")
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"👤 **You:** {text}")
    else:
        st.markdown(f"🤖 **Jarvis:** {text}")

# --- Display logs ---
with st.expander("📜 Logs"):
    for msg in st.session_state.logs[-30:]:  # last 30 logs
        st.text(msg)


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

def hotkey_listener():
    # Press Ctrl+Shift+S anywhere to trigger screenshot
    keyboard.add_hotkey("ctrl+shift+s", solve_from_screenshot)
    keyboard.wait()  # keep listener alive

# Run in background (won’t block Streamlit or CLI loop)
threading.Thread(target=hotkey_listener, daemon=True).start()
