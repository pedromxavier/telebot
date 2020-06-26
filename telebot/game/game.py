from telegram import User

class Game(object):
    """
    """
    MIN_PLAYERS = 1
    MAX_PLAYERS = None

    def __init__(self):
        self.__players = {}
        self.__started = False

    def start_game(self):
        if len(self) >= self.MIN_PLAYERS:
            pass
        else:
            self.__players.clear()

    def user_join(self, user: User):
        if (self.MAX_PLAYERS is None) or (len(self) < self.MAX_PLAYERS):
            self.__players[user.id] = {
                'user': user,
                'name': user.name,
                'username': user.username,
                'score': 0,
            }
        else:
            pass

    def user_flee(self, user_id: int):
        del self.__players[user_id]

    def __getitem__(self, user_id: int):
        return self.__players[user_id]

    def __enter__(self, *args, **kwargs):
        self.__started = True
        return self

    def __exit__(self, *args, **kwargs):
        self.__started = False

    @property
    def started(self):
        return self.__started

    @property
    def players(self) -> list:
        return list(self.__players)

        