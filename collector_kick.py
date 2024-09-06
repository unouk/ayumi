from multiprocessing import Process, Queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from dependencies.queue import ShortMemoryChat


class Kick:
    def __init__(self, url, queue):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")

        self.window = webdriver.Chrome(options=chrome_options)
        self.window.get(url)
        self.queue = queue

    def read_message(self):
        prev_message = {"author": "", "message": ""}
        while True:
            message = {"author": "", "message": ""}
            messages = self.window.find_elements('css selector', '#chatroom .chat-entry')
            if len(messages) > 0:
                message['author'] = messages[-1].find_element('css selector', '.chat-entry-username').text
                message['message'] = messages[-1].find_element('css selector', '.chat-entry-content').text
                if message != prev_message:
                    self.queue.put({
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'author': message['author'],
                        'message': message['message'],
                        'timestamp': time.time()
                    })
                    prev_message = message
            time.sleep(1)

def process_messages(queue, memory):
    while True:
        if not queue.empty():
            message = queue.get()
            memory.enqueue(
                date=message['date'],
                author=message['author'],
                message=message['message'],
                timestamp=message['timestamp']
            )

# Inicia la cola de mensajes
queue = Queue()

# Crea una instancia de ShortMemoryChat
memory = ShortMemoryChat('messages')

# Crea y lanza el proceso para leer mensajes
kick = Kick('https://kick.com/ayumi-ewaifu', queue)
reader_process = Process(target=kick.read_message)
reader_process.start()

# Procesa los mensajes desde la cola en el proceso principal o en otro subproceso
process_messages(queue, memory)

# Para detener el subproceso correctamente en tu aplicación real, asegúrate de manejar la finalización
