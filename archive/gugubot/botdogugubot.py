## Standard Library
import traceback
import re
import os
import time
import datetime
import random
from collections import deque

## Third-Party
from telegram import Bot, User, Message, MessageEntity, PhotoSize
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, BaseFilter, InlineQueryHandler

## Local
from telebot.game import GameBot, Game, Player, GameError
from telebot.proxy import Proxy, lock_start, lock_group
from telebot.layer import Layer, with_info, log
from telebot.filters import Mention
from telebot.botlib import start_logging, load, stdwar, stderr, stdout, shuffled

ENDL = '\n'

TOKEN = load('botdogugubot.token')

class PhotoAnswer(object):

    def __init__(self, photo: PhotoSize, player: Player):
        self.photo = photo
        self.player = player

class GuguGame(Game):

    OBJECTS = load('assets/objects.txt').split('\n')

    START_GIFS = os.listdir('assets/start')
    FINISH_GIFS = os.listdir('assets/finish')

    def __init__(self, bot: Bot, chat_id: int):
        Game.__init__(self, bot, chat_id)
    
        self.object: str = None
        self.master: Player = None
        self.photo = None

    @Game.start
    def start(self, info: dict):
        self.master_queue = deque(shuffled(self.players))
        self.object_queue = deque(shuffled(self.OBJECTS))
        self.photo_queue = deque([])

        keyboard_markup = GameBot.keyboard_markup('entrar',
            [('Entrar no Jogo', {'url': f"https://t.me/botdogugubot?start={info['chat_id']}"})]
        )

        kwargs = {
            'chat_id': self.chat_id,
            'animation': open(random.choice(self.START_GIFS), 'rb'),
            'text': f"{info['name']} está organizando a caravana para ir no Domingo Legal! Entra aí que a Kombi já vai partir!",
            'reply_to_message_id': info['message_id'],
            'reply_markup': keyboard_markup,
        }
        return self.bot.send_animation(**kwargs)

    @Game.finish
    def finish(self, info: dict):
        kwargs = {
            'chat_id': self.chat_id,
            'animation': open(random.choice(self.FINISH_GIFS), 'rb'),
            'text': f"{self.winner} venceu o Domingo Legal!"
        }
        self.bot.send_animation(**kwargs)

    def update(self):
        ...

    def next_master(self):
        return self.master_queue.pop()

    def add_photo(self, photo: PhotoAnswer) -> None:
        self.photo_queue.appendleft(photo)

    def ask_photo(self):
        self.photo_answer: PhotoAnswer = self.photo_queue.pop()

        keyboard_markup = GameBot.keyboard_markup('objeto',
            [('Sim', {'data': True}), ('Não', {'data': False})]
        )

        kwargs = {
            'chat_id': self.master.chat_id,
            'photo': self.photo_answer.photo, 
            'caption': 'Tá certo isso Gugu?',
            'reply_markup': keyboard_markup
        }
        self.bot.send_photo(**kwargs)

    def accept_photo(self):
        self.photo_answer.player.score += 1
        self.update()

    def reject_photo(self):
        self.ask_photo()

