## Local
from ..botlib import pkload, pkdump
from ..chat import Chat


class Data(object):

    _EXT = 'bot-data'

    _MEMORY_DEFAULT = {
        'chats': {},
        'common': {}
    }
    def __init__(self):
        self._memory = self._MEMORY_DEFAULT.copy()

    def __getitem__(self, key):
        return self._memory[key]

    def __setitem__(self, key, value):
        self._memory[key] = value

    def get_chat(self, chat_id):
        try:
            return self.chats[chat_id]
        except KeyError:
            self.chats[chat_id] = Chat(chat_id)
            return self.chats[chat_id]

    def load(self, bot_name: str):
        fname = f'{bot_name}.{self._EXT}'
        self._memory.update(pkload(fname))

    def save(self, bot_name: str):
        fname = f'{bot_name}.{self._EXT}'
        pkdump(fname, self._memory)

    def clear(self):
        self._memory.update(self._MEMORY_DEFAULT)

    @property
    def chats(self):
        return self._memory['chats']

    @property
    def common(self):
        return self._memory['common']