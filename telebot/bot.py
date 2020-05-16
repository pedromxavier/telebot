from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from functools import wraps

class MetaBot(type):
    
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, attrs)

class Bot(metaclass=MetaBot):

    command_handlers = []
    message_handlers = []

    commands = []

    def __init__(self, token=None, **options):
        self.token = token

    def start(self):
        raise NotImplementedError

    def run(self):
        ## Setup Updater
        self.updater = Updater(token=self.token, use_context=True)

        ## Retrieve Dispatcher
        self.dispatcher = self.updater.dispatcher

        ## Add Handlers
        self.add_handlers()
        
        try:
            self.updater.start_polling()
            self.updater.idle()
        except KeyboardInterrupt:
            return

    ## Context Management
    def __enter__(self, *args, **kwargs):
        self.run()

    def __exit__(self, *args, **kwargs):
        self.updater.stop()

    def add_handlers(self):
        for command_name, callback in self.command_handlers:
            new_callback = wraps(callback)(lambda update, context: callback(self, update, context))
            self.dispatcher.add_handler(CommandHandler(command_name, new_callback))

        for filters, callback in self.message_handlers:
            new_callback = wraps(callback)(lambda update, context: callback(self, update, context))
            self.dispatcher.add_handler(MessageHandler(filters, new_callback))
        

    @staticmethod
    def get_info(update, context) -> dict:
        """ get_info(update, context) -> dict
            This function is intended to gather the most relevant information
            from these two objects into a single dictionary.
        """
        return  {
            'chat_id': update.effective_chat.id,
            'bot' : context.bot,
        }

    ## decorators
    ## command vs. _command:
    ## 
    @classmethod
    def _command(cls, command_name: str):
        """ callback(self, update, context)
        """
        def decor(callback):
            cls.command_handlers.append((command_name, callback))
            cls.commands.append(command_name)
            return callback
        return decor

    @classmethod
    def command(cls, command_name: str):
        """ callback(self, update, context)
        """
        def decor(callback):
            @wraps(callback)
            def new_callback(self, update, context):
                return callback(self, self.get_info(update, context))
            cls.command_handlers.append((command_name, new_callback))
            cls.commands.append(command_name)
            return new_callback
        return decor

    ## message vs. _message
    ##
    @classmethod
    def _message(cls, filters: Filters):
        """ callback(self, update, context)
        """
        def decor(callback):
            cls.message_handlers.append((filters, callback))
            return callback
        return decor

    @classmethod
    def message(cls, filters: Filters):
        """ callback(self, update, context)
        """
        def decor(callback):
            @wraps(callback)
            def new_callback(self, update, context):
                return callback(self, self.get_info(update, context))
            cls.message_handlers.append((filters, new_callback))
            return new_callback
        return decor