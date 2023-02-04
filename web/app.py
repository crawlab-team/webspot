import base64

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from detect.detectors.plain_list import PlainListDetector

app = FastAPI()

app.mount('/static', StaticFiles(directory='web/static'), name='static')

templates = Jinja2Templates(directory='web/templates')


@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    detector = PlainListDetector(url=request.query_params.get('url'))
    detector.run()

    return templates.TemplateResponse('index.html', {
        'request': request,
        'url': request.query_params.get('url'),
        'results': detector.results,
        'html': detector.html_base64,
    })
