import os.path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from webspot.web.routes import init_routes

# root path
root_path = os.path.abspath(os.path.dirname(__file__))

# app instance
app = FastAPI()

# static files
app.mount('/static', StaticFiles(directory=os.path.join(root_path, 'static')), name='static')

# set no cache for static files
if os.environ.get('WEBSERVER_NO_CACHE', 'false').lower() == 'true':
    __import__('webspot.web.middlewares.no_cache')

# templates
templates = Jinja2Templates(directory=root_path)

# initialize routes
init_routes()
