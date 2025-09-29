import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import locale

COUNTRY_CONFIG = {
    "México": {
        "country_code": "MX",
        "locale": "es_ES.UTF-8",
        "lang_api": "es",
        "api_units": "metric",
        "temp_unit": "°C",
        "wind_unit": "km/h",
        "precip_unit": "mm",
        "title": "🌦️ Clima y Pronóstico 🌦️",
        "subtitle": "Escribe tu ciudad o Estado para obtener el clima en tiempo real y el pronóstico a 5 días.",
        "city_label": "Ciudad",
        "default_city": "Campeche",
        "button_label": "Ver el clima",
        "spinner_text": "Obteniendo datos para",
        "temp_label": "🌡️ Temperatura",
        "wind_label": "🌬️ Viento",
        "humidity_label": "💧 Humedad",
        "precip_label": "🌧️ Precipitación (1h)",
        "clouds_label": "☁️ Cobertura de nubes",
        "desc_label": "Descripción:",
        "last_update_caption": "Última actualización de la estación:",
        "location_header": "📍 Ubicación",
        "map_warning": "No se pudieron obtener las coordenadas para mostrar el mapa.",
        "error_city_not_found": "Error de conexión o API: No se pudo obtener el clima. Verifica el nombre de la ciudad.",
        "error_processing": "No se pudo procesar la respuesta de la API. La ciudad podría no ser válida.",
        "error_no_city": "Por favor, escribe el nombre de una ciudad.",
        "am_pm": ("a. m.", "p. m."),
        "date_format": "%A, %d de %B de %Y, %I:%M",
        "forecast_header": "📅 Pronóstico a 5 Días",
        "advice_header": "💡 Consejo del Día",
        "connector_in": "en",
        "precip_forecast_header": "💧 Pronóstico de Lluvia",
        "precip_forecast_phrases": {
            "rain_now": "¡Atención! Es muy probable que comience a llover en cualquier momento.",
            "rain_in_one_hour": "Es muy probable que llueva dentro de la próxima hora.",
            "rain_in_hours": "Se espera lluvia en aproximadamente {hours} horas.",
            "no_rain": "No se esperan lluvias en las próximas 12 horas. ✅"
        },
        "advice_phrases": {
            "hot": "¡Hace mucho calor! Mantente hidratado y busca la sombra. 💧",
            "cold": "¡Brrr, hace frío! Asegúrate de abrigarte bien. 🧥",
            "rain": "Hay lluvia en el pronóstico. ¡No olvides tu paraguas! ☔",
            "windy": "El viento está fuerte. ¡Ten cuidado con objetos sueltos! 🌬️",
            "storm": "¡Se esperan tormentas! Es mejor quedarse en un lugar seguro. ⛈️",
            "snow": "¡Va a nevar! Tiempo perfecto para un chocolate caliente. ❄️",
            "fog": "Hay niebla, conduce con precaución. 🌫️",
            "clear": "¡Un día despejado y hermoso! Perfecto para salir a disfrutar. 😎",
            "cloudy": "El cielo está nublado, pero sigue siendo un buen día. ☁️",
            "default": "Revisa el clima y planifica tu día. ¡Que tengas uno excelente! 👍"
        }
    },
    "Estados Unidos": {
        "country_code": "US",
        "locale": "en_US.UTF-8",
        "lang_api": "en",
        "api_units": "imperial",
        "temp_unit": "°F",
        "wind_unit": "mph",
        "precip_unit": "in",
        "title": "🌦️ Weather & Forecast 🌦️",
        "subtitle": "Enter your city or state to get real-time weather and a 5-day forecast.",
        "city_label": "City",
        "default_city": "New York",
        "button_label": "Get Weather",
        "spinner_text": "Fetching data for",
        "temp_label": "🌡️ Temperature",
        "wind_label": "🌬️ Wind",
        "humidity_label": "💧 Humidity",
        "precip_label": "🌧️ Precipitation (1h)",
        "clouds_label": "☁️ Cloud Cover",
        "desc_label": "Description:",
        "last_update_caption": "Last station update:",
        "location_header": "📍 Location",
        "map_warning": "Could not get coordinates to display the map.",
        "error_city_not_found": "Connection or API Error: Could not get weather. Please check the city name.",
        "error_processing": "Could not process the API response. The city might be invalid.",
        "error_no_city": "Please, enter a city name.",
        "am_pm": ("AM", "PM"),
        "date_format": "%A, %B %d, %Y, %I:%M",
        "forecast_header": "📅 5-Day Forecast",
        "advice_header": "💡 Tip of the Day",
        "connector_in": "in",
        "precip_forecast_header": "💧 Rain Forecast",
        "precip_forecast_phrases": {
            "rain_now": "Attention! It is very likely to start raining at any moment.",
            "rain_in_one_hour": "It's very likely to rain within the next hour.",
            "rain_in_hours": "Rain is expected in approximately {hours} hours.",
            "no_rain": "No rain is expected in the next 12 hours. ✅"
        },
        "advice_phrases": {
            "hot": "It's very hot! Stay hydrated and seek shade. 💧",
            "cold": "Brrr, it's cold! Make sure to bundle up. 🧥",
            "rain": "Rain is in the forecast. Don't forget your umbrella! ☔",
            "windy": "It's windy out there! Be careful with loose objects. 🌬️",
            "storm": "Storms are expected! It's best to stay indoors. ⛈️",
            "snow": "It's going to snow! Perfect weather for a hot chocolate. ❄️",
            "fog": "There is fog, drive carefully. 🌫️",
            "clear": "A beautiful clear day! Perfect for going out and enjoying. 😎",
            "cloudy": "The sky is cloudy, but it's still a good day. ☁️",
            "default": "Check the weather and plan your day. Have a great one! 👍"
        }
    }
}

