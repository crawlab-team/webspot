import os.path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from webspot.web.routes import init_routes

root_path = os.path.abspath(os.path.dirname(__file__))

app = FastAPI()

app.mount('/static', StaticFiles(directory=os.path.join(root_path, 'static')), name='static')

templates = Jinja2Templates(directory=root_path)

init_routes()
