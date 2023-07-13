from argparse import ArgumentParser

from dotenv import load_dotenv

from webspot.cmd.crawl import cmd_crawl
from webspot.cmd.request import cmd_request
from webspot.cmd.web import cmd_web
from webspot.constants.html_request_method import HTML_REQUEST_METHOD_REQUEST

load_dotenv()

parser = ArgumentParser()

subparsers = parser.add_subparsers(
    title='subcommands',
    description='valid subcommands',
    help='additional help',
)

crawl_parser = subparsers.add_parser('crawl')
crawl_parser.add_argument('--url', '-U', help='url to crawl')
crawl_parser.add_argument('--output', '-o', help='output file path')
crawl_parser.set_defaults(func=cmd_crawl)

web_parser = subparsers.add_parser('web')
web_parser.add_argument('--host', '-H', default='0.0.0.0', help='port')
web_parser.add_argument('--port', '-P', default=80, type=int, help='port')
web_parser.add_argument('--log-level', '-L', default='debug', help='log level')
web_parser.set_defaults(func=cmd_web)

request_parser = subparsers.add_parser('request')
request_parser.add_argument('--url', '-U', help='url to request', required=True)
request_parser.add_argument('--method', '-M', help='request method', default=HTML_REQUEST_METHOD_REQUEST)
request_parser.set_defaults(func=cmd_request)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
