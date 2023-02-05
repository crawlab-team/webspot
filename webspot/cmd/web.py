import uvicorn


def cmd_web(args):
    uvicorn.run('webspot.web.app:app', reload=True, host=args.host, port=args.port, log_level=args.log_level)
