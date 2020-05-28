import traceback
import lorem
import re
from random import randint

from telegram import Message, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter

from telebot import Bot, Filters
from telebot.proxy import Proxy, lock_start, lock_awake
from telebot.layer import Layer, with_info
from telebot.filters import Mention
from telebot.botlib import log, load, stdwar, stderr, stdout

TOKEN = load('vilabot.token')

class MoonEmoji(BaseFilter):

    MOONS = ['🌝','🌕','🌗','🌘','🌖','🌙','🌛','🌚','🌑','🌓','🌒','🌔','☪','☾','☽']

    def __init__(self):
        self.regex = re.compile('|'.join(self.MOONS), re.MULTILINE)

    def filter(self, message: Message):
        return self.regex.search(message.text) is not None

class VilaBot(Bot):

    __cast__ = [with_info, lock_start, lock_awake]

    def get_answer(self, text: str, **kwargs):
        return text
        
    @lock_start.invert
    @Bot.command('start', 'Inicializa um chat com o Bot')
    def start(self, info):
        stdout[2] << f"> /start from @{info['username']}"
        ## Starts chat
        self.start_chat(info['chat_id'])
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.uivo,
        }
        return info['bot'].send_message(**kwargs)

    @Bot.command('lorem', 'Gera um parágrafo Lorem Ipsum')
    def lorem(self, info):
        stdout[2] << f"> /lorem from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': lorem.paragraph(),
        }
        return info['bot'].send_message(**kwargs)

    @Bot.command('comandos', 'Lista os comandos disponíveis')
    def comandos(self, info):
        stdout[2] << f"> /comandos from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': "\n".join([f"/{cmd}" for cmd, des in self.commands]),
        }
        return info['bot'].send_message(**kwargs)

    @Bot.command('durma', 'Bota o VilaBot para dormir')
    def durma(self, info):
        stdout[2] << f"> /durma from @{info['username']}"
        chat = self.get_chat(info['chat_id'])
        chat.sleep()
        kwargs = {
            'chat_id': info['chat_id'],
            'text': '🌙 ZZZzzzzzzz'
        }
        return info['bot'].send_message(**kwargs)

    @lock_awake.invert
    @Bot.command('acorde', 'Manda o VilaBot acordar')
    def acorde(self, info):
        stdout[2] << f"> /acorde from @{info['username']}"
        chat = self.get_chat(info['chat_id'])
        chat.wakeup()
        kwargs = {
            'chat_id': info['chat_id'],
            'text': '☀️' + self.uivo,
        }
        return info['bot'].send_message(**kwargs)

    @Bot.command('uive', 'Uiva o lobo')
    def uive(self, info):
        stdout[2] << f"> /uive from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.uivo,
        }
        return info['bot'].send_message(**kwargs)

    @Bot.command('lista')
    def _lista(self, info):
        stdout[2] << f"> /lista from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.command_list,
        }
        return info['bot'].send_message(**kwargs)

    @Bot.message(Filters.text & MoonEmoji())
    def moon_emoji(self, info):
        stdout[2] << f"> Text Message with Moon Emoji from @{info['username']}:\n{info['text']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.uivo,
            'reply_to_message_id': info['message_id'],
        }
        return info['bot'].send_message(**kwargs)

    @Bot.message(Mention('ovilabot'))
    def mention(self, info):
        stdout[2] << f"> Text Message from @{info['username']}:\n{info['text']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.get_answer(info['text']),
            'reply_to_message_id': info['message_id'],
        }
        return info['bot'].send_message(**kwargs)

    @Bot.message(~Filters.command, Filters.text, ~Filters.group)
    def echo(self, info):
        stdout[2] << f"> Text Message from @{info['username']}:\n{info['text']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.get_answer(info['text']),
        }
        return info['bot'].send_message(**kwargs)

    @Bot.message(Filters.command)
    def unknown(self, info):
        stdout[2] << f"> Unknown command '{info['text']}' from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': f"Comando desconhecido: `{info['text']}`",
            'parse_mode': self.MARKDOWN
        }
        return info['bot'].send_message(**kwargs)

    @Bot.get_error
    def error(self, info):
        for line in traceback.format_tb(info['error'].__traceback__):
            stderr << line
        stderr << info['error']

    @property
    def uivo(self):
        return  f"{randint(1,3)*'A'}{randint(4,6)*'a'}{randint(5,8)*'u'}!"

if __name__ == '__main__':
    with VilaBot(TOKEN) as bot:
        bot.run()