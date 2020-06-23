class Game(object):

    def __init__(self):
        self.__users = set()
        self.__active = None

    def user_join(self, user):
        self.__users.add(user)

    def user_flee(self, user):
        self.__users.discard(user)

    def __enter__(self, *args, **kwargs):
        self.__active = True
        return self

    def __exit__(self, *args, **kwargs):
        self.__active = False

        