def prepare_city_name(city_name: str, country_code: str) -> str:
    city_name = city_name.strip()
    if "," not in city_name:
        city_name += f", {country_code}"
    return city_name

@st.cache_data(ttl=600)
def get_weather_data(city_name: str, lang: str, api_units: str, config: dict) -> dict | None:
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": api_units,
        "lang": lang
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        timestamp = data.get("dt", 0)
        measurement_time = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
        temp_raw = data.get("main", {}).get("temp")
        temperature_rounded = round(temp_raw) if isinstance(temp_raw, (int, float)) else "N/A"
        wind_speed_raw = data.get("wind", {}).get("speed", 0)
        if api_units == "metric":
            wind_speed = round(wind_speed_raw * 3.6)
        else:
            wind_speed = round(wind_speed_raw)
        precip_raw = data.get("rain", {}).get("1h", 0)
        if api_units == "imperial":
            precipitation = round(precip_raw / 25.4, 2)
        else:
            precipitation = precip_raw
        return {
            "temperature": temperature_rounded,
            "precipitation": precipitation,
            "wind": wind_speed,
            "humidity": data.get("main", {}).get("humidity", "N/A"),
            "description": data.get("weather", [{}])[0].get("description", "N/A"),
            "cloudiness": data.get("clouds", {}).get("all", "N/A"),
            "time": measurement_time,
            "lat": data.get("coord", {}).get("lat", None),
            "lon": data.get("coord", {}).get("lon", None),
        }
    except requests.exceptions.RequestException as e:
        st.error(config["error_city_not_found"])
        return None
    except (KeyError, IndexError):
        st.error(config["error_processing"])
        return None

@st.cache_data(ttl=600)
def get_forecast_data(lat: float, lon: float, api_units: str) -> dict | None:
    temperature_unit = "celsius" if api_units == "metric" else "fahrenheit"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min",
        "hourly": "precipitation_probability",
        "forecast_days": 5,
        "forecast_hours": 24,
        "timezone": "auto",
        "temperature_unit": temperature_unit
    }
    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.warning("No se pudo obtener el pronóstico del tiempo.")
        return None

def get_precipitation_forecast_message(forecast: dict, config: dict) -> str:
    phrases = config["precip_forecast_phrases"]
    try:
        hourly_data = forecast["hourly"]
        probabilities = hourly_data["precipitation_probability"]
        
        for i, prob in enumerate(probabilities[:12]):
            if prob > 40:
                if i == 0:
                    return phrases["rain_now"]
                elif i == 1:
                    return phrases["rain_in_one_hour"]
                else:
                    return phrases["rain_in_hours"].format(hours=i)
        
        return phrases["no_rain"]

    except (KeyError, IndexError):
        return ""

