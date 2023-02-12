from fastapi import Request
from fastapi.responses import HTMLResponse

from webspot.web.app import app, templates


@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse('index.html', {
        'request': request,
    })
