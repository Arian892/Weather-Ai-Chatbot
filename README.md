# 🌦️ Weather Agent using LangChain and Gemini

This is a conversational weather assistant powered by **LangChain**, **Google Gemini (via Generative AI)**, and the **OpenWeatherMap API**. It allows users to:

- 🌤️ Fetch **current weather**
- 📅 Provide **daily forecasts**
- 🕰️ Retrieve **historical weather data**

If no city is provided, it detects your location automatically using your IP address.

---

## ✅ Requirements

Before you begin, ensure you have the following:

- Python 3.8 or newer
- API keys for:
  - [Google Generative AI (Gemini)](https://makersuite.google.com/)
  - [OpenWeatherMap](https://openweathermap.org/api)

---

## 🧠 Installation Steps

### 1. Clone or download this repository

```bash
git clone https://github.com/your-username/weather-agent-gemini
cd weather-agent-gemini
```

### 2. Install the required Python packages

```bash
pip install langchain requests streamlit langchain-google-genai
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
├── app.py               # Streamlit frontend
├── weatherAgent.py      # LangChain agent logic and tools
├── my_api_key.py        # Your API keys (excluded from version control)
├── requirements.txt     # (Optional) dependencies list
└── README.md            # This file
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
