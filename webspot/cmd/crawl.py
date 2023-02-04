from webspot.crawler.actions.run_crawler import run_crawler


def cmd_crawl(args):
    run_crawler(
        args.domain,
        [f'https://{args.domain}'] if args.urls is None else args.urls.split(','),
        args.data_root_dir,
    )
