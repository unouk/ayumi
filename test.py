import time
from dependencies.queue import ShortMemoryChat
memory = ShortMemoryChat('messages')
memory.enqueue(date='2024-09-01 20:00',
               author='Undou',
               message='¿Cual es tu personaje de anime favorito y porqué?',
               timestamp=1738472000)