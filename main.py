import streamlit as st
from datetime import datetime
import random
from io import BytesIO
from gtts import gTTS
import av
import numpy as np

from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

from transformers import pipeline
from utils.translator import Translator
from utils.json_guide import spanish2arhuaco, arhuaco2spanish

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="Traductor Arhuaco SAYTA",
    layout="wide",
)

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #FFFFFF;
        color: #000000;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2em;
        color: #004A87;
    }
    .big-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2em;
        color: #004A87;
    }
    .subtitle {
        font-size: 1.2rem;
        margin-bottom: 1em;
        color: #888888;
    }
    .sayta-name {
        font-size: 1.4rem;
        font-weight: bold;
        color: #00A50B;
        margin-top: -0.3em;
        margin-bottom: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<div class="main-title">Proyecto SAYTA</div>', unsafe_allow_html=True)
st.image("./assets/escudo.png", width=100)
st.markdown('<div class="big-title">Traductor Arhuaco ↔ Español</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Esta herramienta busca preservar y facilitar la comunicación en la lengua Arhuaca.</div>', unsafe_allow_html=True)
st.markdown('<div class="sayta-name">🌿 Universidad del Magdalena</div>', unsafe_allow_html=True)

# --- CARGA DE MODELOS ---
if "model_loaded" not in st.session_state:
    with st.spinner("🔄 Inicializando modelos..."):
        st.session_state["translator_arhuaco"] = Translator(spanish2arhuaco)
        st.session_state["translator_espanol"] = Translator(arhuaco2spanish)
        st.session_state["asr"] = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
        st.session_state["model_loaded"] = True
    st.success("✅ Modelos listos.")

# --- SELECCIÓN DE MODO ---
modo = st.selectbox("Selecciona el modo de traducción:", ["Arhuaco -> Español", "Español -> Arhuaco"])

# --- CLASE PARA PROCESAR AUDIO ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten()
        self.audio_frames.append(audio)
        return frame

# --- RECORDER ---
st.markdown("### 🎤 Graba tu voz")
webrtc_ctx = webrtc_streamer(
    key="speech",
    mode="SENDRECV",
    audio_receiver_size=256,
    client_settings={"media_stream_constraints": {"audio": True, "video": False}},
    audio_processor_factory=AudioProcessor,
)

# --- PROCESAR CUANDO SE DETENGA LA GRABACIÓN ---
if webrtc_ctx and webrtc_ctx.state.playing is False and webrtc_ctx.audio_processor:
    audio_data = np.concatenate(webrtc_ctx.audio_processor.audio_frames)
    audio_bytes = BytesIO()
    # Convertir a WAV en memoria
    import soundfile as sf
    sf.write(audio_bytes, audio_data, 16000, format="wav")
    audio_bytes.seek(0)

    st.audio(audio_bytes, format="audio/wav")

    with st.spinner("🔍 Transcribiendo..."):
        transcription = st.session_state["asr"](audio_bytes)["text"]
        st.success("✅ Transcripción completada")

    st.markdown("**Texto transcrito:**")
    st.write(transcription)

    with st.spinner("🌐 Traduciendo..."):
        if modo == "Arhuaco -> Español":
            traduccion = st.session_state["translator_espanol"].translate(transcription)["translated"]
        else:
            traduccion = st.session_state["translator_arhuaco"].translate(transcription)["translated"]
    st.success("✅ Traducción lista")

    st.markdown("**Traducción:**")
    st.write(traduccion)

    with st.spinner("🔈 Generando audio traducido..."):
        tts = gTTS(text=traduccion, lang="es")
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        st.audio(audio_fp, format="audio/mp3")

