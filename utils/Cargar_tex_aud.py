from gtts import gTTS
import io
import pygame

# Crear audio en memoria
text = "Que es lo que pasa Alex?!"
tts = gTTS(text, lang="es")
mp3_fp = io.BytesIO()
tts.write_to_fp(mp3_fp)

# Reproducir el audio con pygame
mp3_fp.seek(0)
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(mp3_fp, 'mp3')
pygame.mixer.music.play()

# Esperar a que termine
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)
