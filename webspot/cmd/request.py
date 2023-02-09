from webspot.request.get_html import get_html


def cmd_request(args):
    get_html(args.url, request_method=args.method, save=True)
