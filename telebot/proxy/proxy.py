from functools import wraps
from telebot.botlib import stdout

class Proxy:
    """ func(bot: Bot, info: dict) -> bool

        Example:

        @Proxy.proxy('reply')
        def block_politics(bot, info):
            return 'politics' not in info['text']

        @block_politics # this will not be called if 'politics' in message text
        def reply(bot, info):
            kwargs = {
                'chat_id': info['chat_id'],
                'text': 'I like that too.'
            }
            return bot.send_message(**kwargs)
    """

    NULL_FUNC = (lambda *args, **kwargs: None)

    @classmethod
    def proxy(cls, name: str):
        def decor(func: staticmethod):
            return cls(func, name)
        return decor

    @classmethod
    def apply(cls, callback: callable):
        @wraps(callback)
        def new_callback(bot, *args, **kwargs):
            info = bot.get_info(*args)
            if cls.allow(bot, info, callback.proxy):
                return callback(bot, *args, **kwargs)
            else:
                return None
        return new_callback

    @classmethod
    def allow(cls, bot: object, info: dict,  proxy: dict):
        return all(proxy[key](bot, info) for key in proxy)

    def __init__(self, func: callable, name: str):
        """ func(bot, info) -> None
        """
        self.func = func
        self.name = name

    def __invert__(self):
        @wraps(self.func)
        def new_func(bot, info):
            return (not self.func(bot, info))
        return self.__class__(new_func, self.name)

    def __neg__(self):
        @wraps(self.func)
        def new_func(bot, info):
            return True
        return self.__class__(new_func, self.name)

    @property
    def invert(self):
        return ~self

    @property
    def cancel(self):
        return -self

    def __call__(self, callback: object):
        if hasattr(callback, 'proxy'):
            callback.proxy[self.name] = self.func
        else:
            setattr(callback, 'proxy', {self.name: self.func})
        stdout[3] << f">> Apply Proxy '{self.func}' @ {callback}"
        return callback

    ## Common proxies

## lock_start
@Proxy.proxy('start')
def lock_start(bot: object, info: dict):
    chat = bot.get_chat(info['chat_id'])
    return chat.started

## lock_awake
@Proxy.proxy('sleep')
def lock_awake(bot: object, info: dict):
    chat = bot.get_chat(info['chat_id'])
    return chat.awake

## lock_group
@Proxy.proxy('group')
def lock_group(bot: object, info: dict):
    return info['type'] in {'group', 'supergroup'}