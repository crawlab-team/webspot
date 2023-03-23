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
        'method': 'request',
        'no_async': False,
        'detectors': ['plain_list', 'pagination'],
    }
)) -> RequestOut:
    """Create a request. This is used to generate a new request to detect a web page."""
    d = Request(
        url=payload.url,
        method=payload.method,
        no_async=payload.no_async,
        detectors=payload.detectors,
    )
    d.save()

    if d.no_async:
        # run request (sync)
        d = _run_request(d)
    else:
        # run request (async)
        t = threading.Thread(target=_run_request, args=[d])
        t.start()

    return d.to_out()


def _run_request(d: Request):
    execution_time = {
        'html_requester': None,
        'graph_loader': None,
        'detectors': {},
    }
    try:
        # html requester
        tic = datetime.now()
        html_requester = HtmlRequester(
            url=d.url,
            request_method=d.method,
            request_rod_duration=d.duration,
        )
        html_requester.run()
        execution_time['html_requester'] = round((datetime.now() - tic).total_seconds() * 1000)

        # graph loader
        tic = datetime.now()
        graph_loader = GraphLoader(
            html=html_requester.html_,
            json_data=html_requester.json_data,
        )
        graph_loader.run()
        execution_time['graph_loader'] = round((datetime.now() - tic).total_seconds() * 1000)

        # run detectors
        html = html_requester.html
        for detector_name in d.detectors:
            # start time
            tic = datetime.now()

            # detector class
            if detector_name == DETECTOR_PLAIN_LIST:
                detector_cls = PlainListDetector
            elif detector_name == DETECTOR_PAGINATION:
                detector_cls = PaginationDetector
            else:
                raise Exception(f'Invalid detector: {detector_name}')

            # run detector
            detector = detector_cls(
                graph_loader=graph_loader,
                html_requester=html_requester,
            )
            detector.run()

            # highlight html
            html = detector.highlight_html(html)

            # add to results
            d.results[detector_name] = [r.dict() for r in detector.results]

            # execution time
            execution_time['detectors'][detector_name] = round((datetime.now() - tic).total_seconds() * 1000)

        # update request
        d.status = REQUEST_STATUS_SUCCESS
        d.html = html_requester.html_
        d.html_highlighted = html
        d.execution_time = execution_time
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
