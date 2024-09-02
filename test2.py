from dependencies.models import ManagerTTS
import time


tts = ManagerTTS()
print("-----Esperando inicio de animación")
tts.play("Hola, como estás? Me llamo Dionisio esto es una prueba larga", "Dionisio Schuyler", "es", "waveout")
print("-----Esperando inicio de animación")
tts.play("Hola, como estás? Me llamo Daisy esto es una prueba larga", "Daisy Studious", "es", "waveout", sync=True)
print("-----Iniciando animación")
tts.play("", "Daisy Studious", silence=True)
print("-----Terminando animación")
time.sleep(10)