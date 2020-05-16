import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.DEBUG)
from telebot import Bot

with open('vilabot.token') as file:
    TOKEN = file.read()

class VilaBot(Bot):

    START_TEXT = "Aaauuuuuuuuu!"

    @Bot.command('start')
    def start(self, info):
        info['bot'].send_message(chat_id=info['chat_id'], text=self.START_TEXT)

if __name__ == '__main__':
    bot = VilaBot(TOKEN)
    bot.run()


