# Libreries
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import time
# Dependencies
from dependencies.queue import ShortMemoryChat


class Youtube:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")

        self.window = webdriver.Chrome(options=chrome_options)
        self.window.get('https://studio.youtube.com/live_chat?is_popout=1&v=uayb-QKtmeU')

    def read_message(self):
        message = {"author": "", "message": ""}
        messages = self.window.find_elements('css selector', 'yt-live-chat-text-message-renderer')
        if len(messages) > 0:
            author = messages[-1].find_element('css selector', '#author-name').text
            content = messages[-1].find_element('css selector', '#message').text
            message['author'] = author
            message['message'] = content
        return message


if __name__ == '__main__':
    memory = ShortMemoryChat('messages')
    youtube = Youtube()
    time.sleep(60)
    prev_message = {"author": "", "message": ""}
    while True:
        message = youtube.read_message()
        if message != prev_message:
            memory.enqueue(date=time.strftime('%Y-%m-%d %H:%M:%S'),
                           author=message['author'],
                           message=message['message'],
                           timestamp=time.time())
            prev_message = message
        time.sleep(0.5)