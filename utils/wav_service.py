import soundfile as sf
import numpy as np
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import os
import torch
import requests
import zipfile
from io import BytesIO
import time


class Wav2Vec2ModelLoader:
    def __init__(self, dropbox_url, zip_filename, extract_folder, modelo_subfolder="modelo_guardado"):
        self.dropbox_url = dropbox_url
        self.zip_filename = zip_filename
        self.extract_folder = extract_folder
        self.modelo_path = os.path.join(extract_folder, modelo_subfolder)
        self.model = None
        self.processor = None

    def download_and_extract(self):
        if not os.path.exists(self.zip_filename):
            print("⚙️ Descargando modelo...")
            t0 = time.perf_counter()
            response = requests.get(self.dropbox_url)
            with open(self.zip_filename, "wb") as f:
                f.write(response.content)
            t1 = time.perf_counter()
            print(f"✅ Descarga completada en {t1 - t0:.2f} segundos.")
        else:
            print("✅ Archivo zip ya existe, no se descarga.")

        if not os.path.exists(self.extract_folder):
            print("⚙️ Extrayendo zip...")
            t0 = time.perf_counter()
            with zipfile.ZipFile(self.zip_filename, "r") as zip_ref:
                zip_ref.extractall(self.extract_folder)
            t1 = time.perf_counter()
            print(f"✅ Extracción completada en {t1 - t0:.2f} segundos.")
        else:
            print("✅ Carpeta de modelo ya extraída.")

    def load_model(self):
        print("⚙️ Cargando modelo Wav2Vec2...")
        t0 = time.perf_counter()
        self.model = Wav2Vec2ForCTC.from_pretrained(self.modelo_path)
        self.processor = Wav2Vec2Processor.from_pretrained(self.modelo_path)
        self.model.eval()
        t1 = time.perf_counter()
        print(f"✅ Modelo cargado en {t1 - t0:.2f} segundos.")

    def get_model(self):
        return self.model, self.processor


class Transcriber:
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor

    def transcribe_bytes(self, audio_bytes):
        print("⚙️ Iniciando transcripción de audio con soundfile...")
        import time

        t0 = time.perf_counter()

        # Cargar audio desde BytesIO
        data, sample_rate = sf.read(BytesIO(audio_bytes))
        t1 = time.perf_counter()
        print(f"✅ Carga de audio en {t1 - t0:.2f}s")

        # Convertir a mono si necesario
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        # Remuestrear si necesario
        if sample_rate != 16000:
            import librosa
            t_resample0 = time.perf_counter()
            data = librosa.resample(data, orig_sr=sample_rate, target_sr=16000)
            t_resample1 = time.perf_counter()
            print(f"✅ Remuestreo en {t_resample1 - t_resample0:.2f}s")
            sample_rate = 16000

        input_values = self.processor(
            data,
            sampling_rate=sample_rate,
            return_tensors="pt"
        ).input_values

        with torch.no_grad():
            logits = self.model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]

        return transcription
