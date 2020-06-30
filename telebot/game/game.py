## Standard Library
from functools import wraps

## Third-Party
from telegram import Bot, User

class Player(object):

    def __init__(self, user_id: int, chat_id: int, full_name: str=None):
        self.user_id: int = user_id
        self.chat_id: int = chat_id
        self.full_name: str = full_name

        self.score: int = 0

    def __str__(self):
        return self.full_name

class GameError(Exception):
    ...

class Game(object):
    """
    """
    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

        self.__players = {}
        self.__started = False

    @classmethod
    def start(cls, callback: callable) -> callable:
        @wraps(callback)
        def new_callback(self, *args, **kwargs):
            if not self.__started:
                try:
                    self.__started = True
                    return callback(self, *args, **kwargs)
                except:
                    self.__started = False        
            else:
                raise GameError('Game already started.')
        return new_callback

    @classmethod
    def finish(cls, callback: callable) -> callable:
        @wraps(callback)
        def new_callback(self, *args, **kwargs):
            if self.__started:
                try:
                    self.__started = False
                    return callback(self, *args, **kwargs)
                except:
                    self.__started = True
            else:
                raise GameError('Game already finished.')
        return new_callback

    def add_player(self, player: Player) -> None:
        self.__players[player.user_id] = player

    def rmv_player(self, user_id: int) -> None:
        del self.__players[user_id]

    def __contains__(self, user_id: int) -> bool:
        return (user_id in self.players)

    def __getitem__(self, user_id: int) -> Player:
        return self.__players[user_id]

    def __enter__(self, *args, **kwargs):
        self.__started = True
        return self

    def __exit__(self, *args, **kwargs):
        self.__started = False

    @property
    def started(self) -> bool:
        return self.__started

    @property
    def finished(self) -> bool:
        return not self.__started

    @property
    def players(self) -> list:
        return list(self.__players.values())

    @property
    def scores(self) -> list:
        return [(player.full_name, player.score) for player in self.players]

    @property
    def winner(self) -> Player:
        return max(self.players, key=(lambda player: player.score))
        