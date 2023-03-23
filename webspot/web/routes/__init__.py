import os

MODULE_PREFIX = 'webspot.web.routes'


def init_routes():
    __import__(f'{MODULE_PREFIX}.index')
    __import__(f'{MODULE_PREFIX}.api.request')
