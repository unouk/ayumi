from dependencies.models import ManagerTTS, ManagerLLM, AyumiLLM, ReaderLLM, ExpressionLLM
from dependencies.queue import QueueChat, QueueExpression
import asyncio


async def main():
    # Iniciando modelos base
    tts = ManagerTTS()
    llm = ManagerLLM()
    # Instanciando modelos de lenguaje
    reader_llm = ReaderLLM(llm)
    ayumi_llm = AyumiLLM(llm, stream_name="Conversando")
    expression_llm = ExpressionLLM(llm)
    # Conectando con redis
    chat = QueueChat('messages')
    chat.dequeue(script="return redis.call('DEL', KEYS[1])")
    
    expression_queue = QueueExpression('expressions')

    while True:
        messages = chat.dequeue()
        # Caso: Existen mensajes en la memoria

        if messages:
            # Procesando mensajes del chat
            if len(messages) > 1:
                message = reader_llm.select(messages)
                tts.process(text=message['message'], speaker="Dionisio Schuyler")
            else:
                message = messages[0]
                if message['author'] == 'Undou':
                    tts.process(text=message['message'], speaker="Viktor Menelaos")
                    message['author'] = 'Jefe'
                else:
                    tts.process(text=message['message'], speaker="Dionisio Schuyler")


            # Procesando por partes la respuesta de Ayumi
            response = ayumi_llm.ask(author=message['author'], answer=message['message'])
            response = response.replace('...', '.').split('.')
            for sentence in response:
                tts.process(text=sentence, speaker="Daisy Studious", device="waveout")

            # Cambiando expresión
            expression = expression_llm.identify(question=message['message'], answer=response)
            if expression != 'neutral':
                expression_queue.enqueue(expression)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())