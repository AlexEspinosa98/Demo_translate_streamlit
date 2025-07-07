import streamlit as st
from datetime import datetime
import warnings
from audiorecorder import audiorecorder
from io import BytesIO
import random
import time

from gtts import gTTS

from utils.translator import Translator
from utils.json_guide import spanish2arhuaco, arhuaco2spanish
from transformers import pipeline
from utils.spanish_transcribe import SpanishTranscriber

# --- INICIALIZACIÓN DE MODELOS ---
if "model" not in st.session_state:
    with st.spinner("🔄 Inicializando modelos. Esto puede tardar un momento..."):
        t0 = time.perf_counter()

        st.session_state["translator_arhuaco"] = Translator(spanish2arhuaco)
        st.session_state["translator_espanol"] = Translator(arhuaco2spanish)

        asr_es = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
        st.session_state["asr_es"] = SpanishTranscriber(asr_es)

        t1 = time.perf_counter()

    st.toast(f"✅ Modelos listos en {t1 - t0:.2f} segundos TOT.")

warnings.filterwarnings("ignore")
st.set_page_config(
    page_title="Traductor Arhuaco SAYTA",
    layout="wide",
)

dif_audios = {
    "duzano": "./recorders/duzano.wav",
    "azi mezare": "./recorders/azi_mezare.wav",
}


# --- CSS PERSONALIZADO ---
st.markdown(f"""
    <style>
    html, body, [class*="css"]  {{
        background-color: #FFFFFF;
        color: #000000;
    }}
    .main-title {{
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2em;
        color: #004A87;
    }}
    .big-title {{
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2em;
        color: #004A87;
    }}
    .subtitle {{
        font-size: 1.2rem;
        margin-bottom: 1em;
        color: #888888;
    }}
    .sayta-name {{
        font-size: 1.4rem;
        font-weight: bold;
        color: #00A50B;
        margin-top: -0.3em;
        margin-bottom: 1em;
    }}
    .stButton button {{
        background-color: #004A87;
        color: white;
        border: None;
        padding: 0.5em 1em;
        border-radius: 5px;
    }}
    .stButton button:hover {{
        background-color: #005CAB;
        color: white;
    }}
    .streamlit-expanderHeader {{
        font-size: 1.1rem;
        color: #004A87;
    }}
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
if "texto_entrada" not in st.session_state:
    st.session_state["texto_entrada"] = ""
if "texto_traducido" not in st.session_state:
    st.session_state["texto_traducido"] = ""
if "num_traducciones" not in st.session_state:
    st.session_state["num_traducciones"] = 0

# --- HEADER ORGANIZADO ---
st.markdown('<div class="main-title">Proyecto SAYTA</div>', unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("./assets/escudo.png", width=100)
with col_title:
    st.markdown('<div class="big-title">Traductor Arhuaco ↔ Español</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Esta herramienta busca preservar y facilitar la comunicación en la lengua Arhuaca, permitiendo traducciones entre el idioma Arhuaco y el español.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sayta-name">🌿 Universidad del Magdalena</div>', unsafe_allow_html=True)

# --- MODO DE TRADUCCIÓN ---
modo = st.selectbox("Selecciona el modo de traducción:", ["Arhuaco -> Español", "Español -> Arhuaco"])
st.session_state.modo = modo

if st.session_state.modo != st.session_state.modo_anterior:
    st.session_state.messages = []
    st.session_state.audio_key = str(random.randint(0, 1000000))
    st.session_state.modo_anterior = st.session_state.modo
    st.session_state["texto_entrada"] = ""
    st.session_state["texto_traducido"] = ""
    st.session_state["num_traducciones"] = 0

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
                    with st.spinner("🎙️ Procesando audio..."):
                        audio_buffer = BytesIO()
                        audio.export(audio_buffer, format="wav")
                        audio_bytes = audio_buffer.getvalue()
                        st.audio(audio_bytes, format="audio/wav")

                        texto_transcrito = st.session_state["asr_es"].transcribe(audio_bytes)
                        traduccion = st.session_state["translator_espanol"].translate(texto_transcrito)

                        st.session_state["texto_entrada"] = texto_transcrito
                        st.session_state["texto_traducido"] = traduccion["translated"]

                        agregar_mensaje("usuario", "Audio grabado en Arhuaco", tipo="audio")
                        agregar_mensaje("asistente", traduccion["translated"])
                        st.session_state["num_traducciones"] += 1

    else:
        col1, col2 = st.columns([2,1])
        with col1:
            with st.expander("💬 Escribir texto en español (opcional)", expanded=True):
                texto = st.text_input("Escribe aquí:")
        with col2:
            with st.expander("🎤 Grabar audio en español (opcional)", expanded=True):
                audio = audiorecorder("Grabar audio", "Detener grabación", key=st.session_state.audio_key)

        if texto:
            traduccion = st.session_state["translator_arhuaco"].translate(texto)
            st.session_state["texto_entrada"] = texto
            st.session_state["texto_traducido"] = traduccion["translated"]
            agregar_mensaje("usuario", texto)
            agregar_mensaje("asistente", traduccion["translated"])
            st.session_state["num_traducciones"] += 1

        elif len(audio) > 0:
            with st.spinner("🎙️ Procesando audio..."):
                audio_buffer = BytesIO()
                audio.export(audio_buffer, format="wav")
                audio_bytes = audio_buffer.getvalue()
                st.audio(audio_bytes, format="audio/wav")

                texto_transcrito = st.session_state["asr_es"].transcribe(audio_bytes)

                if not texto_transcrito:
                    st.error("No se pudo transcribir el audio. Por favor, intenta de nuevo.")
                else:
                    traduccion = st.session_state["translator_arhuaco"].translate(texto_transcrito)
                    st.session_state["texto_entrada"] = texto_transcrito
                    st.session_state["texto_traducido"] = traduccion["translated"]
                    agregar_mensaje("usuario", "Audio grabado en español", tipo="audio")
                    agregar_mensaje("asistente", traduccion["translated"])
                    st.session_state["num_traducciones"] += 1

# --- RESULTADOS Y AUDIO ---
if st.session_state["texto_entrada"] or st.session_state["texto_traducido"]:
    col_es, col_ar = st.columns(2)
    with col_es:
        st.text_area(
            "Español" if modo == "Español -> Arhuaco" else "Arhuaco",
            value=st.session_state["texto_entrada"],
            height=150,
            disabled=True
        )
    with col_ar:
        st.text_area(
            "Arhuaco" if modo == "Español -> Arhuaco" else "Español",
            value=st.session_state["texto_traducido"],
            height=150,
            disabled=True
        )

    if st.session_state["texto_traducido"]:
            
        if dif_audios.get(st.session_state["texto_traducido"].lower(), None):

            with open(dif_audios[st.session_state["texto_traducido"].lower()], "rb") as audio_file:
                audio_fp = audio_file.read()
        else:

            tts = gTTS(
                text=st.session_state["texto_traducido"],
                lang="es"
            )
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            st.markdown("### 🔊 Audio traducido:")
        st.audio(audio_fp, format="audio/mp3")

    st.info(f"📊 Número de traducciones realizadas: {st.session_state['num_traducciones']}")

# --- HISTORIAL ---
st.markdown("---")
st.markdown("### 🕓 Historial de conversación")
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
    st.session_state["texto_entrada"] = ""
    st.session_state["texto_traducido"] = ""
    st.session_state["num_traducciones"] = 0
    st.rerun()
