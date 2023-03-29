import threading
import traceback
from datetime import datetime
from typing import List

from fastapi import Body
from starlette.responses import HTMLResponse

from webspot.constants.detector import DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION
from webspot.constants.request_status import REQUEST_STATUS_SUCCESS, REQUEST_STATUS_ERROR
from webspot.detect.detectors.pagination import PaginationDetector
from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.detect.utils.highlight_html import embed_highlight_css
from webspot.extract.extract_results import extract_rules
from webspot.graph.graph_loader import GraphLoader
from webspot.models.request import Request, RequestOut
from webspot.request.html_requester import HtmlRequester
from webspot.web.app import app
from webspot.web.logging import logger
from webspot.web.models.payload.request import RequestPayload


@app.get('/api/requests')
async def requests(skip: int = 0, limit: int = 20) -> List[RequestOut]:
    """Get all requests."""
    docs = Request.objects[skip:(skip + limit)].order_by('-_id')
    return [d.to_out() for d in docs]


@app.get('/api/requests/{id}')
async def request(id: str) -> RequestOut:
    """Get a request."""
    d = Request.objects(pk=id).first()
    return d.to_out()


@app.get('/api/requests/{id}/html')
async def request_html(id: str) -> HTMLResponse:
    """Get a request."""
    d = Request.objects(pk=id).first()
    return HTMLResponse(content=embed_highlight_css(d.html_highlighted))


@app.put('/api/requests/{id}')
async def request(id: str) -> RequestOut:
    """Update a request."""
    d = Request.objects(pk=id).first()
    _d = await request.json()
    d.update(_d)
    return d.to_out()


@app.post('/api/requests')
async def request(payload: RequestPayload = Body(
    example={
        'url': 'https://quotes.toscrape.com',
        'html': '<html>...</html>',
        'method': 'request',
        'no_async': False,
        'detectors': ['plain_list', 'pagination'],
        'duration': 5,
    }
)) -> RequestOut:
    """Create a request. This is used to generate a new request to detect a web page."""
    d = Request(
        url=payload.url,
        html=payload.html,
        method=payload.method,
        no_async=payload.no_async,
        detectors=payload.detectors,
        duration=payload.duration,
    )
    d.save()

    if payload.html:
        d.no_async = True

    if d.no_async:
        # run request (sync)
        d = _run_request(d)
    else:
        # run request (async)
        t = threading.Thread(target=_run_request, args=[d])
        t.start()

    return d.to_out()


def _run_request(d: Request):
    try:
        results, execution_time, html_requester, graph_loader, detectors = extract_rules(
            url=d.url,
            method=d.method,
            duration=d.duration,
            html=d.html,
            detectors=d.detectors,
        )

        # update request
        d.status = REQUEST_STATUS_SUCCESS
        d.html = html_requester.html_
        html = html_requester.html
        for detector in detectors:
            html = detector.highlight_html(html)
        d.html_highlighted = html
        d.execution_time = execution_time
        d.results = results
        d.save()

    except Exception as e:
        err_lines = traceback.format_exception(type(e), e, e.__traceback__)
        err = ''.join(err_lines)
        logger.error(err)

        # update request
        d.status = REQUEST_STATUS_ERROR
        d.error = err
        d.save()

    return d
