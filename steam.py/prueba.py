# -------------------------
# IMPORTS (asegúrate que esto esté al inicio del archivo)
# -------------------------
import streamlit as st
import requests
from datetime import datetime, date

import folium
from streamlit_folium import st_folium
# -------------------------

# -------------------------
# 3. Interfaz Streamlit con MAPA en lugar de input de texto
# -------------------------
st.set_page_config(page_title="App del clima", page_icon="⛅")
st.title("🌦️ Clima con mapa interactivo")

st.markdown("Selecciona un lugar en el mapa para ver el clima")

# Crear mapa centrado en México por defecto
m = folium.Map(location=[19.4326, -99.1332], zoom_start=5)

# Mostrar mapa en Streamlit
map_data = st_folium(m, width=700, height=500)

# Input para fecha
selected_date = st.date_input("Fecha")

# Si el usuario hace clic en el mapa
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"Ubicación seleccionada: {lat}, {lon}")

    if selected_date == date.today():
        # Usa OpenWeather con coordenadas (tendrás que adaptar tu función get_weather_data)
        weather = get_weather_data(f"{lat},{lon}")
    else:
        weather = get_future_weather(lat, lon, selected_date)

    if weather:
        st.write(weather)
else:
    st.info("Haz clic en el mapa para seleccionar una ubicación")
