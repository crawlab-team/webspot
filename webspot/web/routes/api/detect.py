import asyncio
import logging
import os
import traceback

from fastapi import Request, HTTPException

from webspot.constants.html_request_method import HTML_REQUEST_METHOD_ROD
from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.graph.graph_loader import GraphLoader
from webspot.request.html_requester import HtmlRequester
from webspot.web.app import app
from webspot.web.utils.db import save_page_request


@app.post('/api/detect')
async def detect(payload: dict):
    url = payload.get('url')
    if url is None or url == '':
        raise HTTPException(status_code=400, detail='url is required')
    method = payload.get('method') or os.environ.get('WEBSPOT_REQUEST_METHOD') or HTML_REQUEST_METHOD_ROD

    try:
        # html requester
        html_requester = HtmlRequester(
            url=url,
            request_method=method,
        )
        html_requester.run()

        # graph loader
        graph_loader = GraphLoader(
            html=html_requester.html,
            json_data=html_requester.json_data,
        )
        graph_loader.run()

        # detector
        detector = PlainListDetector(
            graph_loader=graph_loader,
            html_requester=html_requester,
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
