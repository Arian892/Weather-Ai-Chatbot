from elevenlabs.client import ElevenLabs
from elevenlabs import play
from my_api_key import text_analytics_api_key  # Your key

client = ElevenLabs(api_key=text_analytics_api_key)

def speak(text):
    audio = client.generate(
        text=text,
        voice="Rachel",
        model="eleven_monolingual_v1"
    )
    play(audio)