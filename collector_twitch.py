from twitchio.channel import Channel
from dependencies.queue import ShortMemoryChat
from twitchio.ext import commands
import os


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=os.environ['TWITCH_OAUTH_TOKEN'], prefix='?', initial_channels=['ayumi_ewaifu'])
        self.memory = ShortMemoryChat('messages')

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return
        
        self.memory.enqueue(date=message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            author=message.author.name, 
                            message=message.content,
                            timestamp=message.timestamp.timestamp())

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

if __name__ == '__main__':
    bot = Bot()
    bot.run()