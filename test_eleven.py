from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
import time
import subprocess


client = ElevenLabs(
  api_key="sk_3f454cc750ec4586d094dbb4790082140599a3132adf7df7"
)

audio = client.generate(
    text="Hola, como estás? este es un texto muy largo de prueba",
    model="eleven_multilingual_v2",
    voice=Voice(
        voice_id='cgSgspJ2msm6clMCkdW9',
        settings=VoiceSettings(stability=0.35, similarity_boost=0.9, style=0.1, use_speaker_boost=True)
    )
)

file_name = f'audio/{int(time.time())}.mp3'
save(audio, file_name)
subprocess.run(['powershell.exe', '-c', f'Start-Process vlc -ArgumentList "--play-and-exit", "--aout=waveout", "{file_name}" -Wait -WindowStyle Hidden'])
