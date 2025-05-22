from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from datetime import datetime, timedelta
from collections import defaultdict
import requests
import json
from typing import Optional, Tuple, List, Dict
from dateutil import parser as date_parser
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.prompts import MessagesPlaceholder
from langchain_core.prompts.chat import ChatPromptTemplate
from  models import QueryHistory , Session, log_query_to_db, load_recent_history


# === API Keys ===
from my_api_key import api_key, weather_api_key , another_api_key


# Add system message enforcing behavior

# === LLM Setup ===
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=api_key,
    temperature=0.7,
)

# === Utility Functions ===
def get_location_from_ip() -> Tuple[Optional[str], Optional[str]]:
    """Get city and country from IP address using ipinfo.io"""
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        res.raise_for_status()  # Raise HTTPError if not 200
        data = res.json()
        city = data.get("city")
        country = data.get("country")
        if not city or not country:
            print("Warning: Incomplete location data:", data)
        return city, country
    except requests.exceptions.RequestException as e:
        print("Network or HTTP error:", e)
    except ValueError as e:
        print("JSON decode error:", e)
    except Exception as e:
        print("Unexpected error:", e)
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
    print("get current weather function callled")
    print(f"[DEBUG] city argument value: {repr(city)}")
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

# import requests
# from typing import Optional
# from datetime import datetime
# from collections import defaultdict







def get_forecast_for_datetime(city: Optional[str] = None, target_datetime: Optional[datetime] = None) -> str:


    print("get forecast function callled")
    print(f"[DEBUG] city argument value: {repr(city)}")

    """Get the weather forecast closest to a specific datetime for a given city.
    
    If city or datetime is not provided, defaults to current location and current time.
    """
    # Default city if not provided
    if not city:
        city, _ = get_location_from_ip()
        print(f"City from IP: {city}")

    # Default datetime if not provided
    if target_datetime is None:
        target_datetime = datetime.now()

    print(f"City: {city}")
    print(f"Target Datetime: {target_datetime}")

    max_days_ahead = 3
    now = datetime.now()
    days_ahead = (target_datetime.date() - now.date()).days

    if days_ahead < 0 or days_ahead >= max_days_ahead:
        return f"❌ Can only fetch forecast up to {max_days_ahead} days ahead with the free plan."

    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": another_api_key,
        "q": city,
        "days": days_ahead + 1,
        "aqi": "no",
        "alerts": "no"
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()
        print(data)

        if "forecast" not in data:
            return "❌ Forecast data not available."

        # Collect all hourly forecasts
        all_hours = []
        for day in data["forecast"]["forecastday"]:
            all_hours.extend(day["hour"])

        target_ts = int(target_datetime.timestamp())
        closest = min(
            all_hours, 
            key=lambda h: abs(int(datetime.strptime(h["time"], "%Y-%m-%d %H:%M").timestamp()) - target_ts)
        )

        time = closest["time"]
        temp = closest["temp_c"]
        feels_like = closest["feelslike_c"]
        condition = closest["condition"]["text"]
        wind = closest["wind_kph"]
        humidity = closest["humidity"]
        pressure = closest["pressure_mb"]



        print(f"time {time}")   
        print(f"temp {temp}")
        print(f"feels_like {feels_like}")
        print(f"condition {condition}")
        print(f"wind {wind}")
        print(f"humidity {humidity}")
        print(f"pressure {pressure}")
        # Format the output


        return (
            f"📍 Weather in {city} at {time}:\n"
            f"🌡️ Temperature: {temp}°C (Feels like {feels_like}°C)\n"
            f"🌬️ Wind Speed: {wind} kph\n"
            f"💧 Humidity: {humidity}%\n"
            f"📈 Pressure: {pressure} hPa\n"
            f"📖 Condition: {condition}"
        )

    except Exception as e:
        print(f"Exception: {e}")
        return "❌ Error retrieving forecast."



def parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string with optional year. Return None if ambiguous."""
    formats = ["%B %d %Y", "%b %d %Y", "%Y-%m-%d", "%B %d", "%b %d"]  # Full & partial formats
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # If year missing, return None for clarity
            if '%Y' not in fmt:
                return None
            return dt
        except ValueError:
            continue
    return None
def get_historical_weather(city: Optional[str] = None, target_date: Optional[datetime] = None, api_key: Optional[str] = None) -> str:
    """
    Get detailed historical weather for a city on a specific date.

    If city is None, attempts to get location from IP.
    If target_date is None, defaults to yesterday.
    """
    print("get forecast function callled")

   

    # Default city if not provided
    if not city:
        city, _ = get_location_from_ip()
        print(f"City from IP: {city}")

    # Default target_date if not provided: yesterday (historical data can't be today or future)
    if target_date is None:
        target_date = datetime.now() - timedelta(days=1)

    # Format date for WeatherAPI: yyyy-mm-dd
    date_str = target_date.strftime("%Y-%m-%d")

    # Make sure the target date is not in the future or today
    if target_date.date() >= datetime.now().date():
        return "❌ Historical data is only available for past dates (not today or future)."

    print(f"City: {city}")
    print(f"Date: {date_str}")

    url = "http://api.weatherapi.com/v1/history.json"
    params = {
        "key": another_api_key,
        "q": city,
        "dt": date_str,
        "aqi": "no",
        "alerts": "no"
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()
        print(f"API response: {data}")

        if "forecast" not in data or "forecastday" not in data["forecast"]:
            return f"❌ No historical weather data found for {city} on {date_str}."

        day_data = data["forecast"]["forecastday"][0]["day"]

        max_temp = day_data["maxtemp_c"]
        min_temp = day_data["mintemp_c"]
        avg_temp = day_data["avgtemp_c"]
        max_wind = day_data["maxwind_kph"]
        total_precip = day_data["totalprecip_mm"]
        avg_humidity = day_data["avghumidity"]
        condition = day_data["condition"]["text"]

        print(f"Max Temp: {max_temp}°C")
        print(f"Min Temp: {min_temp}°C")
        print(f"Avg Temp: {avg_temp}°C")
        print(f"Max Wind: {max_wind} kph")
        print(f"Total Precipitation: {total_precip} mm")
        print(f"Avg Humidity: {avg_humidity}%")
        print(f"Condition: {condition}")

        return (
            f"📅 Historical weather in {city} on {date_str}:\n"
            f"🌡️ Max Temp: {max_temp}°C\n"
            f"🌡️ Min Temp: {min_temp}°C\n"
            f"🌡️ Avg Temp: {avg_temp}°C\n"
            f"🌬️ Max Wind Speed: {max_wind} kph\n"
            f"💧 Total Precipitation: {total_precip} mm\n"
            f"💧 Avg Humidity: {avg_humidity}%\n"
            f"📖 Condition: {condition}"
        )

    except Exception as e:
        print(f"Exception: {e}")
        return "❌ Error retrieving historical weather."



# === LangChain Agent Tools ===
tools = [
    Tool(name="CurrentWeather", func=get_current_weather, description="Get current weather if no city name is provided, it will use your current location"),
    Tool(name="ForecastWeather", func=get_forecast_for_datetime, description=(
        "Get weather forecast for a specific city and date. "
        "If no city is provided, the function uses your current location automatically. "
        "If no date is given, it defaults to the current date. "
        "Note: Only supports dates up to 3 days in the future."
    )
    ),
    Tool(
    name="HistoricalWeather",
    func=get_historical_weather,
    description=(
        "Fetch detailed historical weather data for a specific city and date. "
        "If no city is provided, the function uses your current location automatically. "
        "If no date is given, it defaults to yesterday's weather. "
        "Provides information such as temperature highs and lows, wind speed, precipitation, humidity, and conditions. "
        "Note: Supports dates up to a few days in the past."
    )
)
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
        # Load recent history as context string
        context = load_recent_history()

        # Combine context + new query
        full_input = f"{context}\n\nUser: {query}\nAssistant:"

        # Run the agent on this combined input
        response = agent.run(full_input)

        # Log new query & response as usual
        log_query_to_db(query, response)

        return response
    except Exception as e:
        return f"Error: {str(e)}"


# === Entry Point ===
if __name__ == "__main__":
    query = input("Ask your weather question: ")
    print(process_weather_query(query))
