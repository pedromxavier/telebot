from ..game import Game

class Chat(object):

    def __init__(self, chat_id: int):
        self.__chat_id = chat_id
        self.__started = False
        self.__awake = True

        self.__cache = []

    def start(self):
        self.__started = True

    def save(self, message):
        self.__cache.append(message)

    def sleep(self):
        self.__awake = False

    def wakeup(self):
        self.__awake = True

    @property
    def chat_id(self):
        return self.__chat_id

    @property
    def started(self):
        return self.__started

    @property
    def awake(self):
        return self.__awake

    @property
    def cache(self):
        return self.__cache.copy()

class GameChat(Chat):

    def __init__(self, chat_id: int):
        Chat.__init__(self, chat_id)

        self.__game = Game()