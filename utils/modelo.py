import torch
import torchaudio
import os
import requests
import zipfile
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# CONFIGURACIÓN
dropbox_url = "https://www.dropbox.com/scl/fi/3ihcwk0v68ai6m72s5s7v/modelo_guardado.zip?rlkey=za3p7nh0boo5qsrgiyxufx6sb&st=bm8rd8p0&dl=1"  # asegúrate de usar ?dl=1
zip_filename = "modelo_guardado.zip"
extract_folder = "modelo_extraido"
audio_path = "Data_set/Audio/Audio_16.wav"

# 1. Descargar el archivo zip si no existe
if not os.path.exists(zip_filename):
    print("Descargando archivo desde Dropbox...")
    response = requests.get(dropbox_url)
    with open(zip_filename, "wb") as f:
        f.write(response.content)
    print("Descarga completada.")

# 2. Extraer el contenido del zip
if not os.path.exists(extract_folder):
    print("Extrayendo archivo .zip...")
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    print("Extracción completada.")

# 3. Cargar el modelo desde la carpeta extraída
modelo_path = os.path.join(extract_folder, "modelo_guardado")  # cambia esto si tu modelo está en otra carpeta

print("Cargando modelo...")
model = Wav2Vec2ForCTC.from_pretrained(modelo_path)
processor = Wav2Vec2Processor.from_pretrained(modelo_path)
model.eval()
print("✅ Modelo cargado y listo para usar.")

# Cargar audio
waveform, sample_rate = torchaudio.load(audio_path)

# Convertir a mono si tiene más de un canal
if waveform.shape[0] > 1:
    waveform = torch.mean(waveform, dim=0, keepdim=True)

# Remuestrear si es necesario
if sample_rate != 16000:
    resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
    waveform = resampler(waveform)

# Eliminar la dimensión del canal: de [1, N] → [N]
input_values = processor(waveform.squeeze(), sampling_rate=16000, return_tensors="pt").input_values

# Inferencia
with torch.no_grad():
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]

# Resultado
print("Transcripción:", transcription)