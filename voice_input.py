# voice_input.py
import speech_recognition as sr

def record_and_transcribe(duration=5):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Recording...")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, phrase_time_limit=duration)
        print("Done.")

    try:
        # You can replace 'recognize_google' with other engines if needed
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "❌ Could not understand the audio."
    except sr.RequestError as e:
        return f"❌ Could not request results; {e}"
