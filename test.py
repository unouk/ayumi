import time
from dependencies.queue import ShortMemoryChat
memory = ShortMemoryChat('messages')
memory.enqueue(date='2024-09-01 20:00',
               author='Undou',
               message='Que anime es tu favorito, dame una respuesta larga',
               timestamp=1738472000)

