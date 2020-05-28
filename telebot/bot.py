## Standard Library
from functools import wraps, reduce
import re

## Third-Party
from telegram import ParseMode
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler

## Local
from .proxy import Proxy
from .layer import Layer
from .botlib import stream, stdwar, stderr, stdout
from .data import Data

class MetaBot(type):

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        attrs = cls.cast(attrs)
        attrs = cls.add_proxies(attrs)
        attrs = cls.add_layers(attrs)
        attrs = cls.get_handlers(attrs)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def cast(cls, attrs: dict):
        if 'proxy' in attrs or 'layer' in attrs:
            raise SyntaxError('Bot class definition may not contain `proxy` or `layer` attributes / methods.')

        if '__cast__' in attrs:
            proxies = []
            layers = []
            for caster in attrs['__cast__']:
                if type(caster) is Proxy:
                    proxies.append(caster)
                elif type(caster) is Layer:
                    layers.append(caster)
                else:
                    raise TypeError('Object in __cast__ is neither Layer nor Proxy')
            attrs['proxy'] = {proxy.name: proxy.func for proxy in proxies}
            attrs['layer'] = [layer.decor for layer in layers]
        return attrs

    @classmethod
    def add_proxies(cls, attrs: dict):
        has_proxy, bot_proxy = (True, attrs['proxy']) if ('proxy' in attrs) else (False, None)
        if has_proxy: stdout[3] << f">> Broadcast Proxies to handlers @{cls}"
        for name in attrs:
            attr = attrs[name]
            ## Add eventual proxies
            if has_proxy and hasattr(attr, 'handler'):
                if hasattr(attr, 'proxy'):
                    attr.proxy = {**bot_proxy, **attr.proxy}
                else:
                    setattr(attr, 'proxy', bot_proxy.copy())
                stdout[3] << f">> Add Proxies from {cls} to {attr}."
            ## Apply proxy to function stack
            if hasattr(attr, 'proxy'):
                attr = Proxy.apply(attr)
            attrs[name] = attr
        return attrs

    @classmethod
    def add_layers(cls, attrs:dict):
        has_layer, bot_layer = (True, attrs['layer']) if ('layer' in attrs) else (False, None)
        if has_layer: stdout[3] << f">> Broadcast Layers to handlers @{cls}"
        for name in attrs:
            attr = attrs[name]
            ## Add eventual proxies
            if has_layer and hasattr(attr, 'handler'):
                if hasattr(attr, 'layer'):
                    attr.layer = (bot_layer + attr.layer)
                else:
                    setattr(attr, 'layer', bot_layer.copy())
                stdout[3] << f">> Add Layers from {cls} to {attr}."
            ## Apply layer to function stack
            if hasattr(attr, 'layer'):
                attr = Layer.apply(attr)
            attrs[name] = attr
        return attrs

    @classmethod
    def get_handlers(cls, attrs: dict):
        commands = []
        command_handlers = []
        message_handlers = []
        error_handler = None
        
        for name in attrs:
            attr = attrs[name]
            if hasattr(attr, 'command_handler'):
                ## Adds the command name, the handler function and eventual key-word wargs
                command_handlers.append((attr.name, attr, attr.kw))
                ## Controls bot command listing
                ## Commands handled by functions which name is started with '_' are ignored.
                if not name.startswith('_'): commands.append((attr.name, attr.description))
            if hasattr(attr, 'message_handler'):
                ## Adds filters, the handler function and eventual key-word wargs
                message_handlers.append((attr.filters, attr, attr.kw))
            if hasattr(attr, 'error_handler'):
                ## Adds the latest defined error handler
                error_handler = attr

        attrs['commands'] = commands
        attrs['command_handlers'] = command_handlers
        attrs['message_handlers'] = message_handlers
        attrs['error_handler'] = error_handler
        return attrs

