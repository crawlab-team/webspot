from argparse import Namespace

from webspot.cmd.web import cmd_web

if __name__ == '__main__':
    args = Namespace(port=8000, log_level='debug')
    cmd_web(args)
