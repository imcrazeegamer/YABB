import numpy as np
from bots.api import Bot


class DefaultBot(Bot):
    name = 'Default'
    say = 'I\'m a simple bot.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def bot_logic(self, api):
        return np.random.randint(-1, 2, (2,), dtype=int)


CLS = DefaultBot
