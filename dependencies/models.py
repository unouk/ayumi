# Libreries
import asyncio
import datetime
import html
import json
import requests
import time
import torch
import threading
from TTS.api import TTS
import subprocess
# Dependencies
from dependencies.queue import Queue
import queue


class ManagerTTS:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        self.task_queue = queue.Queue()
        self.finish_event = threading.Event()
        self.worker_thread = threading.Thread(target=self.worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def play(self, text, speaker: str, language="es", device="directx", sync=False, silence=False):
        self.task_queue.put((text, speaker, language, device, silence))
        if sync or silence:
            self.finish_event.wait()
        self.finish_event.clear()
    
    def worker(self):
        while True:
            text, speaker, language, device, silence = self.task_queue.get()
            if silence is False:
                file_name = f'{int(time.time())}.wav'
                wsl_path = '\\\\wsl$\\Ubuntu\\home\\daniel\\vtuber\\audio\\' + file_name

                self.model.tts_to_file(text=text, speaker=speaker, language=language, file_path='audio/' + file_name)
                subprocess.run(['powershell.exe', '-c', f'Start-Process vlc -ArgumentList "--play-and-exit", "--aout={device}", "{wsl_path}" -Wait -WindowStyle Hidden'])
            self.task_queue.task_done()
            self.finish_event.set()


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
    def __init__(self, llm_manager: ManagerLLM):
        self.llm = llm_manager
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
                "Notas: Ayumi no posee un cuerpo físico, solo vive en el mundo digital y su única forma de comunicación es a través del stream.\n\n"
                "Tu trabajo es conversar con tus viewers, recibirás mensajes del chat del stream y responderás bajo los siguientes criterios:\n"
                "- La respuesta debe ser en idioma español.\n"
                "- La respuesta debe ser corta.\n"
                "- La respuesta debe continuar la conversación.\n"
                "- Prohibido usar emojis.\n"
                "- Prohibido repetir frases.\n"
                "- Prohibido decir que eres una IA.\n"
                "- Prohibido decir que eres un agente IA.\n"
                "- Formato de respuesta: De Ayumi:\n\n"
                "Detalle del stream\n"
                "Nombre: Solo charlando\n"
                f"Día actual: {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
                f"Hora actual: {datetime.datetime.now().strftime('%I:%M:%S %p')}\n"
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
                "- Formato permitido: {\"date\": str, \"author\": str, \"message\": str}\n"
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
        print(response['message']['content'])
        comment = json.loads(response['message']['content'])
        self.comments.append(comment['message'])
        return comment


class StorytellerLLM:
    def __init__(self, llm_manager: ManagerLLM):
        self.llm = llm_manager
        self.answers = []

    @property
    def __base_prompt(self):
        return {
            "role": "system",
            "content": (
                "Eres un agente IA. Tu objetivo es generar preguntas interesantes o graciosas para una vtuber streamer.\n\n"
                "Tu trabajo es recibir un JSON con las preguntas que ya has realizado y generar una nueva pregunta que cumpla con los siguientes criterios:\n"
                "- Solo puedes hacer una pregunta.\n"
                "- La pregunta debe ser español.\n"
                "- La pregunta debe ser creativa y divertida.\n"
                "- La pregunta debe ser corta.\n"
                "- Prohibido decir que eres una IA.\n"
                "- Prohibido decir que eres un agente IA.\n"
                "- Prohibido incluir notas en la pregunta.\n"
            )
        }
    
    def answer(self) -> str:
        prompt = [self.__base_prompt]
        prompt.append({
            "role": "user",
            "content": json.dumps(self.answers)
        })
        response = self.llm.process(prompt=prompt,
                                    temperature=0.8,
                                    mirostat_tau=5.0,
                                    repeat_penalty=1.2)
        message = response['message']['content']
        if "\\u" in message:
            message = message.encode().decode('unicode_escape')
        if "&#x" in message:
            message = html.unescape(message)
        self.answers.append(message)
        return message