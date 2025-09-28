import streamlit as st
import requests
from datetime import datetime
import pandas as pd  


try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("API Key no encontrada. Asegúrate de crear tu archivo .streamlit/secrets.toml")
    st.stop()

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


def prepare_city_name(city_name: str) -> str:
    """Agrega ', MX' automáticamente si no se especifica un país."""
    city_name = city_name.strip()
    if "," not in city_name:
        city_name += ", MX"
    return city_name

def get_weather_data(city_name: str) -> dict | None:
    """Obtiene datos del clima, incluyendo coordenadas, % de nubes y hora de la medición."""
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric",
        "lang": "es"
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        timestamp = data.get("dt", 0)
        measurement_time = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

        temp_raw = data.get("main", {}).get("temp")
        temperature_rounded = round(temp_raw) if isinstance(temp_raw, (int, float)) else "N/A"

        return {
            "temperature": temperature_rounded,
            "precipitation": data.get("rain", {}).get("1h", 0),
            "wind": round(data.get("wind", {}).get("speed", 0) * 3.6),
            "humidity": data.get("main", {}).get("humidity", "N/A"),
            "description": data.get("weather", [{}])[0].get("description", "N/A"),
            "cloudiness": data.get("clouds", {}).get("all", "N/A"),
            "time": measurement_time,
            
            "lat": data.get("coord", {}).get("lat", None),
            "lon": data.get("coord", {}).get("lon", None),
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión o API: No se pudo obtener el clima. Verifica el nombre de la ciudad.")
        return None
    except (KeyError, IndexError):
        st.error("No se pudo procesar la respuesta de la API. La ciudad podría no ser válida.")
        return None

def classify_weather(weather: dict) -> tuple[str, str]:
    """Clasifica el estado general del clima usando una lógica de prioridad."""
    temp = weather.get("temperature", "N/A")
    precip = weather.get("precipitation", 0)
    wind = weather.get("wind", "N/A")
    humidity = weather.get("humidity", "N/A")

    if precip > 10:
        return ("Muy mojado", "💧🟦🟦🟦💧")
    if wind != "N/A" and wind > 50:
        return ("Mucho viento", "🌬️⬛⬜⬛🌬️")
    if temp != "N/A":
        if temp > 35:
            return ("Muy caliente", "🔥🟥🟧🟥🔥")
        if temp < 0:
            return ("Muy frio", "❄️🟦⬜🟦❄️")
    if temp != "N/A" and humidity != "N/A" and temp > 30 and humidity > 70:
        return ("Muy incomodo", "😓🟨🟧🟨😓")
    return ("Normal", "🙂⬜⬜⬜🙂")

def get_temp_color(temp) -> str:
    """Devuelve un color CSS según la temperatura."""
    if not isinstance(temp, (int, float)):
        return "black"
    if temp <= 0: return "blue"
    if temp <= 20: return "cyan"
    if temp <= 30: return "orange"
    return "red"

def get_user_friendly_description(weather: dict) -> str:
    """Genera una descripción más detallada y amigable basada en los datos."""
    cloudiness = weather.get("cloudiness", 0)
    api_description = weather.get("description", "")

    if any(keyword in api_description for keyword in ["lluvia", "tormenta", "nieve", "niebla"]):
        return api_description.capitalize()

    if cloudiness <= 10:
        return "Cielo despejado y soleado"
    elif 11 <= cloudiness <= 40:
        return "Parcialmente nublado"
    elif 41 <= cloudiness <= 70:
        return "Mayormente nublado"
    elif 71 <= cloudiness <= 90:
        return "Nublado con algunos claros"
    else:
        return "Cielo completamente cubierto"


st.set_page_config(page_title="App del clima", page_icon="⛅")
st.title("🌦️ Clima Actual De Tu Ciudad 🌦️")

st.markdown(
    "Escribe tu ciudad para obtener el clima en tiempo real."
)

with st.form("weather_form"):
    city_name = st.text_input("Ciudad", value="Campeche")
    submitted = st.form_submit_button("Ver el clima")

if submitted:
    if not city_name:
        st.error("Por favor, escribe el nombre de una ciudad.")
    else:
        city_name_prepared = prepare_city_name(city_name)
        
        with st.spinner(f"Obteniendo el clima para {city_name_prepared}..."):
            weather = get_weather_data(city_name_prepared)
        
        if weather:
            label, icon = classify_weather(weather)
            temp_color = get_temp_color(weather["temperature"])
            
            st.markdown(f"<h2 style='text-align: center; color:{temp_color};'>{icon}<br>{label} en {city_name_prepared.split(',')[0].strip()}</h2>", unsafe_allow_html=True)
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="🌡️ Temperatura", value=f"{weather.get('temperature', 'N/A')} °C")
                st.metric(label="🌬️ Viento", value=f"{weather.get('wind', 'N/A')} km/h")
            with col2:
                st.metric(label="💧 Humedad", value=f"{weather.get('humidity', 'N/A')} %")
                st.metric(label="🌧️ Precipitación (1h)", value=f"{weather.get('precipitation', 'N/A')} mm")
            with col3:
                st.metric(label="☁️ Cobertura de nubes", value=f"{weather.get('cloudiness', 'N/A')} %")

            friendly_description = get_user_friendly_description(weather)
            st.info(f"**Descripción:** {friendly_description}")
            
            st.caption(f"Última actualización de la estación: {weather.get('time', 'N/A')}")
            
            
            st.markdown("---")
            st.subheader("📍 Ubicación")
            
            
            if weather.get("lat") is not None and weather.get("lon") is not None:
                
                map_data = pd.DataFrame({
                    'lat': [weather['lat']],
                    'lon': [weather['lon']]
                })
                
                st.map(map_data, zoom=10)
            else:
                st.warning("No se pudieron obtener las coordenadas para mostrar el mapa.")
