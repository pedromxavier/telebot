## Standard Library
from functools import wraps, reduce
import re

## Third-Party
from telegram import ParseMode
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler

## Local
from .botlib import stream, stdwar, stderr, stdout
from .data import Data

class MetaBot(type):

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        attrs = cls.get_handlers(attrs)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def get_handlers(cls, attrs: dict):
        commands = []
        command_handlers = []
        message_handlers = []
        error_handler = None
        for name in attrs:
            attr = attrs[name]
            if hasattr(attr, 'command_handler'):
                command_handlers.append((attr.name, attr, attr.kw))
                commands.append(attr.name)
            if hasattr(attr, 'message_handler'):
                message_handlers.append((attr.filters, attr, attr.kw))
            if hasattr(attr, 'error_handler'):
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

    def load(self):
        try:
            self.__data__.load(self.bot_name)
        except FileNotFoundError:
            pass

    def save(self):
        self.__data__.save(self.bot_name)

    def clear(self):
        self.__data__.clear()

    def stop(self):
        return self.updater.stop()

    def init(self):
        ## Setup Updater
        self.updater = Updater(token=self.token, use_context=True)
        stdout[1] << "> Updater setup"

        ## Retrieve Dispatcher
        self.dispatcher = self.updater.dispatcher

        ## Add Handlers
        self.add_handlers()
        stdout[1] << "> Handlers added"

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
        self.init()
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

            ## Include name in command list
            self.commands.append(command_name)

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
            'username': update.effective_chat.username,
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

    ## lock_start
    @classmethod
    def lock_start(cls, callback):
        @wraps(callback)
        def new_callback(self, *args):
            info = self.get_info(*args)
            chat = self.get_chat(info['chat_id'])
            if chat.started:
                return callback(self, *args)
            else:
                return None
        return new_callback

    ## command
    @classmethod
    def command(cls, command_name: str, **kwargs: dict):
        """ callback(self, *args)
        """
        def decor(callback):
            setattr(callback, 'command_handler', True)
            setattr(callback, 'name', command_name)
            setattr(callback, 'kw', kwargs)
            return callback
        return decor

    ## message
    @classmethod
    def message(cls, *filters: Filters, **kwargs: dict):
        """ callback(self, update, context)
        """
        def decor(callback):
            setattr(callback, 'message_handler', True)
            setattr(callback, 'filters', filters)
            setattr(callback, 'kw', kwargs)
            return callback
        return decor

    ## error
    @classmethod
    def set_error(cls, callback):
        setattr(callback, 'error_handler', True)
        return callback

    @property
    def bot_name(self):
        return self.__class__.__name__

    @property
    def bot_cache(self):
        return sum([chat.cache for chat in self.__data__.chats.values()], [])