class Bot(metaclass=MetaBot):

    ## Constants
    MARKDOWN = ParseMode.MARKDOWN_V2

    START_TEXT = 'Hello, human.'

    commands = []
    command_handlers = []
    message_handlers = []
    error_handlers = []

    __data__ = Data()

    def __init__(self, token=None, **options):
        self.token = token

        ## Setup Updater
        self.updater = Updater(token=self.token, use_context=True)
        stdout[1] << "> Updater setup"

        ## Retrieve Dispatcher
        self.dispatcher = self.updater.dispatcher

        ## Add Handlers
        self.add_handlers()
        stdout[1] << "> Handlers added"

    def load(self):
        try:
            self.__data__.load(self.username)
            stdout[1] << "> Data Loaded"
        except FileNotFoundError:
            stderr[1] << "> Failed to load bot data. Creating new."

    def save(self):
        self.__data__.save(self.username)

    def clear(self):
        self.__data__.clear()

    def stop(self):
        return self.updater.stop()

    def main(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug')

        self.run()

    def run(self, idle=True):
        try:
            self.updater.start_polling()
            if idle:
                stdout[0] << "> Started Polling, going idle."
                self.updater.idle()
            else:
                stdout[0] << "> Started Polling."
        except KeyboardInterrupt:
            stderr[1] << "Keyboard Interrupt"
            return
        finally:
            if idle:
                if self.updater.running:
                    self.updater.stop()
                stdout[0] << "> Stopped"
            else:
                stdout[0] << "> remember calling 'bot.stop()' aftewards."

    ## Context Management
    def __enter__(self, *args, **kwargs):
        self.load()
        return self

    def __exit__(self, *args, **kwargs):
        self.save()

    ## Event Handlers
    def add_handlers(self):
        self.add_command_handlers()
        self.add_message_handlers()
        self.add_error_handler()

    def add_command_handlers(self):
        for command_name, callback, kwargs in self.command_handlers:
            ## Create Handler Object
            handler = CommandHandler(command_name, self.static(callback))

            ## Add Handler to Dispatcher
            self.dispatcher.add_handler(handler, **kwargs)

            stdout[3] << f"> Add Command Handler: /{command_name} @{callback}"

    def add_message_handlers(self):
        for filters, callback, kwargs in self.message_handlers:
            ## AND filters together
            filters = reduce(lambda x, y: x & y, filters)

            ## Create Handler Object
            handler = MessageHandler(filters, self.static(callback), **kwargs)

            ## Add Handler to Dispatcher
            self.dispatcher.add_handler(handler)

            stdout[3] << f"> Add Message Handler: [{filters}] @{callback}"

    def add_error_handler(self):
        for callback in self.error_handlers:
            self.dispatcher.add_error_handler(self.static(callback))
            stdout[3] << f"> Add Error Handler: @{callback}"
            break

    def static(self, callback):
        return (lambda update, context: callback(self, update, context))

    def get_info(self, *args):
        return args[0] if (len(args) == 1) else self._get_info(args[0], args[1])

    def _get_info(self, update, context) -> dict:
        """ get_info(update, context) -> dict
            This function is intended to gather the most relevant information
            from these two objects into a single dictionary.
        """
        return  {
            'error': context.error,
            'chat': update.effective_chat,
            'chat_id': update.effective_chat.id,
            'message': update.message,
            'message_id' : update.message.message_id,
            'text': update.message.text,
            'username': update.effective_user.username,
            'bot': context.bot,
        }    

    def get_answer(self, text: str):
        """
        """
        ## By default, echoes back to the user.
        return f"What do you mean by '{text}'?"

    def get_chat(self, chat_id: int):
        """
        """
        return self.__data__.get_chat(chat_id)
    
    def start_chat(self, chat_id: int):
        """
        """
        return self.get_chat(chat_id).start()

    ## Decorators

    ## with_info
    @classmethod
    def with_info(cls, callback):
        @wraps(callback)
        def new_callback(self, *args):
            info = self.get_info(*args)
            return callback(self, info)
        return new_callback

    ## cache
    @classmethod
    def cache(cls, callback):
        @wraps(callback)
        def new_callback(self, *args):
            info = self.get_info(*args)
            chat = self.get_chat(info['chat_id'])
            chat.save(info['message'])
            return callback(self, *args)
        return new_callback

    ## command
    @classmethod
    def command(cls, command_name: str, description: str='', **kwargs: dict):
        """ callback(self, *args)
        """
        def decor(callback):
            setattr(callback, 'handler', True)
            setattr(callback, 'command_handler', True)
            setattr(callback, 'name', command_name)
            setattr(callback, 'kw', kwargs)
            setattr(callback, 'description', description)
            return callback
        return decor

    ## message
    @classmethod
    def message(cls, *filters: Filters, **kwargs: dict):
        """ callback(self, update, context)
        """
        def decor(callback):
            setattr(callback, 'handler', True)
            setattr(callback, 'message_handler', True)
            setattr(callback, 'filters', filters)
            setattr(callback, 'kw', kwargs)
            return callback
        return decor

    ## error
    @classmethod
    def get_error(cls, callback):
        setattr(callback, 'handler', True)
        setattr(callback, 'error_handler', True)
        return callback

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def username(self):
        return self.updater.bot.name

    @property
    def bot_cache(self):
        return sum([chat.cache for chat in self.__data__.chats.values()], [])

    @property
    def command_list(self):
        return "\n".join([f"{name} - {description}" for name, description in self.commands])