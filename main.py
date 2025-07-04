import streamlit as st
from datetime import datetime
import warnings
from audiorecorder import audiorecorder
from io import BytesIO

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

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "modo" not in st.session_state:
    st.session_state.modo = "Arhuaco -> Español"

if "modo_anterior" not in st.session_state:
    st.session_state.modo_anterior = st.session_state.modo

# --- HEADER ---
st.title("🗣️ Traductor Arhuaco ↔ Español")
modo = st.selectbox("Selecciona el modo de traducción:", ["Arhuaco -> Español", "Español -> Arhuaco"])
st.session_state.modo = modo

# Reiniciar historial si cambia de modo
if st.session_state.modo != st.session_state.modo_anterior:
    st.session_state.messages = []
    st.session_state.modo_anterior = st.session_state.modo

# --- FUNCIONES AUXILIARES ---
def agregar_mensaje(rol, contenido, tipo="texto"):
    st.session_state.messages.append({
        "rol": rol,
        "contenido": contenido,
        "tipo": tipo,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# --- FORMULARIO DE ENTRADA ---
with st.container():
    if modo == "Arhuaco -> Español":
        st.info("🎤 Grabación de audio (solo entrada de audio permitida en este modo)")
        audio = audiorecorder("Grabar audio", "Detener grabación")
        if len(audio) > 0:
            # Convertir AudioSegment a bytes
            audio_buffer = BytesIO()
            audio.export(audio_buffer, format="wav")
            audio_bytes = audio_buffer.getvalue()
            st.audio(audio_bytes, format="audio/wav")

            agregar_mensaje("usuario", "Audio grabado en Arhuaco", tipo="audio")
            agregar_mensaje("asistente", "Traducción simulada al español")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            texto = st.text_input("Escribe el texto en español:")
        with col2:
            audio = audiorecorder("Grabar audio", "Detener grabación")

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

for msg in st.session_state.messages:
    with st.chat_message(msg["rol"]):
        if msg["tipo"] == "texto":
            st.markdown(msg["contenido"])
        elif msg["tipo"] == "audio":
            st.markdown(f"🎧 Audio grabado a las {msg['timestamp']}")

# --- BORRAR HISTORIAL ---
if st.button("🗑️ Borrar historial"):
    st.session_state.messages = []
