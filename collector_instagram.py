# Libreries
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import time
# Dependencies
from dependencies.queue import ShortMemoryChat


class Instagram:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")

        self.window = webdriver.Chrome(options=chrome_options)
        self.window.get('https://www.instagram.com/')

    def login(self, username, password):
        WebDriverWait(self.window, 10).until(lambda d: d.find_element('css selector', '[name=username]'))
        self.window.find_element('css selector', '[name=username]').send_keys(username)
        self.window.find_element('css selector', '[name=password]').send_keys(password)
        self.window.find_element('css selector', '[name=password]').send_keys(Keys.RETURN)
        time.sleep(10)

    def live(self):
        create_button = self.window.find_elements('css selector', 'div.x1iyjqo2.xh8yej3 > div')[6]
        create_button.find_elements('css selector', 'a')[0].click()
        time.sleep(1)
        create_button.find_elements('css selector', 'a')[2].click()
        time.sleep(10)

    def read_message(self):
        message = {"author": "", "message": ""}
        messages = self.window.find_elements('css selector', 'section.x11njtxf div.x17y8kql')
        if len(messages) > 0:
            content = messages[-1].find_elements('css selector', 'span')
            if len(content) == 4:
                message['author'] = content[2].text
                message['message'] = content[3].text
            elif len(content) == 3:
                if 'joined' in content[2].text:
                    author = content[2].text.split('joined')[0].strip()
                    message['author'] = author
                    message['message'] = f"{author} se ha unido a la transmisión"
        return message


if __name__ == '__main__':
    memory = ShortMemoryChat('messages')
    instagram = Instagram()
    instagram.login('ayumi@ewaifu.com', '9053326aA*')
    instagram.live()
    prev_message = {"author": "", "message": ""}
    while True:
        message = instagram.read_message()
        if message != prev_message:
            memory.enqueue(date=time.strftime('%Y-%m-%d %H:%M:%S'),
                           author=message['author'],
                           message=message['message'],
                           timestamp=time.time())
            prev_message = message
        time.sleep(0.5)