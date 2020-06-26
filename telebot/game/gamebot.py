from ..bot import Bot
from .game import Game

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

class GameBot(Bot):

    __game__ = Game

    def __init__(self, token: str, **options):
        Bot.__init__(self, token, **options)