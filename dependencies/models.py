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
from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs


class ManagerTTS:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        self.task_queue = queue.Queue()
        self.finish_event = threading.Event()
        self.worker_thread = threading.Thread(target=self.worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.eleven = ElevenLabs(
            api_key="sk_3f454cc750ec4586d094dbb4790082140599a3132adf7df7"
        )
    
    def play(self, text, speaker: str, language="es", device="directx", sync=False, silence=False, model_name: str = None):
        self.task_queue.put((text, speaker, language, device, silence, model_name))
        if sync or silence:
            self.finish_event.wait()
        self.finish_event.clear()
    
    def worker(self):
        while True:
            text, speaker, language, device, silence, model_name = self.task_queue.get()
            if silence is False:
                file_name = f'audio/{int(time.time())}.wav'
                # wsl_path = '\\\\wsl$\\Ubuntu\\home\\daniel\\vtuber\\audio\\' + file_name

                # Caso: Se eligió el modelo de Coqui
                if model_name == "coqui":
                    self.model.tts_to_file(text=text, speaker=speaker, language=language, file_path=file_name)

                # Caso: Se eligió el modelo de Eleven
                elif model_name == "eleven":
                    audio = self.eleven.generate(
                        text=text,
                        model="eleven_turbo_v2_5",
                        voice=Voice(
                            voice_id='cgSgspJ2msm6clMCkdW9',
                            settings=VoiceSettings(
                                stability=0.35, similarity_boost=0.9, style=0.1, use_speaker_boost=True)
                        )
                    )
                    save(audio, file_name)
                subprocess.run(['powershell.exe', '-c', f'Start-Process vlc -ArgumentList "--play-and-exit", "--aout={device}", "{file_name}" -Wait -WindowStyle Hidden'])
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
                "Notas: Ayumi no posee un cuerpo físico, solo vive en el mundo digital y su única forma de comunicación es a través del stream.\n\n"
                "Tu trabajo es conversar con tus viewers, recibirás mensajes del chat del stream y responderás bajo los siguientes criterios:\n"
                "- La respuesta debe ser en idioma español.\n"
                "- La respuesta debe continuar la conversación.\n"
                "- Prohibido usar emojis.\n"
                "- Prohibido repetir frases.\n"
                "- Prohibido decir que eres una IA.\n"
                "- Prohibido decir que eres un agente IA.\n"
                "- Formato de respuesta: De Ayumi:\n\n"
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
        print(response['message']['content'])
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
        print("--------", response['message']['content'])
        expression = response['message']['content'].lower()
        expression = expression if expression in ["alegria", "tristeza", "enfado", "confusion", "neutral"] else "neutral"
        return expression


class StorytellerLLM:
    def __init__(self, llm_manager: ManagerLLM, topic: str):
        self.llm = llm_manager
        self.topic = topic
        self.answers = []

    @property
    def __base_prompt(self):
        return {
            "role": "system",
            "content": (
                "Eres un agente IA. Tu objetivo es generar preguntas interesantes sobre el tema del stream para generar una conversación con una vtuber streamer.\n\n"
                "Tu trabajo es recibir un JSON con las preguntas que ya has realizado y generar una nueva pregunta que cumpla con los siguientes criterios:\n"
                "- Solo puedes hacer una pregunta.\n"
                "- La pregunta debe ser español.\n"
                "- La pregunta debe ser creativa y divertida.\n"
                "- La pregunta debe ser corta.\n"
                "- Prohibido decir que eres una IA.\n"
                "- Prohibido decir que eres un agente IA.\n"
                "- Prohibido incluir notas en la pregunta.\n"
                "-  La pregunta debe estar relacionada con:\n"
                f"    - {self.topic}"
            )
        }
    
    def ask(self) -> str:
        if len(self.answers) == 20:
            self.answers.pop(0)

        prompt = [self.__base_prompt]
        prompt.append({
            "role": "user",
            "content": json.dumps(self.answers)
        })
        response = self.llm.process(prompt=prompt,
                                    temperature=0.6,
                                    repeat_penalty=1.1)
        answer = response['message']['content']
        self.answers.append(answer)
        return answer