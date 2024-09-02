from dependencies.models import ManagerTTS, ManagerLLM, AyumiLLM, ReaderLLM
from dependencies.queue import ShortMemoryChat
from dependencies.animation import VTubeStudio
import time
import random


if __name__ == "__main__":
    # Iniciando modelos base
    tts = ManagerTTS()
    llm = ManagerLLM()
    # Instanciando modelos de lenguaje
    reader_llm = ReaderLLM(llm)
    ayumi_llm = AyumiLLM(llm)
    # Conectando con Redis
    memory = ShortMemoryChat('messages')
    memory.dequeue(script="return redis.call('DEL', KEYS[1])")

    while True:
        messages = memory.dequeue()
        # Caso: Existen mensajes en la memoria
        if messages:
            # Procesando mensajes del chat
            message = reader_llm.select(messages)
            response = ayumi_llm.ask(author=message['author'], answer=message['message'])
            # Leyendo y respondiendo mensajes
            tts.play(text=message['message'], speaker="Dionisio Schuyler", device="waveout")
            tts.play(text=response, speaker="Daisy Studious", sync=True)
            tts.play("", "Daisy Studious", silence=True)
            animation_timer = time.time()
        time.sleep(0.5)
