import asyncio
import logging
import os
import traceback

from fastapi import Request
from fastapi.responses import HTMLResponse

from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.web.app import app, templates
from webspot.web.utils.db import save_page_request


@app.get('/', response_class=HTMLResponse)
async def detect(request: Request):
    url = request.query_params.get('url')
    if url is None or url == '':
        return templates.TemplateResponse('index.html', {
            'request': request,
        })

    try:
        # create and run a detector
        detector = PlainListDetector(
            url=request.query_params.get('url'),
            request_method=os.environ.get('WEBSPOT_REQUEST_METHOD'),
        )
        detector.run()
    except Exception as e:
        err_lines = traceback.format_exception(type(e), e, e.__traceback__)
        err = ''.join(err_lines)
        logging.error(err)
        return templates.TemplateResponse('index.html', {
            'request': request,
            'url': request.query_params.get('url'),
            'error': err,
        })

    # save to db
    asyncio.ensure_future(save_page_request(detector, url))

    return templates.TemplateResponse('index.html', {
        'request': request,
        'url': request.query_params.get('url'),
        'html': detector.html_base64,
        'results': detector.results_base64,
    })
