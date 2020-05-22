import traceback
import lorem

from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler

from telebot import Bot, Filters
from botlib import stdwar, stderr, stdout

with open('vilabot.token') as file:
    TOKEN = file.read()

class VilaBot(Bot):

    START_TEXT = "Aaauuuuuuuuu!"

    def get_answer(self, text: str, **kwargs):
        return text

    @Bot.with_info
    @Bot.command('start')
    def start(self, info):
        stdout[2] << f"> /start from @{info['username']}"
        chat = self.get_chat(info['chat_id'])
        if chat.started:
            return None
        else:
            self.start_chat(info['chat_id'])
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.START_TEXT,
        }
        return info['bot'].send_message(**kwargs)

    @Bot.with_info
    @Bot.lock_start
    @Bot.command('lorem')
    def lorem(self, info):
        stdout[2] << f"> /lorem from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': lorem.paragraph(),
        }
        return info['bot'].send_message(**kwargs)

    @Bot.with_info
    @Bot.lock_start
    @Bot.message(~Filters.command, Filters.text)
    def echo(self, info):
        stdout[2] << f"> Text Message from @{info['username']}:\n{info['text']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.get_answer(info['text']),
        }
        return info['bot'].send_message(**kwargs)

    @Bot.with_info
    @Bot.lock_start
    @Bot.message(~Filters.command, Filters.text, Filters.entity('mention'))
    def mention(self, info):
        stdout[2] << f"> Text Message from @{info['username']}:\n{info['text']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': self.get_answer(info['text']),
            'reply_to_message_id': info['message_id'],
        }
        return info['bot'].send_message(**kwargs)

    @Bot.with_info
    @Bot.lock_start
    @Bot.message(Filters.command)
    def unknown(self, info):
        stdout[2] << f"> Unknown command '{info['text']}' from @{info['username']}"
        kwargs = {
            'chat_id': info['chat_id'],
            'text': f"Comando desconhecido: `{info['text']}`",
            'parse_mode': self.MARKDOWN
        }
        return info['bot'].send_message(**kwargs)

    @Bot.with_info
    @Bot.set_error
    def error(self, info):
        for line in traceback.format_tb(info['error'].__traceback__):
            stderr << line
        stderr << info['error']

if __name__ == '__main__':
    with VilaBot(TOKEN) as bot:
        bot.run()
        bot.clear()