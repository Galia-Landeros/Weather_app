import streamlit as st
import requests
from datetime import datetime

# 1. Importasciones y config

# 2. Functiones (API request and classificacion)

def get_weather_data(lat, lon, date):
    """
    Fetches weather data from NASA POWER API for the given latitude, longitude, and date.
    Returns a dictionary with temperature (°C), precipitation (mm/day), wind speed (km/h), and humidity (%).
    """
    # NASA POWER API endpoint for single-point daily data
    endpoint = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        "?parameters=T2M,PRECTOTCORR,WS2M,RH2M"
        f"&community=AG"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={date}"
        f"&end={date}"
        "&format=JSON"
    )
    response = requests.get(endpoint)
    data = response.json()
    try:
        weather = {
            "temperature": data["properties"]["parameter"]["T2M"][date],
            "precipitation": data["properties"]["parameter"]["PRECTOTCORR"][date],
            "wind": data["properties"]["parameter"]["WS2M"][date],
            "humidity": data["properties"]["parameter"]["RH2M"][date],
        }
    except Exception:
        return None
    return weather

def classify_weather(weather):
    """
    Classifies weather conditions and returns a tuple: (label, pixel_art_icon).
    """
    temp = weather["temperature"]
    precip = weather["precipitation"]
    wind = weather["wind"]
    humidity = weather["humidity"]

    if temp > 35:
        return ("Muy caliente", "🔥🟥🟧🟥🔥")
    elif temp < 0:
        return ("Muy frio", "❄️🟦⬜🟦❄️")
    elif precip > 10:
        return ("Muy mojado", "💧🟦🟦🟦💧")
    elif wind > 50:
        return ("Mucho viento", "🌬️⬛⬜⬛🌬️")
    elif temp > 30 and humidity > 70:
        return ("Muy incomodo", "😓🟨🟧🟨😓")
    else:
        return ("Normal", "🙂⬜⬜⬜🙂")

# 3. Streamlit interface

st.set_page_config(page_title="App del tiempo", page_icon="⛅")
st.title("🌦️ Pixel Art Condiciones del clima")

st.markdown(
    """
    Mete la latitud, longitud y tu fecha de viaje para ver el clima!!
    """
)

with st.form("weather_form"):
    lat = st.number_input("Latitud", min_value=-90.0, max_value=90.0, value=0.0, format="%.4f")
    lon = st.number_input("Longitud", min_value=-180.0, max_value=180.0, value=0.0, format="%.4f")
    date = st.date_input("Fecha", value=datetime.today())
    submitted = st.form_submit_button("Ve el clima")

if submitted:
    date_str = date.strftime("%Y%m%d")
    weather = get_weather_data(lat, lon, date_str)
    if weather:
        label, icon = classify_weather(weather)
        st.markdown(f"### {icon}")
        st.markdown(f"**Condition:** {label}")
        st.markdown(
            f"""
            - **Temperatura:** {weather['temperature']} °C  
            - **Precipitacion:** {weather['precipitation']} mm/day  
            - **Velocidad del viento:** {w  eather['wind']} km/h  
            - **Humedad:** {weather['humidity']} %
            """
        )
    else:
        st.error("Could not retrieve weather data. Please check your inputs or try a different date.")

st.info("Esta es una prueba de la app")