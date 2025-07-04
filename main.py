import streamlit as st
from datetime import datetime
import warnings
from audiorecorder import audiorecorder
from io import BytesIO
import random

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Traductor Arhuaco", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.image("./assets/escudo.png", use_container_width=True)
    st.title("Traductor Arhuaco - Español")
    st.markdown("""
    Esta herramienta busca preservar y facilitar la comunicación en la lengua Arhuaca, 
    permitiendo traducciones entre el idioma Arhuaco y el español.
    """)
    st.image("./assets/indigena.jpeg", caption="Pueblo Arhuaco", use_container_width=True)

# --- CSS ---
st.markdown("""
    <style>
    .streamlit-expanderHeader {
        font-size: 1.1rem;
    }
    .streamlit-expanderContent {
        min-height: 180px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "modo" not in st.session_state:
    st.session_state.modo = "Arhuaco -> Español"
if "modo_anterior" not in st.session_state:
    st.session_state.modo_anterior = st.session_state.modo
if "audio_key" not in st.session_state:
    st.session_state.audio_key = str(random.randint(0, 1000000))

# --- HEADER ---
st.title("🗣️ Traductor Arhuaco ↔ Español")
modo = st.selectbox("Selecciona el modo de traducción:", ["Arhuaco -> Español", "Español -> Arhuaco"])
st.session_state.modo = modo

# Reiniciar historial si cambia de modo
if st.session_state.modo != st.session_state.modo_anterior:
    st.session_state.messages = []
    st.session_state.audio_key = str(random.randint(0, 1000000))
    st.session_state.modo_anterior = st.session_state.modo

# --- FUNCIONES ---
def agregar_mensaje(rol, contenido, tipo="texto"):
    st.session_state.messages.append({
        "rol": rol,
        "contenido": contenido,
        "tipo": tipo,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# --- FORMULARIO ---
with st.container():
    if modo == "Arhuaco -> Español":
        col1, _ = st.columns([2,1])
        with col1:
            with st.expander("🎤 Grabar audio en Arhuaco", expanded=True):
                audio = audiorecorder("Grabar audio", "Detener grabación", key=st.session_state.audio_key)
                if len(audio) > 0:
                    audio_buffer = BytesIO()
                    audio.export(audio_buffer, format="wav")
                    audio_bytes = audio_buffer.getvalue()
                    st.audio(audio_bytes, format="audio/wav")
                    agregar_mensaje("usuario", "Audio grabado en Arhuaco", tipo="audio")
                    agregar_mensaje("asistente", "Traducción simulada al español")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            with st.expander("💬 Escribir texto en español (opcional)", expanded=True):
                texto = st.text_input("Escribe aquí:")
        with col2:
            with st.expander("🎤 Grabar audio en español (opcional)", expanded=True):
                audio = audiorecorder("Grabar audio", "Detener grabación", key=st.session_state.audio_key)

        if texto:
            agregar_mensaje("usuario", texto)
            agregar_mensaje("asistente", "Traducción simulada al Arhuaco")
        elif len(audio) > 0:
            audio_buffer = BytesIO()
            audio.export(audio_buffer, format="wav")
            audio_bytes = audio_buffer.getvalue()
            st.audio(audio_bytes, format="audio/wav")
            agregar_mensaje("usuario", "Audio grabado en español", tipo="audio")
            agregar_mensaje("asistente", "Traducción simulada al Arhuaco")

# --- HISTORIAL ---
st.markdown("---")
st.markdown("### 🕓 Historial de conversación")

with st.container():
    for msg in reversed(st.session_state.messages):
        with st.chat_message(msg["rol"]):
            if msg["tipo"] == "texto":
                st.markdown(msg["contenido"])
            elif msg["tipo"] == "audio":
                st.markdown(f"🎧 Audio grabado a las {msg['timestamp']}")

# --- BOTÓN BORRAR ---
if st.button("🗑️ Borrar historial"):
    st.session_state.messages = []
    st.session_state.audio_key = str(random.randint(0, 1000000))  # cambia clave del componente
    st.rerun()
