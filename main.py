import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av

st.set_page_config(page_title="Maku Kaku - Traductor Arhuaco <-> Español", layout="centered")

st.title("🗣️ Maku Kaku")
st.subheader("Traductor interactivo Arhuaco ↔ Español")

translation_direction = st.radio(
    "Selecciona dirección de traducción:",
    ("Arhuaco ➡ Español", "Español ➡ Arhuaco")
)

st.markdown("### 🎤 Graba tu audio")

class AudioProcessor(AudioProcessorBase):
    def recv_queued(self, frames):
        # Aquí cada frame es un fragmento de audio
        # Puedes convertir a bytes y procesar
        audio = b"".join([frame.to_ndarray().tobytes() for frame in frames])
        # Guarda en variable de ejemplo
        st.session_state['last_audio'] = audio

        # Opcional: mostrar mensaje
        st.info("Audio capturado y almacenado en variable.")
        return av.AudioFrame.from_ndarray(frames[0].to_ndarray(), layout="mono")

# Inicializar grabadora
webrtc_ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=256,
    video_receiver_size=0,
    client_settings={
        "media_stream_constraints": {
            "audio": True,
            "video": False,
        }
    },
    audio_processor_factory=AudioProcessor,
)

st.markdown("### 📝 Opcional: Escribe texto")
text_input = st.text_area("Texto a traducir")

if st.button("Traducir"):
    st.success("Aquí aparecerá la traducción...")
    if "last_audio" in st.session_state:
        st.write("Audio capturado (bytes):", len(st.session_state["last_audio"]), "bytes")

st.markdown("---")
st.caption("🌿 Este proyecto busca preservar y difundir las lenguas indígenas de la Sierra Nevada de Santa Marta.")
