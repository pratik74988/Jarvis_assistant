
import streamlit as st
import time
from memory import (
    add_to_history,
    get_context,
    extract_important_parts,
    should_store,
    store_long_term_memory,
    recall_long_term_memory,
)
# import your voice + brain modules
from listener import listen
from speaker import speak, beep
from brain import get_response

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False

st.title("Jarvis V0.0 🎙️")

# --- Sidebar ---
st.sidebar.header("wanna change me?")
voice_mode = st.sidebar.checkbox("Enable voice mode", value=False)
if st.sidebar.button("🔴 Toggle Live Mode"):
    st.session_state.live_mode = not st.session_state.live_mode

# --- Input Area ---
user_input = st.text_input("say something dont be shy:", "")

# --- Main Interaction ---
def process_input(user_input):
    print(f"[LOG] Received input: {user_input}")

    # Exit condition
    if any(x in user_input.lower() for x in ["bye", "goodbye", "exit"]):
        response = "Shutting down... but not because you told me to. Totally my own idea."
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", response))
        speak(response)
        st.write("#### Jarvis stopped")
        st.stop()

    # --- Short-term memory ---
    print(f"[LOG] Calling extract_important_parts")
    important_user_text = extract_important_parts(user_input)

    print(f"[LOG] Calling add_to_history for user")
    add_to_history("user", important_user_text)

    # --- Long-term memory storage ---
    print(f"[LOG] Checking if input should be stored")
    if should_store(user_input):
        print(f"[LOG] Storing input in long-term memory")
        store_long_term_memory(user_input, role="user")

    # --- Recall long-term memory ---
    print(f"[LOG] Recalling long-term memory")
    past_memories = recall_long_term_memory(user_input, top_k=3)
    memory_context = "\n".join(past_memories[0]) if past_memories else ""

    # --- Full context for LLM ---
    print(f"[LOG] Getting short-term context")
    full_context = get_context()
    if memory_context:
        full_context.append({"role": "memory", "content": memory_context})
        print(f"[MEMORY USED] {memory_context}")

    print(f"[LOG] Getting response from LLM")
    response = get_response(user_input, full_context)

    print(f"[LOG] Calling add_to_history for assistant")
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











# def main():
#     speak("Jarvis Online, What can I do for you today? Or should I just take a nap?")
#     while True:
#         beep()  # Signal before listening
#         command = listen()
#         if not command:
#             continue

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

#         speak(response)  # Will finish speaking before listening again
#         time.sleep(0.8)

# if __name__ == "__main__":
#     main()
from listener import listen
from speaker import speak, beep
from brain import get_response
from memory import add_to_history, get_context, extract_important_parts
import time

def main():
    speak("Jarvis Online")
    while True:
        beep()  # Signal before listening
        command = listen()
        if not command:
            continue

        #exit Condition
        if "bye" in command or "goodbye" in command or "exit" in command:
            speak("Shutting down... but not because you told me to. Totally my own idea.")
            time.sleep(5)
            break
        #save important parts of what user said
        important_user_text = extract_important_parts(command)
        add_to_history("user", important_user_text)
        #Get jarvis reply with memory context
        response = get_response(command, get_context())
        # Save Jarvis's reply too (optional for callbacks/roasts)
        add_to_history("assistant", response)

        speak(response)  # Will finish speaking before listening again
        time.sleep(0.8)

if __name__ == "__main__":
    main()