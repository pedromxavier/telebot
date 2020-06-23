import traceback
import re
from random import randint

from telegram import Message, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter

from telebot import Bot, Filters
from telebot.proxy import Proxy, lock_start
from telebot.layer import Layer, with_info
from telebot.filters import Mention
from telebot.botlib import log, load, stdwar, stderr, stdout

TOKEN = load('botdogugubot.token')

class GuguBot(Bot):

    __cast__ = [with_info, lock_start]

    def get_answer(self, text: str, **kwargs):
        return text
        
    @lock_start.invert
    @Bot.command('start', 'Inicializa um chat com o Bot')
    def start(self, info):
        stdout[2] << f"> /start from @{info['username']}"
        ## Starts chat
        chat = self.get_chat(info['chat_id'])
        chat.start()
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.uivo,
        }
        return info['bot'].send_message(**kwargs)

    ## Jogo

    @Bot.command('startgame', 'Cria uma partida')
    def startgame(self, info):
        stdout[2] << f"> /startgame from @{info['username']} in {info['group']}"
        ...

    @Bot.command('join', 'Entra em uma partida')
    def join(self, info):
        ...

    @Bot.command('flee', 'Sai de uma partida')
    def flee(self, info):
        ... 

    @Bot.command('comandos', 'Lista os comandos disponíveis')
    def comandos(self, info):
        stdout[2] << f"> /comandos from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': "\n".join([f"/{cmd}" for cmd, des in self.commands]),
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

if __name__ == '__main__':
    with VilaBot(TOKEN) as bot:
        bot.run()