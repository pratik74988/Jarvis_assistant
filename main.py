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
