import time
from dependencies.queue import ShortMemoryChat
memory = ShortMemoryChat('messages')
while True:
    memory.enqueue(date='2024-09-01 20:00',
                author='Daniel',
                message='Hola, como estás?',
                timestamp=1738472000)
    time.sleep(15)
