import html
import datetime
import time
from dependencies.queue import ShortMemoryChat
from dependencies.models import ManagerLLM, StorytellerLLM


memory = ShortMemoryChat('messages')
manager_llm = ManagerLLM()
storyteller_llm = StorytellerLLM(manager_llm, topic="El mundo del anime")

while True:
    messages = memory.dequeue(script="return redis.call('LRANGE', KEYS[1], 0, -1)")
    if len(messages) == 0:
        story = storyteller_llm.ask()
        if '&#' in story:
            story = html.unescape(story)
        if '\\u' in story:
            story = story.encode('utf-8').decode('unicode-escape')
        memory.enqueue(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       author='Manager',
                       message=story,
                       timestamp=int(time.time()))
    time.sleep(60)