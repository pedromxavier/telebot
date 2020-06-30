from ..bot import TeleBot
from ..botlib import stdout
from .game import Game, GameError

class GameBot(TeleBot):

    __game__ = Game

    def __init__(self, token: str, **options):
        TeleBot.__init__(self, token, **options)
        self.games = {} ## chat_id: int -> game: Game
        self.queue = {} ## user_id: int -> chat_id: int

    def update(self) -> None:
        for game_id in list(self.games):
            game = self.games[game_id]
            game.update()
            if game.finished:
                del self.games[game_id]

    def get_game(self, info: dict) -> Game:
        if info['chat_id'] in self.games:
            return self.games[info['chat_id']]
        else:
            raise GameError(f"A game does not exists for chat_id `{info['chat_id']}`")

    def in_group(self, info: dict):
        return (info['type'] in {'group', 'supergroup'})

    def in_game(self, info: dict):
        return self.in_group(info) and (info['chat_id'] in self.games) and (info['user_id'] in self.games[info['chat_id']])
        
