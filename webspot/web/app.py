import os.path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from webspot.detect.detectors.plain_list import PlainListDetector

root_path = os.path.abspath(os.path.dirname(__file__))

app = FastAPI()

app.mount('/static', StaticFiles(directory=os.path.join(root_path, 'static')), name='static')

templates = Jinja2Templates(directory=root_path)


@app.get('/')
async def root():
    return {'status': 'ok'}


@app.get('/detect', response_class=HTMLResponse)
async def detect(request: Request):
    detector = PlainListDetector(url=request.query_params.get('url'))
    detector.run()

    return templates.TemplateResponse('index.html', {
        'request': request,
        'url': request.query_params.get('url'),
        'html': detector.html_base64,
        'results': detector.results_base64,
    })
