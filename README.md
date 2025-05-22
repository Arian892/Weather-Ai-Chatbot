# 🌦️ Weather Agent using LangChain, Gemini, and Voice I/O

This is a conversational weather assistant powered by:

- **LangChain** for chaining LLM calls  
- **Google Gemini (via Generative AI)** for conversational AI  
- **OpenWeatherMap API** for weather data  
- **ElevenLabs** for voice synthesis (text-to-speech)  
- **SpeechRecognition** for voice input (speech-to-text)  
- **SQLAlchemy** for query history storage  
- **Streamlit** for the web interface  

It allows users to:

- 🌤️ Fetch **current weather**  
- 📅 Provide **forecasts for any date/time**  
- 🕰️ Retrieve **historical weather data**  
- 🎤 Speak and listen via voice commands (optional)  
- 📚 Keep a persistent query history for contextual follow-ups  

If no city is provided, it detects your location automatically using your IP address.

---


## ✅ Requirements

Before you begin, ensure you have the following:

- Python 3.8 or newer
- API keys for:
  - [Google Generative AI (Gemini)](https://makersuite.google.com/)
  - [OpenWeatherMap](https://openweathermap.org/api)
  - [weatherapi](http://weatherapi.com)
  - [ElevenLabs](https://elevenlabs.io/)

---

## 🧠 Installation Steps

### 1. Clone or download this repository

```bash
git clone https://github.com/Arian892/Weather-Ai-Chatbot.git
cd Weather-Ai-Chatbot
```

### 2. Install the required Python packages

```bash
pip install langchain requests streamlit langchain-google-genai elevenlabs SpeechRecognition sqlalchemy dateparser
```

> Optionally, create a `requirements.txt` with the above lines and run:
> ```bash
> pip install -r requirements.txt
> ```

### 3. Add your API keys

Create a `my_api_key.py` file in the root directory of your project:

```python
# my_api_key.py
api_key = "your_google_gemini_api_key"
weather_api_key = "your_openweathermap_api_key"
another_api_key = 'you weatherapi key'
text_analytics_api_key = "your_text_analytics_api_key"  # if used


```

⚠️ **Important:** Do not share or commit this file to GitHub.

---

## 🚀 Run the Weather Chatbot

Launch the app using Streamlit:

```bash
streamlit run app.py
```

This will open the chatbot in your default browser.

---

## 💬 Example Queries

Try asking:

- What's the weather like in New York right now?
- Will it rain tomorrow in Berlin?
- Show me the forecast for Tokyo.
- What was the temperature in Paris 3 days ago?
- What's the humidity in Mumbai today?

---

## 📂 Project Structure

```
weather-agent-gemini/
├── app.py                  # Streamlit frontend with voice I/O and query history
├── weatherAgent.py         # Core LangChain agent and weather API tools
├── voice_input.py          # Microphone recording and speech-to-text
├── voice_output.py         # Text-to-speech using ElevenLabs
├── models.py               # SQLAlchemy models and DB setup for query history
├── my_api_key.py           # Your API keys (excluded from git)
├── requirements.txt        # Python dependencies
└── README.md               # This file

```

---

## 📌 Notes

- Historical weather data may require a paid plan from OpenWeatherMap.
- IP-based location detection may be inaccurate if using VPN or proxies.
- You can enhance this project with:
  - LangChain memory
  - Voice I/O (e.g., ElevenLabs)
  - Vector search for context-aware weather conversations

---

## 📜 License

MIT License.
