# Libreries
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import time
# Dependencies
from dependencies.queue import ShortMemoryChat

class Kick:
    def __init__(self, url):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")

        self.window = webdriver.Chrome(options=chrome_options)
        self.window.get(url)

    def read_message(self):
        message = {"author": "", "message": ""}
        messages = self.window.find_elements('css selector', '#chatroom .chat-entry')
        if len(messages) > 0:
            message['author'] = messages[-1].find_element('css selector', '.chat-entry-username').text
            message['message'] = messages[-1].find_element('css selector', '.chat-entry-content').text
        return message


if __name__ == '__main__':
    memory = ShortMemoryChat('messages')
    kick = Kick('https://kick.com/ayumi-ewaifu')
    time.sleep(10)
    prev_message = {"author": "", "message": ""}
    while True:
        message = kick.read_message()
        if message != prev_message:
            print(message)
            memory.enqueue(date=time.strftime('%Y-%m-%d %H:%M:%S'),
                           author=message['author'],
                           message=message['message'],
                           timestamp=time.time())
            prev_message = message
        time.sleep(2)
