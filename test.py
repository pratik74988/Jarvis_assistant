import pyttsx3

engine = pyttsx3.init()

# List voices
voices = engine.getProperty('voices')
for i, v in enumerate(voices):
    print(f"{i}: {v.name}")

# Set voice
engine.setProperty('voice', voices[0].id)  # Try other indexes if no sound
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

# Speak test
engine.say("Hello, this is Jarvis. If you can hear me, then my voice is working perfectly.")
engine.runAndWait()
