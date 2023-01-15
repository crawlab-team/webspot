from argparse import ArgumentParser

from cmd.crawl import cmd_crawl

parser = ArgumentParser()

subparsers = parser.add_subparsers(
    title='subcommands',
    description='valid subcommands',
    help='additional help',
)

crawl_parser = subparsers.add_parser('crawl')
crawl_parser.add_argument('--domain', '-D', help='domain to crawl', required=True)
crawl_parser.add_argument('--urls', help='urls to crawl, comma separated')
crawl_parser.add_argument('--data-root-dir', help='root directory to store data')
crawl_parser.set_defaults(func=cmd_crawl)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
