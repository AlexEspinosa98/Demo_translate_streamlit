import io
import soundfile as sf


class SpanishTranscriber:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def transcribe(self, audio_bytes: bytes, generate_kwargs=None) -> str:
        import io
        import soundfile as sf
        try:
            data, samplerate = sf.read(io.BytesIO(audio_bytes))

            if len(data.shape) > 1:
                data = data.mean(axis=1)

            # Usa generate_kwargs si te lo pasan, si no usa uno por defecto
            if generate_kwargs is None:
                generate_kwargs = {"task": "transcribe", "language": "spanish"}

            result = self.pipeline(
                {
                    "array": data,
                    "sampling_rate": samplerate
                },
                generate_kwargs=generate_kwargs
            )
            return result["text"].lower().strip()

        except Exception as e:
            print(f"[ERROR] Fallo al transcribir audio: {e}")
            return ""