class GuguBot(GameBot):

    __cast__ = [with_info, log]
    __game__ = GuguGame

    def get_answer(self, text: str, **kwargs):
        return text
    
    @GameBot.command('start', 'Entra em uma partida')
    def start(self, info: dict):
        try:
            game_id = self.queue.pop(info['user_id'])
        except KeyError:
            kwargs = {
                'chat_id': info['chat_id'],
                'text': f"Você deve clicar no botão `Entrar no jogo` em um grupo para jogar.",
                'parse_mode': self.MARKDOWN
            }
            return info['bot'].send_message(**kwargs)

        player = Player(info['user_id'], info['chat_id'], info['full_name'])

        self.games[game_id].add_player(player)
        kwargs = {
            'chat_id': info['chat_id'],
            'text': f"Você está no Domingo Legal da {info['title']}!",
        }
        return info['bot'].send_message(**kwargs)

    @GameBot.command('jogar', 'Cria uma partida')
    def jogar(self, info: dict):
        if info['type'] not in {'group', 'supergroup'}:
            kwargs = {
                'chat_id': info['chat_id'],
                'text': 'Sem a sua caravana, não dá pra vir no Domingo Legal.'
            }
            return info['bot'].send_message(**kwargs)
        elif info['chat_id'] in self.games:
            kwargs = {
                'chat_id': info['chat_id'],
                'text': 'Já tem um jogo rolando nesse grupo!',
                'reply_to_message_id': info['message_id'],
            }
            return info['bot'].send_message(**kwargs)
        else:
            ## Create Game instance
            self.games[info['chat_id']] = self.__game__(info['bot'], info['chat_id'])
            
            ## Start Game
            return self.games[info['chat_id']].start()

    @GameBot.command('iniciar', 'Inicia a partida')
    def iniciar(self, info: dict):
        """
        """
        game = self.get_game(info)
        game.start()

    @GameBot.command('sair', 'Sai de uma partida')
    def sair(self, info: dict):
        """
        """
        ## Verifica se uma pessoa está em um grupo
        if ((info['type'] not in {'group', 'supergroup'})
            or (info['chat_id'] not in self.games)
            or (info['user_id'] not in self.games[info['chat_id']])):
            kwargs = {
                'chat_id': info['chat_id'],
                'text': "Você precisa estar em um jogo num grupo do Domingo Legal para amarelar.",
            }
            return info['bot'].send_message(**kwargs)
        else:
            game = self.get_game(info)
            game.rmv_player(info['user_id'])
            kwargs = {
                'chat_id': info['chat_id'],
                'text': f"{info['full_name']} voltou pra casa mais cedo!"
            }
            return info['bot'].send_message(**kwargs)

    @GameBot.command('jogadores', 'Lista os jogadores')
    def jogadores(self, info: dict):
        if (info['type'] not in {'group', 'supergroup'}):
            kwargs = {
                'chat_id': info['chat_id'],
                'text': f"Você precisa me perguntar isso em um grupo.",
            }
        elif (info['chat_id'] not in self.games):
            kwargs = {
                'chat_id': info['chat_id'],
                'text': f"Hoje não é domingo nesse grupo.",
                'reply_to_message_id': info['message_id'],
            }
        else:
            game = self.get_game(info)
            kwargs = {
                    'chat_id': info['chat_id'],
                    'text': f"Lista de jogadores:{ENDL}{ENDL.join(game.players)}",
                    'reply_to_message_id': info['message_id'],
                }
        return info['bot'].send_message(**kwargs)    

    @GameBot.command('comandos', 'Lista os comandos disponíveis')
    def comandos(self, info: dict):
        kwargs = {
            'chat_id': info['chat_id'],
            'text': "\n".join([f"/{cmd}" for cmd, des in self.commands]),
        }
        return info['bot'].send_message(**kwargs)
        
    @GameBot.command('lista')
    def _lista(self, info):
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.command_list,
        }
        return info['bot'].send_message(**kwargs)

    @GameBot.message(Filters.command)
    def unknown(self, info: dict):
        kwargs = {
            'chat_id': info['chat_id'],
            'text': f"Comando desconhecido: `{info['text']}`",
            'parse_mode': self.MARKDOWN
        }
        return info['bot'].send_message(**kwargs)

    @GameBot.message(Filters.photo, Filters.group)
    def photo(self, info: dict):
        ## Verifica se a pessoa está em um jogo
        if not self.in_game(info):
            return
        else:
            game = self.get_game(info)
            game.add_photo(info['photo'])

    @GameBot.query('entrar')
    def entrar(self, info: dict, data: str):
        self.queue[info['user_id']] = info['chat_id']
        return info['query'].answer()

    @GameBot.query('objeto')
    def objeto(self, info: dict, data: str):
        game = self.get_game(info)
        
        if data == 'True':
            game.accept_photo()
        elif data == 'False':
            game.reject_photo()
        else:
            raise GameError('Received data is neither `True` nor `False`')

        return info['query'].answer()

    @GameBot.get_error
    def error(self, info):
        for line in traceback.format_tb(info['error'].__traceback__):
            stderr << line
        stderr << info['error']

if __name__ == '__main__':
    with GuguBot(TOKEN) as bot:
        bot.run()