def weather_code_to_icon(code: int) -> str:
    if code in [0, 1]: return "☀️"
    if code in [2]: return "⛅"
    if code in [3]: return "☁️"
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    if code in [66, 67, 71, 73, 75, 77, 85, 86]: return "❄️"
    if code in [95, 96, 99]: return "⛈️"
    return "🌍"

def get_weather_advice(weather: dict, config: dict, api_units: str) -> str:
    phrases = config["advice_phrases"]
    description = weather.get("description", "").lower()
    temp = weather.get("temperature")
    hot_temp = 30 if api_units == 'metric' else 86
    cold_temp = 10 if api_units == 'metric' else 50
    if any(keyword in description for keyword in ["tormenta", "storm"]): return phrases["storm"]
    if any(keyword in description for keyword in ["lluvia", "rain", "llovizna", "drizzle"]): return phrases["rain"]
    if any(keyword in description for keyword in ["nieve", "snow"]): return phrases["snow"]
    if any(keyword in description for keyword in ["niebla", "fog", "mist"]): return phrases["fog"]
    if isinstance(temp, (int, float)):
        if temp > hot_temp: return phrases["hot"]
        if temp < cold_temp: return phrases["cold"]
    if "despejado" in description or "clear" in description: return phrases["clear"]
    if "nubes" in description or "clouds" in description or "nublado" in description: return phrases["cloudy"]
    return phrases["default"]

def classify_weather(weather: dict, api_units: str) -> tuple[str, str]:
    temp = weather.get("temperature", "N/A")
    precip = weather.get("precipitation", 0)
    wind = weather.get("wind", "N/A")
    humidity = weather.get("humidity", "N/A")
    if api_units == 'metric':
        precip_threshold, wind_threshold, hot_temp, cold_temp, uncomfortable_temp = 10, 50, 35, 0, 30
    else:
        precip_threshold, wind_threshold, hot_temp, cold_temp, uncomfortable_temp = 0.4, 31, 95, 32, 86
    if precip > precip_threshold: return ("Muy mojado / Very Wet", "💧🟦🟦🟦💧")
    if wind != "N/A" and wind > wind_threshold: return ("Mucho viento / Very Windy", "🌬️⬛⬜⬛🌬️")
    if temp != "N/A":
        if temp > hot_temp: return ("Muy caliente / Very Hot", "🔥🟥🟧🟥🔥")
        if temp < cold_temp: return ("Muy frio / Very Cold", "❄️🟦⬜🟦❄️")
    if temp != "N/A" and humidity != "N/A" and temp > uncomfortable_temp and humidity > 70: 
        return ("Muy incomodo / Very Uncomfortable", "😓_🟨🟧🟨😓")
    return ("Normal / Normal", "🙂⬜⬜⬜🙂")

def get_temp_color(temp) -> str:
    if not isinstance(temp, (int, float)): return "black"
    if temp <= 32 and temp > 0: return "cyan"
    if temp <= 0: return "blue"
    if temp <= 20: return "cyan"
    if temp <= 86: return "orange"
    return "red"

def get_user_friendly_description(weather: dict, lang: str) -> str:
    cloudiness = weather.get("cloudiness", 0)
    api_description = weather.get("description", "").capitalize()
    if lang == 'es':
        if any(keyword in api_description.lower() for keyword in ["lluvia", "tormenta", "nieve", "niebla"]): return api_description
        if cloudiness <= 10: return "Cielo despejado y soleado"
        elif 11 <= cloudiness <= 40: return "Parcialmente nublado"
        else: return "Cielo mayormente cubierto"
    else:
        if any(keyword in api_description.lower() for keyword in ["rain", "storm", "snow", "fog", "mist"]): return api_description
        if cloudiness <= 10: return "Clear and sunny sky"
        elif 11 <= cloudiness <= 40: return "Partly cloudy"
        else: return "Mostly overcast sky"

st.set_page_config(page_title="EOLO", page_icon="⛅")

