from dependencies.models import ManagerTTS, ManagerLLM, AyumiLLM, ReaderLLM, ExpressionLLM, ManagerTTS2
from dependencies.queue import ShortMemoryChat
from dependencies.animation import Animator
import time
import random
import asyncio
import os
import subprocess


async def main():
    # Iniciando modelos base
    tts = ManagerTTS2()
    llm = ManagerLLM()
    # Instanciando modelos de lenguaje
    reader_llm = ReaderLLM(llm)
    ayumi_llm = AyumiLLM(llm, stream_name="Hablemos de anime")
    expression_llm = ExpressionLLM(llm)
    # Conectando con Redis
    memory = ShortMemoryChat('messages')
    memory.dequeue(script="return redis.call('DEL', KEYS[1])")
    # Iniciando VTubeStudio
    animator = Animator(ip="172.28.32.1", port="8001")
    await animator.animate(f"base_{random.randint(1, 5)}")
    animation_duration = 28
    animation_timer = time.time()
    expression_timer = time.time()
    expression_active = False

    while True:
        # Caso: Actualizando animación base
        if time.time() - animation_timer > animation_duration:
            asyncio.create_task(animator.animate(f"base_{random.randint(1, 5)}"))
            animation_duration = random.randint(5, 10)
            animation_timer = time.time()

        # Caso: Desactivando expresión activa
        if time.time() - expression_timer > random.randint(5, 20) and expression_active:
            asyncio.create_task(animator.animate(f"expression_{expression}"))
            expression_timer = time.time()
            expression_active = False

        messages = memory.dequeue()
        # Caso: Existen mensajes en la memoria
        if messages:
            # Caso: Desactivando expresión activa
            if expression_active:
                asyncio.create_task(animator.animate(f"expression_{expression}"))

            # Procesando mensajes del chat
            if len(messages) > 1:
                message = reader_llm.select(messages)
                tts.process(text=message['message'], speaker="Dionisio Schuyler")
            else:
                message = messages[0]
                tts.process(text=message['message'], speaker="Dionisio Schuyler")

            
            # Procesando por partes la respuesta de Ayumi
            response = ayumi_llm.ask(author=message['author'], answer=message['message'])
            response = response.replace('...', '.').split('.')
            for sentence in response:
                tts.process(text=sentence, speaker="Daisy Studious", device="waveout")

            # Cambiando expresión
            expression = expression_llm.identify(question=message['message'], answer=response)
            if expression != 'neutral':
                asyncio.create_task(animator.animate(f"expression_{expression}"))
                expression_active = True
                expression_timer = time.time()
            animation_duration = 0
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())