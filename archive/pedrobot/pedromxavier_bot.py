## Extras
from minerva import minerva

## Telegram
from telebot import Bot, Filters
from telebot.proxy import Proxy, lock_start
from telebot.layer import Layer, with_info
from telebot.botlib import load, stream, stderr, stdout, stdwar

TOKEN = load('pedromxavier_bot.token')

@Proxy.proxy('pedro')
def pedro(bot: Bot, info: dict):
    return (info['username'] == 'pedromxavier')

class PedroBot(Bot):

    __cast__ = [with_info, lock_start, pedro]

    @lock_start.invert
    @Bot.command('start', 'Inicializa o bot')
    def start(self, info):
        chat = self.get_chat(info['chat_id'])
        chat.start()
        kwargs = {
            'chat_id': info['chat_id'],
            'text': 'Oi Pedro!'
        }
        return info['bot'].send_message(**kwargs)

    @Bot.command('minerva', 'Renova os empréstimos de livro da biblioteca da UFRJ', pass_args=True)
    def minerva(self, info, **kwargs):
        try:
            if len(info['args']) != 2:
                text = 'O comando /minerva precisa de 2 parâmetros (user, pswd)'
            else:
                user, pswd = info['args']
                info['bot'].delete_message(info['chat_id'], info['message_id'])
                minerva.renew(user, pswd)
                text = 'Renovado com sucesso.'
        except:
            text = 'Falha ao renovar.'
        kwargs = {
            'chat_id': info['chat_id'],
            'text': text
        }
        info['bot'].send_message(**kwargs)

if __name__ == '__main__':
    PedroBot(TOKEN).main()