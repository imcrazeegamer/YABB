import pkgutil, importlib
from pathlib import Path


BOTS_DIR = str(Path.cwd() / 'bots')
BOT_CLASSES = {}

print('Loading bot classes...')
for loader, modname, ispkg in pkgutil.iter_modules([BOTS_DIR]):
    module = importlib.import_module(f'.{modname}', f'bots')
    if not hasattr(module, 'CLS'):
        print(f'Disqualified {modname}, no bot class')
        continue
    cls = module.CLS
    name = cls.name
    if name in BOT_CLASSES:
        raise ValueError(f'While resolving {cls}, found bot by the name "{name}" already exists: {BOT_CLASSES[name]}')
    print(f'Found bot: {name} {cls}')
    BOT_CLASSES[name] = cls
