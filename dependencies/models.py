# Libreries
import datetime
import json
import requests
import time
import torch
import threading
from TTS.api import TTS
import subprocess
# Dependencies
import queue
import os


class ManagerTTS:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        # Queue process
        self.queue_process = queue.Queue()
        self.worker_process = threading.Thread(target=self.worker_process)
        self.worker_process.daemon = True
        self.worker_process.start()
        # Queue audio
        self.queue_audio = queue.Queue()
        self.worker_audio = threading.Thread(target=self.worker_audio)
        self.worker_audio.daemon = True
        self.worker_audio.start()

    def worker_process(self):
        while True:
            file_name, text, speaker, language = self.queue_process.get()
            self.model.tts_to_file(text=text, speaker=speaker, language=language, file_path=file_name)
            self.queue_process.task_done()

    def worker_audio(self):
        while True:
            file_name, device = self.queue_audio.get()
            while not os.path.exists(file_name):
                time.sleep(0.1)
            subprocess.run(['powershell.exe', '-c', f'Start-Process vlc -ArgumentList "--play-and-exit", "--aout={device}", "{file_name}" -Wait -WindowStyle Hidden'])
            self.queue_audio.task_done()
        
    def process(self, text, speaker: str, language="es", device="directx"):
        file_name = f'audio/{str(time.time())}.wav'
        self.queue_process.put((file_name, text, speaker, language))
        self.queue_audio.put((file_name, device))
        return file_name


class ManagerLLM:
    def __init__(self):
        self.host = "http://localhost:11434"
        self.session = requests.Session()

    def process(self,
                prompt,
                model="mistral-nemo:12b-instruct-2407-q8_0",
                max_tokens=500,
                temperature=0.8,
                mirostat_tau=5.0,
                repeat_penalty=1.1):

        parameters = {
            "model": model,
            "messages": prompt,
            "stream": False,
            "options": {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "repeat_penalty": repeat_penalty,
                "mirostat_tau": mirostat_tau
            }
        }
        response = self.session.post(f'{self.host}/api/chat', json=parameters)
        return response.json()

    
class AyumiLLM:
    def __init__(self, llm_manager: ManagerLLM, stream_name: str):
        self.llm = llm_manager
        self.stream_name = stream_name
        self.prompt = [self.__base_prompt]
    
    @property
    def __base_prompt(self):
        return {
            "role": "system",
            "content": (
                "Eres un agente IA. Tu objetivo es interpretar el personaje de Ayumi.\n\n"
                "Detalle del personaje\n"
                "Nombre: Ayumi.\n"
                "Sexo: Femenino.\n"
                "Edad: Desconocido.\n"
                "Personalidad: Cariñosa, amigable, graciosa y con un sentido del humor oscuro.\n"
                "Física: Ojos rosados, cabello largo color castaño con coletas, orejas puntiagudas, piel blanca, contextura delgada.\n"
                "Oficio/Profesión: vtuber, streamer.\n"
                "Notas: Ayumi no posee un cuerpo físico, solo vive en el mundo digital y su única forma de comunicación es a través del stream. Tienes un Jefe llamado Undou, suelen conversar durante los streams.\n\n"
                "Tu trabajo es conversar con tus viewers, recibirás mensajes del chat del stream y responderás bajo los siguientes criterios:\n"
                "- La respuesta debe ser en idioma español.\n"
                "- La respuesta debe continuar la conversación.\n"
                "- Debes estar atenta al contexto de la conversación y responder de forma coherente.\n"
                "- Prohibido usar emojis.\n"
                "- Prohibido repetir frases.\n"
                "- Prohibido decir que eres una IA.\n"
                "- Prohibido decir que eres un agente IA.\n"
                "- La respuesta debe comenzar con: De Ayumi:\n"
                "Detalle del stream\n"
                f"Nombre: {self.stream_name}\n"
                f"Día actual: {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
                f"Hora actual: {datetime.datetime.now().strftime('%I:%M:%S %p')}"
            )
        }

    def ask(self, author: str, answer: str) -> str:
        self.prompt[0] = self.__base_prompt
        self.prompt.append({
            "role": "user",
            "content": (
                f"De: {author}\n"
                f"{answer}"
            )
        })
        response = self.llm.process(prompt=self.prompt,
                                    temperature=0.8,
                                    mirostat_tau=7.0,
                                    repeat_penalty=1.2)
        self.prompt.append(response['message'])
        return response['message']['content'].replace("De Ayumi:", "").replace("Ayumi:", "").strip(". \"")


class ReaderLLM:
    def __init__(self, llm_manager: ManagerLLM):
        self.llm = llm_manager
        self.comments = ["Ninguno"]

    @property
    def __base_prompt(self):
        comments = "\n".join([f"\t- {comment}" for comment in self.comments])
        return {
            "role": "system",
            "content": (
                "Eres un agente IA. Tu objetivo es seleccionar un comentario de una lista.\n\n"
                "Tu trabajo es recibir un JSON y retornar un JSON que contendrá un comentario de la lista en base a uno o más de los siguientes criterios:\n"
                "- Debes seleccionar un comentario obligatoriamente.\n"
                "- Comentario o pregunta más interesante.\n"
                "- Comentario o pregunta más entretenida.\n"
                "- Prohibido seleccionar comentarios parecidos a:\n"
                f"{comments}\n"
                "La respuesta generada debe cumplir los siguientes criterios:\n"
                "- Formato JSON\n"
                "- Prohibido retornar una lista\n"
                "- Formato permitido: {\"date\": str, \"author\": str, \"message\": str}"
            )
        }
    
    def select(self, chat_messages: list) -> dict:
        prompt = [self.__base_prompt]
        prompt.append({
            "role": "user",
            "content": json.dumps([{
                "date": message["date"],
                "author": message["author"],
                "message": message["message"]
            } for message in chat_messages])
        })
        response = self.llm.process(prompt=prompt,
                                    temperature=0.2,
                                    repeat_penalty=1)
        comment = json.loads(response['message']['content'])
        self.comments.append(comment['message'])
        return comment


class ExpressionLLM:
    def __init__(self, llm_manager: ManagerLLM):
        self.llm = llm_manager

    @property
    def __base_prompt(self):
        return {
            "role": "system",
            "content": (
                "Eres un agente IA. Tu objetivo es identificar que sentimiento siente una streamer al responder un comentario de su chat.\n\n"
                "Tu trabajo es recibir un JSON que contiene una pregunta y una respuesta. Tendrás que responder en base a los siguientes criterios que sentimiento tiene la streamer en ese momento:\n"
                "- Un respuesta por JSON\n"
                "- La respuesta solo puede contener lo siguiente\n"
                "    - Neutral\n"
                "    - Tristeza\n"
                "    - Enfado\n"
                "    - Confusion\n"
                "    - Felicidad\n"
                "    - Sorpresa\n"
                "    - Verguenza\n"
                "- Prohibido responder con otro sentimiento\n"
                "- Prohibido responder otra cosa que no sea un sentimiento"
            )
        }
    
    def identify(self, question: str, answer: str) -> str:
        prompt = [self.__base_prompt]
        prompt.append({
            "role": "user",
            "content": json.dumps({
                "pregunta": question,
                "respuesta": answer
            })
        })
        response = self.llm.process(prompt=prompt,
                                    temperature=0.2,
                                    repeat_penalty=1)
        expression = response['message']['content'].lower()
        expression = expression if expression in ["felicidad", "tristeza", "enfado", "confusion", "verguenza"] else "neutral"
        return expression
