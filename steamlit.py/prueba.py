import streamlit as st
import random
from PIL import Image

# --- Configuración de la página ---
st.set_page_config(
    page_title="App del clima Móvil",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- codigo CSS basico para simular pantalla móvil (aun no m sale)---
st.markdown(
    """
    <style>
    .main {
        max-width: 400px;  /* ancho tipo móvil */
        margin: auto;
        padding: 10px;
    }
    .stButton>button {
        width: 100%;       /* botones grandes tipo app */
        height: 50px;
        font-size: 18px;streamlit run yourscript.pystreamlit run yourscript.py
        margin-top: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header tipo app ---
st.markdown(
    """
    <div style="text-align:center;">
        <img src="https://i.imgur.com/1Q9Z1Zm.png" width="120">
        <h2 style="font-family:monospace;">🌤️ Clima (prototipo) 🌤️</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Simular "pantallas" ---
pantalla = st.radio("Ir a:", ["Inicio", "Consulta Clima"], horizontal=True)

if pantalla == "Inicio":
    st.image("https://i.imgur.com/Fl9L2R9.png", width=200)
    st.write("Bienvenido a la app de clima tipo móvil!")
    st.write("Consulta tu posibilidad de condiciones extremas para tu ciudad y fecha.")
    
elif pantalla == "Consulta Clima":
    st.subheader("🔍 Consulta personalizada")
    ciudad = st.text_input("📍 Ciudad:", "Campeche")
    fecha = st.date_input("📅 Fecha:")
    condicion = st.selectbox(
        "🌡️ Condición a consultar:",
        ["Muy caliente", "Muy frio", "Muy ventoso", "Muy humedo", "Very Uncomfortable"]
    )

    if st.button("Consultar"):
        prob = random.randint(0, 100)
        st.success(f"Para {ciudad} en {fecha}, la probabilidad de **{condicion}** es:")
        st.progress(prob)
        st.write(f"➡️ {prob}%")

        # Pixel art según condición
        if condicion == "Very Hot":
            st.image("https://i.imgur.com/Fl9L2R9.png", caption="🔥 Muy Caluroso")
        elif condicion == "Very Cold":
            st.image("https://i.imgur.com/koPpMEU.png", caption="❄️ Muy Frío")
        elif condicion == "Very Windy":
            st.image("https://i.imgur.com/FWPLn8N.png", caption="💨 Muy Ventoso")
        elif condicion == "Very Wet":
            st.image("https://i.imgur.com/WRZp3nG.png", caption="🌧️ Muy Húmedo")
        else:
            st.image("https://i.imgur.com/7gUmRzO.png", caption="😓 Muy Incómodo")
