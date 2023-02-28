import threading
import traceback

from fastapi import Body

from webspot.constants.detector import DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION
from webspot.constants.request_status import REQUEST_STATUS_SUCCESS, REQUEST_STATUS_ERROR
from webspot.detect.detectors.pagination import PaginationDetector
from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.graph.graph_loader import GraphLoader
from webspot.models.request import Request
from webspot.request.html_requester import HtmlRequester
from webspot.web.app import app
from webspot.web.logging import logger
from webspot.web.models.payload.request import RequestPayload
from webspot.web.models.response.request import RequestResponse


@app.get('/api/requests')
async def requests():
    """Get all requests."""
    docs = Request.objects().order_by('-_id')
    return [d.to_dict() for d in docs]


@app.get('/api/requests/{id}')
async def request(id: str):
    """Get a request."""
    d = Request.objects(pk=id).first()
    return d.to_dict()


@app.put('/api/requests/{id}')
async def request(id: str):
    """Update a request."""
    d = Request.objects(pk=id).first()
    _d = await request.json()
    d.update(_d)
    return d.to_dict()


@app.post('/api/requests')
async def request(payload: RequestPayload = Body(
    example={
        'url': 'https://quotes.toscrape.com',
        'method': 'request',
        'no_async': False,
        'detectors': ['plain_list', 'pagination'],
    }
)) -> RequestResponse:
    """Create a request. This is used to generate a new request to detect a web page."""
    d = Request(
        url=payload.url,
        method=payload.method,
        no_async=payload.no_async,
        detectors=payload.detectors,
    )
    d.save()

    if d.no_async:
        # run request (async)
        t = threading.Thread(target=_run_request, args=[d])
        t.start()
    else:
        # run request (sync)
        d = _run_request(d)

    return d.to_dict()


def _run_request(d: Request):
    try:
        # html requester
        html_requester = HtmlRequester(
            url=d.url,
            request_method=d.method,
        )
        html_requester.run()

        # graph loader
        graph_loader = GraphLoader(
            html=html_requester.html_,
            json_data=html_requester.json_data,
        )
        graph_loader.run()

        # run detectors
        html = html_requester.html_
        for detector_name in request.detectors:
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
            d.results[detector_name] = detector.results

        # update request
        d.status = REQUEST_STATUS_SUCCESS
        d.html = html_requester.html_
        d.html_highlighted = html
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
