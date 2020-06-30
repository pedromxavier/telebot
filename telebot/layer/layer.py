from functools import wraps
from ..botlib import stdout, stderr, stdwar, stream

class Layer:
    """ func(bot: Bot, info: dict) -> bool

        Example:

        @Layer.layer
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

    @classmethod
    def layer(cls, func: staticmethod):
        return cls(func)

    @classmethod
    def apply(cls, callback: callable):
        return cls.stack(callback, callback.layer)

    @classmethod
    def stack(cls, callback: callable, layers: list):
        if not layers:
            return callback
        else:
            new_callback = wraps(callback)(layers[0](callback))
            return cls.stack(new_callback, layers[1:])

    def __init__(self, decor: staticmethod):
        self.decor = decor

    def __call__(self, obj: object):
        stdout[3] << f"> with_info layer added @ {obj}'s stack"
        if hasattr(obj, 'layer'):
            obj.layer.append(self.decor)
        else:
            setattr(obj, 'layer', [self.decor])
        stdout[3] << f">> Apply Layer '{self.decor}'  @ {obj}"
        return obj

## Common layers

## with_info
@Layer.layer
def with_info(callback: callable):
    @wraps(callback)
    def new_callback(self, *args, **kwargs):
        info = self.get_info(*args)
        return callback(self, info, **kwargs)
    return new_callback

## log
@Layer.layer
def log(level: int=None):
    def decor(callback: callable):
        @wraps(callback)
        def new_callback(self, *args, **kwargs):
            stdout[level] << f"> call @ {self}"
            return callback(self, *args, **kwargs)
        return new_callback
    return decor
