from argparse import ArgumentParser

from webspot.cmd.crawl import cmd_crawl
from webspot.cmd.web import cmd_web

parser = ArgumentParser()

subparsers = parser.add_subparsers(
    title='subcommands',
    description='valid subcommands',
    help='additional help',
)

crawl_parser = subparsers.add_parser('crawl')
crawl_parser.add_argument('--domain', '-D', help='domain to crawl', required=True)
crawl_parser.add_argument('--urls', '-U', help='urls to crawl, comma separated')
crawl_parser.add_argument('--url-paths', '-P', help='root directory to store data')
crawl_parser.add_argument('--data-root-dir', '-d', help='root directory to store data')
crawl_parser.set_defaults(func=cmd_crawl)

web_parser = subparsers.add_parser('web')
web_parser.add_argument('--host', '-h', default='0.0.0.0', help='port')
web_parser.add_argument('--port', '-p', default=8000, type=int, help='port')
web_parser.add_argument('--log-level', '-L', default='debug', help='log level')
web_parser.set_defaults(func=cmd_web)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
