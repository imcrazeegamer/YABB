from bots.api import Bot


class DefaultBot(Bot):
    name = 'Default'
    say = 'I\'m a simple bot.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


CLS = DefaultBot
