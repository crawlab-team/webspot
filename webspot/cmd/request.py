from webspot.request.html_requester import HtmlRequester


def cmd_request(args):
    html_requester = HtmlRequester(url=args.url, request_method=args.method)
    html_requester.run()
    print(html_requester.html)
