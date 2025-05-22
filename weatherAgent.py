from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from datetime import datetime, timedelta
from collections import defaultdict
import dateparser
from langchain.tools import StructuredTool

# from langchain_groq import ChatGroq
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
from datetime import datetime

def get_current_weather(city: Optional[str] = None) -> str:
    """Get current weather data"""
    print("get current weather function called")
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
            return f"❌ Weather unavailable for {city}. Error: {data.get('message', 'Unknown error')}"

        today = datetime.now().strftime("%B %d, %Y")

        # Extract sunrise and sunset times (convert from UTC timestamp)
        sunrise_ts = data["sys"]["sunrise"]
        sunset_ts = data["sys"]["sunset"]
        sunrise_time = datetime.fromtimestamp(sunrise_ts).strftime("%I:%M %p")
        sunset_time = datetime.fromtimestamp(sunset_ts).strftime("%I:%M %p")

        return (
            f"📅 Today is {today}\n"
            f"📍 Current weather in {city}:\n"
            f"🌅 Sunrise: {sunrise_time}\n"
            f"🌇 Sunset: {sunset_time}\n"
            f"🌡️ Temp: {data['main']['temp']}°C (Feels like {data['main']['feels_like']}°C)\n"
            f"📖 {data['weather'][0]['description'].capitalize()}\n"
            f"💧 Humidity: {data['main']['humidity']}%\n"
            f"🌬️ Wind: {data['wind']['speed']} m/s"
        )

    except Exception as e:
        print(f"Exception: {e}")
        return "❌ Error retrieving current weather."

# import requests
# from typing import Optional
# from datetime import datetime
# from collections import defaultdict



def get_forecast_for_datetime(city: Optional[str] = None, target_datetime: Optional[str] = None) -> str:
    print("get forecast function called")
    print(f"[DEBUG] city argument value: {repr(city)}")

    if not city:
        city, _ = get_location_from_ip()
        print(f"City from IP: {city}")

    if target_datetime:
        parsed_dt = dateparser.parse(target_datetime)
        if not parsed_dt:
            return "❌ Could not parse the provided date. Try something like 'tomorrow' or 'next Friday'."
    else:
        parsed_dt = datetime.now()

    print(f"City: {city}")
    print(f"Target Datetime: {parsed_dt}")

    max_days_ahead = 3
    now = datetime.now()
    days_ahead = (parsed_dt.date() - now.date()).days

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

        all_hours = []
        for day in data["forecast"]["forecastday"]:
            all_hours.extend(day["hour"])

        target_ts = int(parsed_dt.timestamp())
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

        sunrise_temp = None
        sunset_temp = None

        for day in data["forecast"]["forecastday"]:
            if day["date"] == parsed_dt.date().isoformat():
                # Sunrise temp
                sunrise_str = day["astro"]["sunrise"]
                sunrise_dt = datetime.strptime(f"{day['date']} {sunrise_str}", "%Y-%m-%d %I:%M %p")
                sunrise_ts = int(sunrise_dt.timestamp())

                closest_to_sunrise = min(
                    day["hour"],
                    key=lambda h: abs(int(datetime.strptime(h["time"], "%Y-%m-%d %H:%M").timestamp()) - sunrise_ts)
                )
                sunrise_temp = closest_to_sunrise["temp_c"]

                # Sunset temp
                sunset_str = day["astro"]["sunset"]
                sunset_dt = datetime.strptime(f"{day['date']} {sunset_str}", "%Y-%m-%d %I:%M %p")
                sunset_ts = int(sunset_dt.timestamp())

                closest_to_sunset = min(
                    day["hour"],
                    key=lambda h: abs(int(datetime.strptime(h["time"], "%Y-%m-%d %H:%M").timestamp()) - sunset_ts)
                )
                sunset_temp = closest_to_sunset["temp_c"]

                break

        print(f"time {time}")   
        print(f"temp {temp}")
        print(f"feels_like {feels_like}")
        print(f"condition {condition}")
        print(f"wind {wind}")
        print(f"humidity {humidity}")
        print(f"pressure {pressure}")
        print(f"sunrise temp {sunrise_temp}")
        print(f"sunset temp {sunset_temp}")

        response = (
            f"📍 Weather in {city} at {time}:\n"
            f"🌡️ Temperature: {temp}°C (Feels like {feels_like}°C)\n"
            f"🌬️ Wind Speed: {wind} kph\n"
            f"💧 Humidity: {humidity}%\n"
            f"📈 Pressure: {pressure} hPa\n"
            f"📖 Condition: {condition}"
        )

        if sunrise_temp is not None:
            response += f"\n🌅 Temperature at sunrise: {sunrise_temp}°C"
        if sunset_temp is not None:
            response += f"\n🌇 Temperature at sunset: {sunset_temp}°C"

        return response

    except Exception as e:
        print(f"Exception: {e}")
        return "❌ Error retrieving forecast."
    

