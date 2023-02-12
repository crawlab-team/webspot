import asyncio
import logging
import os
import traceback

from fastapi import Request, HTTPException

from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.web.app import app, templates
from webspot.web.utils.db import save_page_request


@app.post('/detect')
async def detect(payload: dict):
    url = payload.get('url')
    if url is None or url == '':
        raise HTTPException(status_code=400, detail='url is required')
    method = payload.get('method') or 'request'

    try:
        # create and run a detector
        detector = PlainListDetector(
            url=url,
            request_method=method or os.environ.get('WEBSPOT_REQUEST_METHOD'),
        )
        detector.run()
    except Exception as e:
        err_lines = traceback.format_exception(type(e), e, e.__traceback__)
        err = ''.join(err_lines)
        logging.error(err)
        return {
            'url': url,
            'error': err,
        }

    # save to db
    asyncio.ensure_future(save_page_request(detector, url))

    return {
        'url': url,
        'html': detector.html_base64,
        'results': detector.results_base64,
    }
