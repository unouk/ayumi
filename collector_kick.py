from multiprocessing import Process, Queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from dependencies.queue import QueueChat


class Kick:
    def __init__(self, url, queue):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")

        self.window = webdriver.Chrome(options=chrome_options)
        self.window.get(url)
        self.queue = queue

    def read_message(self):
        prev_message = {"author": "", "message": ""}
        chat = self.window.find_element('css selector', '#chatroom')
        while True:
            message = {"author": "", "message": ""}
            messages = chat.find_elements('css selector', '.chat-entry')
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
                    print(message)
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

if __name__ == '__main__':
    # Inicia la cola de mensajes
    queue = Queue()

    # Crea una instancia de ShortMemoryChat
    memory = QueueChat('messages')

    # Crea y lanza el proceso para leer mensajes
    kick = Kick('https://kick.com/ayumi-ewaifu', queue)
    time.sleep(3)
    reader_process = Process(target=kick.read_message)
    reader_process.start()

    # Procesa los mensajes desde la cola en el proceso principal o en otro subproceso
    process_messages(queue, memory)