def get_historical_weather(city: Optional[str] = None, target_date: Optional[str] = None, api_key: Optional[str] = None) -> str:
    print("get historical function called")

    if not city:
        city, _ = get_location_from_ip()
        print(f"City from IP: {city}")

    if target_date:
        parsed_dt = dateparser.parse(target_date)
        if not parsed_dt:
            return "❌ Could not parse the provided date. Try something like 'last Monday' or '2 days ago'."
    else:
        parsed_dt = datetime.now()

    date_str = parsed_dt.strftime("%Y-%m-%d")

    if parsed_dt.date() >= datetime.now().date():
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

        day_forecast = data["forecast"]["forecastday"][0]
        day_data = day_forecast["day"]
        hour_data = day_forecast["hour"]
        astro = day_forecast["astro"]

        max_temp = day_data["maxtemp_c"]
        min_temp = day_data["mintemp_c"]
        avg_temp = day_data["avgtemp_c"]
        max_wind = day_data["maxwind_kph"]
        total_precip = day_data["totalprecip_mm"]
        avg_humidity = day_data["avghumidity"]
        condition = day_data["condition"]["text"]

        # Parse sunrise and sunset time strings (e.g. "05:34 AM")
        sunrise_str = astro["sunrise"]
        sunset_str = astro["sunset"]

        sunrise_dt = datetime.strptime(f"{date_str} {sunrise_str}", "%Y-%m-%d %I:%M %p")
        sunset_dt = datetime.strptime(f"{date_str} {sunset_str}", "%Y-%m-%d %I:%M %p")

        sunrise_ts = int(sunrise_dt.timestamp())
        sunset_ts = int(sunset_dt.timestamp())

        # Find closest hour entries for sunrise and sunset
        closest_to_sunrise = min(
            hour_data,
            key=lambda h: abs(int(datetime.strptime(h["time"], "%Y-%m-%d %H:%M").timestamp()) - sunrise_ts)
        )
        sunrise_temp = closest_to_sunrise["temp_c"]

        closest_to_sunset = min(
            hour_data,
            key=lambda h: abs(int(datetime.strptime(h["time"], "%Y-%m-%d %H:%M").timestamp()) - sunset_ts)
        )
        sunset_temp = closest_to_sunset["temp_c"]

        print(f"Max Temp: {max_temp}°C")
        print(f"Min Temp: {min_temp}°C")
        print(f"Avg Temp: {avg_temp}°C")
        print(f"Max Wind: {max_wind} kph")
        print(f"Total Precipitation: {total_precip} mm")
        print(f"Avg Humidity: {avg_humidity}%")
        print(f"Condition: {condition}")
        print(f"Sunrise Temp: {sunrise_temp}°C")
        print(f"Sunset Temp: {sunset_temp}°C")

        return (
            f"📅 Historical weather in {city} on {date_str}:\n"
            f"🌡️ Max Temp: {max_temp}°C\n"
            f"🌡️ Min Temp: {min_temp}°C\n"
            f"🌡️ Avg Temp: {avg_temp}°C\n"
            f"🌬️ Max Wind Speed: {max_wind} kph\n"
            f"💧 Total Precipitation: {total_precip} mm\n"
            f"💧 Avg Humidity: {avg_humidity}%\n"
            f"📖 Condition: {condition}\n"
            f"🌅 Temperature at sunrise: {sunrise_temp}°C\n"
            f"🌇 Temperature at sunset: {sunset_temp}°C"
        )

    except Exception as e:
        print(f"Exception: {e}")
        return "❌ Error retrieving historical weather."

# from langchain.tools import StructuredTool

# === LangChain Agent Tools ===
tools = [
    StructuredTool.from_function(
        func=get_current_weather,
        name="CurrentWeather",
        description="Get current weather for a given city. If no city is provided, it uses your current location."
    ),
    
    StructuredTool.from_function(
        func=get_forecast_for_datetime,
        name="GetTomorrowForecast",
        description=(
            "Get the weather forecast for a specific date (e.g., 'tomorrow', 'next Monday') "
            "for a given or current location. Use this for queries like "
            "'weather update tomorrow', 'forecast for Sunday in Dhaka', etc. "
            "Works even if no city is mentioned (uses current location)."
        )
    ),

    StructuredTool.from_function(
        func=get_historical_weather,
        name="HistoricalWeather",
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
    verbose=True,
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
