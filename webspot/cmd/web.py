import uvicorn


def cmd_web(args):
    uvicorn.run('webspot.web.app:app', reload=True, port=args.port, log_level=args.log_level)
