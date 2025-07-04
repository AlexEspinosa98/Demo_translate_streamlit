import streamlit as st
from datetime import datetime
import warnings
from audiorecorder import audiorecorder
from io import BytesIO
import random
import time

from utils.wav_service import Transcriber, Wav2Vec2ModelLoader
from utils.translator import Translator
from utils.json_guide import spanish2arhuaco, arhuaco2spanish
from transformers import pipeline
from utils.spanish_transcribe import SpanishTranscriber

# --- CONFIGURACIÓN DEL MODELO ---
dropbox_url = "https://www.dropbox.com/scl/fi/3ihcwk0v68ai6m72s5s7v/modelo_guardado.zip?rlkey=za3p7nh0boo5qsrgiyxufx6sb&st=bm8rd8p0&dl=1"
zip_filename = "modelo_guardado.zip"
extract_folder = "modelo_extraido"

if "model" not in st.session_state:
    st.info("Inicializando modelos. Esto puede tardar un momento...")
    t0 = time.perf_counter()

    # Arhuaco ASR
    loader = Wav2Vec2ModelLoader(dropbox_url, zip_filename, extract_folder)
    loader.download_and_extract()
    loader.load_model()
    model, processor = loader.get_model()
    st.session_state["model"] = model
    st.session_state["processor"] = processor
    st.session_state["transcriber_arhuaco"] = Transcriber(model, processor)

    # Traductores
    st.session_state["translator_arhuaco"] = Translator(spanish2arhuaco)
    st.session_state["translator_espanol"] = Translator(arhuaco2spanish)

    # Español ASR (Whisper Tiny)
    asr_es = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
    st.session_state["asr_es"] = SpanishTranscriber(asr_es)

    t1 = time.perf_counter()
    st.success(f"✅ Modelos listos en {t1 - t0:.2f} segundos TOT.")

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
    .streamlit-expanderHeader { font-size: 1.1rem; }
    .streamlit-expanderContent { min-height: 180px; }
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
                    st.info("Procesando audio...")
                    audio_buffer = BytesIO()
                    audio.export(audio_buffer, format="wav")
                    audio_bytes = audio_buffer.getvalue()
                    st.audio(audio_bytes, format="audio/wav")

                    texto_transcrito = st.session_state["transcriber_arhuaco"].transcribe_bytes(audio_bytes)
                    traduccion = st.session_state["translator_espanol"].translate(texto_transcrito)

                    # Mostrar en dos columnas
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.markdown("**Arhuaco**")
                        st.markdown(f"> {texto_transcrito}")
                    with col_t2:
                        st.markdown("**Español**")
                        st.markdown(f"> {traduccion['translated']}")

                    agregar_mensaje("usuario", "Audio grabado en Arhuaco", tipo="audio")
                    agregar_mensaje("asistente", traduccion["translated"])

    else:
        col1, col2 = st.columns([2,1])
        with col1:
            with st.expander("💬 Escribir texto en español (opcional)", expanded=True):
                texto = st.text_input("Escribe aquí:")
        with col2:
            with st.expander("🎤 Grabar audio en español (opcional)", expanded=True):
                audio = audiorecorder("Grabar audio", "Detener grabación", key=st.session_state.audio_key)

        if texto:
            agregar_mensaje("usuario", texto)
            traduccion = st.session_state["translator_arhuaco"].translate(texto)
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("**Español**")
                st.markdown(f"> {texto}")
            with col_t2:
                st.markdown("**Arhuaco**")
                st.markdown(f"> {traduccion['translated']}")
            agregar_mensaje("asistente", traduccion["translated"])

        elif len(audio) > 0:
            st.info("Procesando audio...")
            audio_buffer = BytesIO()
            audio.export(audio_buffer, format="wav")
            audio_bytes = audio_buffer.getvalue()
            st.audio(audio_bytes, format="audio/wav")

            texto_transcrito = st.session_state["asr_es"].transcribe(audio_bytes)

            if not texto_transcrito:
                st.error("No se pudo transcribir el audio. Por favor, intenta de nuevo.")
            else:
                traduccion = st.session_state["translator_arhuaco"].translate(texto_transcrito)
                agregar_mensaje("usuario", "Audio grabado en español", tipo="audio")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown("**Español**")
                    st.markdown(f"> {texto_transcrito}")
                with col_t2:
                    st.markdown("**Arhuaco**")
                    st.markdown(f"> {traduccion['translated']}")
                agregar_mensaje("asistente", traduccion["translated"])

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
    st.session_state.audio_key = str(random.randint(0, 1000000))
    st.rerun()
