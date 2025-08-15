import re
import time
import winsound
import asyncio
import edge_tts
import pygame
import os

VOICE = "en-US-JennyNeural"  # Try "en-US-JennyNeural" for female
#en-US-JennyNeural
# Initialize pygame mixer
pygame.mixer.init()

async def _async_speak(text):
    """Internal async function to generate and play speech."""
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
    print(f"Jarvis: {clean_text}")

    # Save to temp mp3
    output_file = "jarvis_temp.mp3"
    tts = edge_tts.Communicate(clean_text, voice=VOICE)
    await tts.save(output_file)

    # Play with pygame
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()

    # Wait until playback finishes
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # Stop & unload to free file
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    pygame.mixer.init()  # re-init so next play works

    # Now delete the file
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except PermissionError:
            pass  # if still locked, ignore

def speak(text):
    """Speak using Edge-TTS (blocks until finished)."""
    asyncio.run(_async_speak(text))
    time.sleep(0.2)  # small pause before mic opens

def beep():
    """Beep to signal Jarvis is ready to listen."""
    winsound.Beep(800, 150)  # softer beep