try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("API Key not found. Make sure you have your .streamlit/secrets.toml file.")
    st.stop()

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

selected_country_name = st.selectbox("Selecciona un país / Select a country", options=list(COUNTRY_CONFIG.keys()))
config = COUNTRY_CONFIG[selected_country_name]

try:
    locale.setlocale(locale.LC_TIME, config['locale'])
except locale.Error:
    st.warning(f"Could not set locale to {config['locale']}. Date formatting may be incorrect.")

now = datetime.now()
am_pm = config['am_pm'][0] if now.hour < 12 else config['am_pm'][1]
formatted_date_time = now.strftime(f"{config['date_format']} {am_pm}")
st.markdown(f"<p style='text-align: right; color: grey;'>{formatted_date_time}</p>", unsafe_allow_html=True)

st.title(config['title'])
st.markdown(config['subtitle'])

with st.form("weather_form"):
    city_name = st.text_input(config['city_label'], value=config['default_city'])
    submitted = st.form_submit_button(config['button_label'])

if submitted:
    if not city_name:
        st.error(config['error_no_city'])
    else:
        city_name_prepared = prepare_city_name(city_name, config['country_code'])
        with st.spinner(f"{config['spinner_text']} {city_name_prepared}..."):
            weather = get_weather_data(city_name_prepared, config['lang_api'], config['api_units'], config)
        if weather:
            label, icon = classify_weather(weather, config['api_units'])
            temp_color = get_temp_color(weather["temperature"])
            st.markdown(f"<h2 style='text-align: center; color:{temp_color};'>{icon}<br>{label} {config['connector_in']} {city_name_prepared.split(',')[0].strip()}</h2>", unsafe_allow_html=True)
            st.markdown("---")
            st.subheader(config['advice_header'])
            advice = get_weather_advice(weather, config, config['api_units'])
            st.info(advice)
            
            lat, lon = weather.get("lat"), weather.get("lon")
            forecast = None
            if lat is not None and lon is not None:
                forecast = get_forecast_data(lat, lon, config['api_units'])

            if forecast:
                st.subheader(config['precip_forecast_header'])
                precip_message = get_precipitation_forecast_message(forecast, config)
                st.warning(precip_message)

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label=config['temp_label'], value=f"{weather.get('temperature', 'N/A')} {config['temp_unit']}")
                st.metric(label=config['wind_label'], value=f"{weather.get('wind', 'N/A')} {config['wind_unit']}")
            with col2:
                st.metric(label=config['humidity_label'], value=f"{weather.get('humidity', 'N/A')} %")
                st.metric(label=config['precip_label'], value=f"{weather.get('precipitation', 'N/A')} {config['precip_unit']}")
            with col3:
                st.metric(label=config['clouds_label'], value=f"{weather.get('cloudiness', 'N/A')} %")
            
            friendly_description = get_user_friendly_description(weather, config['lang_api'])
            st.success(f"**{config['desc_label']}** {friendly_description}")
            st.caption(f"{config['last_update_caption']} {weather.get('time', 'N/A')}")
            
            if lat is not None and lon is not None:
                if forecast and "daily" in forecast:
                    st.markdown("---")
                    st.subheader(config['forecast_header'])
                    forecast_data = forecast["daily"]
                    cols = st.columns(5)
                    for i in range(5):
                        with cols[i]:
                            date = datetime.strptime(forecast_data["time"][i], "%Y-%m-%d")
                            day_name = date.strftime("%a").capitalize()
                            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{day_name}</p>", unsafe_allow_html=True)
                            icon = weather_code_to_icon(forecast_data["weathercode"][i])
                            st.markdown(f"<p style='text-align:center; font-size: 2em;'>{icon}</p>", unsafe_allow_html=True)
                            temp_max = round(forecast_data["temperature_2m_max"][i])
                            temp_min = round(forecast_data["temperature_2m_min"][i])
                            st.metric(label="Máx", value=f"{temp_max}{config['temp_unit']}")
                            st.metric(label="Mín", value=f"{temp_min}{config['temp_unit']}")
                
                st.markdown("---")
                st.subheader(config['location_header'])
                map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                st.map(map_data, zoom=10)
            else:
                st.warning(config['map_warning'])
