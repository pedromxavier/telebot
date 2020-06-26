import traceback
import re
import random

from telegram import Message, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter, InlineQueryHandler

from telebot import Filters
from telebot.game import GameBot, Game
from telebot.proxy import Proxy, lock_start
from telebot.layer import Layer, with_info
from telebot.filters import Mention
from telebot.botlib import log, load, stdwar, stderr, stdout, shuffled

from collections import deque

TOKEN = load('botdogugubot.token')

class GuguGame(Game):

    def __init__(self):
        Game.__init__(self)
        self.__guguqueue = deque(shuffled(self.__players))
        self.__gugu = None

    def next_gugu(self):
        return self.__guguqueue.pop()

class GuguBot(GameBot):

    __cast__ = [with_info, lock_start]
    __game__ = GuguGame

    OBJECTS = load('objects.txt').split('\n')

    def get_answer(self, text: str, **kwargs):
        return text
        
    @lock_start.invert
    @GameBot.command('start', 'Inicializa um chat com o Bot')
    def start(self, info):
        stdout[2] << f"> /start from @{info['username']}"
        ## Starts chat
        chat = self.get_chat(info['chat_id'])
        chat.start()
        kwargs = {
            'chat_id': info['chat_id'],
            'text': 'Você está no Domingo Legal!',
        }
        return info['bot'].send_message(**kwargs)

    ## Jogo

    @GameBot.command('jogar', 'Cria uma partida')
    def jogar(self, info: dict):
        stdout[2] << f"> /startgame from @{info['username']} in {info['group']}"
        self.game[info['group_id']]





    @GameBot.command('entrar', 'Entra em uma partida')
    def entrar(self, info: dict):
        user = info['user_id']
        self.game.user_join(user)

    @GameBot.command('sair', 'Sai de uma partida')
    def sair(self, info: dict):
        ... 

    @GameBot.command('jogadores', 'Lista os jogadores')
    def jogadores(self, info: dict):
        ...

    @GameBot.command('comandos', 'Lista os comandos disponíveis')
    def comandos(self, info: dict):
        stdout[2] << f"> /comandos from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': "\n".join([f"/{cmd}" for cmd, des in self.commands]),
        }
        return info['bot'].send_message(**kwargs)
        
    @GameBot.command('lista')
    def _lista(self, info):
        stdout[2] << f"> /lista from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.command_list,
        }
        return info['bot'].send_message(**kwargs)

    @GameBot.message(Filters.command)
    def unknown(self, info: dict):
        stdout[2] << f"> Unknown command '{info['text']}' from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': f"Comando desconhecido: `{info['text']}`",
            'parse_mode': self.MARKDOWN
        }
        return info['bot'].send_message(**kwargs)

    @GameBot.get_error
    def error(self, info):
        for line in traceback.format_tb(info['error'].__traceback__):
            stderr << line
        stderr << info['error']

if __name__ == '__main__':
    with GuguBot(TOKEN) as bot:
        bot.run()