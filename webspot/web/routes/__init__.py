import os

MODULE_PREFIX = 'webspot.web.routes.'


def init_routes():
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        __import__(f'{MODULE_PREFIX}{module[:-3]}', locals(), globals())
