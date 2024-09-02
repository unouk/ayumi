import json
import redis


class Queue:
    def __init__(self, name: str,):
        self.name = name
        try:
            self.r = redis.Redis(host='localhost', 
                                 port=6379, 
                                 decode_responses=True)
        except Exception as e:
            raise Exception('Queue :: __init__ :: Error al conectar con Redis: ', e)

    def enqueue(self, item: str) -> bool:
        try:
            self.r.rpush(self.name, item)
            return True
        except Exception as e:
            raise Exception('Queue :: enqueue :: Error al encolar: ', e)

    def dequeue(self, script: str) -> list:
        try:
            return self.r.eval(script, 1, self.name)
        except Exception as e:
            raise Exception('Queue :: dequeue :: Error al desencolar: ', e)


class ShortMemoryChat(Queue):
    def __init__(self, name: str,):
        super().__init__(name)

    def enqueue(self, date: str, author: str, message: str, timestamp: str):
        return super().enqueue(json.dumps({
            'date': date,
            'author': author,
            'message': message,
            'timestamp': timestamp
        }))

    def dequeue(self, script="""
        local messages = redis.call('LRANGE', KEYS[1], 0, -1)
        redis.call('DEL', KEYS[1])
        return messages
        """):
        messages = super().dequeue(script)
        if isinstance(messages, list):
            messages = [json.loads(message) for message in messages]
            return sorted(messages, key=lambda x: x['timestamp'])
        else:
            return []
