import streamlit as st
from datetime import datetime

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

# --- HEADER ---
st.title("🗣️ Traductor Arhuaco ↔ Español")
modo = st.selectbox("Selecciona el modo de traducción:", ["Arhuaco -> Español", "Español -> Arhuaco"])
st.session_state.modo = modo

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
        audio_data = st.file_uploader("Sube tu audio en Arhuaco", type=["wav", "mp3"])
        if audio_data:
            st.audio(audio_data)
            agregar_mensaje("usuario", "Audio en Arhuaco", tipo="audio")
            # Aquí vendría el llamado al traductor
            agregar_mensaje("asistente", "Traducción simulada al español")
    else:  # Español -> Arhuaco
        col1, col2 = st.columns([2, 1])
        with col1:
            texto = st.text_input("Escribe el texto en español:")
        with col2:
            audio_data = st.file_uploader("O sube un audio", type=["wav", "mp3"])

        if texto:
            agregar_mensaje("usuario", texto)
            # Aquí vendría la traducción
            agregar_mensaje("asistente", "Traducción simulada al Arhuaco")
        elif audio_data:
            st.audio(audio_data)
            agregar_mensaje("usuario", "Audio en español", tipo="audio")
            agregar_mensaje("asistente", "Traducción simulada al Arhuaco")

# --- HISTORIAL DE CONVERSACIÓN ---
st.markdown("---")
st.markdown("### 🕓 Historial de conversación")

for msg in st.session_state.messages:
    with st.chat_message(msg["rol"]):
        if msg["tipo"] == "texto":
            st.markdown(f"{msg['contenido']}")
        elif msg["tipo"] == "audio":
            st.markdown(f"🎧 Audio subido a las {msg['timestamp']}")

# --- OPCIONAL: Borrar historial ---
if st.button("🗑️ Borrar historial"):
    st.session_state.messages = []
