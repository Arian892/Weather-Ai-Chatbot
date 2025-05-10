from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from datetime import datetime, timedelta
import requests
import json
from typing import Optional, Tuple, List, Dict

# === API Keys ===
from my_api_key import api_key, weather_api_key

# === LLM Setup ===
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=api_key,
    temperature=0.7,
)

# === Utility Functions ===
def get_location_from_ip() -> Tuple[Optional[str], Optional[str]]:
    """Get city and country from IP address"""
    try:
        res = requests.get("https://ipinfo.io/json")
        data = res.json()
        return data.get("city"), data.get("country")
    except:
        return None, None

def get_coordinates(city: str) -> Tuple[Optional[float], Optional[float]]:
    """Get latitude and longitude using city name"""
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city, "limit": 1, "appid": weather_api_key}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
        return None, None
    except:
        return None, None

# === Weather API Calls ===
def get_current_weather(city: Optional[str] = None) -> str:
    """Get current weather data"""
    if not city:
        city, _ = get_location_from_ip()
        print(f"City from IP: {city}")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": weather_api_key, "units": "metric"}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        if res.status_code != 200:
            return f"Weather unavailable for {city}."
        return (
            f"Current weather in {city}:\n"
            f"• Temp: {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)\n"
            f"• {data['weather'][0]['description'].capitalize()}\n"
            f"• Humidity: {data['main']['humidity']}%\n"
            f"• Wind: {data['wind']['speed']} m/s"
        )
    except:
        return "Error retrieving current weather."

def get_forecast_daily(city: Optional[str] = None, days: int = 3) -> str:
    """Get daily forecast for the next few days"""
    if not city:
        city, _ = get_location_from_ip()

    print(f"City from IP: {city}")
    lat, lon = get_coordinates(city)
    print(f"Coordinates: {lat}, {lon}")
    if not lat:
        return f"Could not find coordinates for {city}."
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat, "lon": lon, "cnt": days,
        "appid": weather_api_key, "units": "metric"
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        print(f"Response: {data}")
        return data
        # if res.status_code != 200:
        #     return f"Forecast not available for {city}."
        # forecast = f"{days}-day forecast for {city}:\n"
        # for d in data["list"]:
        #     date = datetime.utcfromtimestamp(d["dt"]).strftime('%Y-%m-%d')
        #     desc = d["weather"][0]["description"]
        #     forecast += f"{date}: {desc}, {d['temp']['min']}°C - {d['temp']['max']}°C\n"
        # return forecast
    except:
        return "Error retrieving forecast."

def get_historical_weather(city: Optional[str] = None, days: int = 3) -> str:
    """Get weather history for past days"""
    if not city:
        city, _ = get_location_from_ip()
        
    print(f"City from IP: {city}")
    lat, lon = get_coordinates(city)
    if not lat:
        return f"Coordinates not found for {city}."

    end_time = int(datetime.now().timestamp())
    start_time = int((datetime.now() - timedelta(days=days)).timestamp())

    url = "https://history.openweathermap.org/data/2.5/history/city"
    params = {
        "lat": lat, "lon": lon,
        "type": "hour",
        "start": start_time,
        "end": end_time,
        "appid": weather_api_key,
        "units": "metric"
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        print(f"Response: {data}")
        return data
        # if res.status_code != 200 or "list" not in data:
        #     return f"No historical data for {city}."

        # history = f"Historical weather for {city} (last {days} days):\n"
        # daily_temps = {}

        # for entry in data["list"]:
        #     date = datetime.utcfromtimestamp(entry["dt"]).strftime('%Y-%m-%d')
        #     temp = entry["main"]["temp"]
        #     daily_temps.setdefault(date, []).append(temp)

        # for date, temps in daily_temps.items():
        #     history += f"{date}: Avg Temp {sum(temps)/len(temps):.1f}°C\n"

        # return history
    except Exception as e:
        return f"Error getting history: {str(e)}"

# === LangChain Agent Tools ===
tools = [
    Tool(name="CurrentWeather", func=get_current_weather, description="Get current weather if no city name is provided, it will use your current location"),
    Tool(name="ForecastWeather", func=get_forecast_daily, description="Get daily weather forecast , get tomorrow forecast if no city name is provided, it will use your current location"),
    Tool(name="HistoricalWeather", func=get_historical_weather, description="Get past weather data for the last 3–4 days like yesterday also if no city name is provided, it will use your current location"),
]

# === Initialize LangChain Agent ===
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

# === Final Query Processing ===
def process_weather_query(query: str) -> str:
    try:
        return agent.run(query)
    except Exception as e:
        return f"Error: {str(e)}"

# === Entry Point ===
if __name__ == "__main__":
    query = input("Ask your weather question: ")
    print(process_weather_query(query))
