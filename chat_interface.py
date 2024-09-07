# Libraries
import time
import datetime as dt
# Dependencies
from dependencies.queue import QueueChat

if __name__ == '__main__':
    memory = QueueChat('messages')
    while True:
        message = input('Message: ')
        memory.enqueue(date=dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       author='Undou',
                       message=message,
                       timestamp=time.time())
