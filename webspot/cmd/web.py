import uvicorn


def cmd_web(args):
    uvicorn.run('webspot.web.app:app', reload=True, port=8000, log_level=args.log_level)
