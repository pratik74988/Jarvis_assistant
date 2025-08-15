from listener import listen
from speaker import speak, beep
from brain import get_response
import time

def main():
    speak("Jarvis Online, Lets Catch Something")
    while True:
        beep()  # Signal before listening
        command = listen()

        if not command:
            continue

        if "bye" in command or "goodbye" in command or "exit" in command:
            speak("Shutting down... but not because you told me to. Totally my own idea.")
            time.sleep(5)
            break

        response = get_response(command)
        speak(response)  # Will finish speaking before listening again
        time.sleep(0.8)

if __name__ == "__main__":
    main()
