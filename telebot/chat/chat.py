class Chat(object):

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.started = False

        self.__cache = []

    def start(self):
        self.started = True

    def save(self, message):
        self.__cache.append(message)

    @property
    def cache(self):
        return self.__cache.copy()

