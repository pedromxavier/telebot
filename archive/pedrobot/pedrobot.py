from telebot import Bot, Filters
from telebot.botlib import load, stream, stderr, stdout, stdwar

class PedroBot(Bot):

    @Bot.with_info
    @Bot.command('start')
    def start(self, info):
        return None