import speech_recognition as sr

recognizer = sr.Recognizer()

def listen (promt="listening...."):
    try:
        with sr.Microphone() as source :
            print(promt)
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5,phrase_time_limit=10)
        text = recognizer.recognize_google(audio)
        print(f"you: {text}")
        return text.lower()
    except sr.WaitTimeoutError:
        print("⏳ Listening timed out. No speech detected.")
        return ""
    except sr.UnknownValueError: 
        print("❌ Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"⚠️ Could not request results from Google: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected error: {e}")
        return ""