import asyncio
import logging
import traceback

from fastapi import Request

from webspot.constants.request_status import REQUEST_STATUS_SUCCESS, REQUEST_STATUS_ERROR
from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.graph.graph_loader import GraphLoader
from webspot.models.request import Request as RequestModel
from webspot.request.html_requester import HtmlRequester
from webspot.web.app import app


@app.get('/api/requests')
async def requests(request: Request):
    docs = RequestModel.objects().order_by('-_id')
    return [d.to_dict() for d in docs]


@app.get('/api/requests/{id}')
async def request(request: Request, id: str):
    """Get a request."""
    d = RequestModel.objects(pk=id).first()
    return d.to_dict()


@app.put('/api/requests/{id}')
async def request(request: Request, id: str):
    """Update a request."""
    d = RequestModel.objects(pk=id).first()
    _d = await request.json()
    d.update(_d)
    return d.to_dict()


@app.post('/api/requests')
async def request(request: Request):
    """Create a request."""
    _d = await request.json()
    d = RequestModel(**_d)
    d.save()

    # run request
    asyncio.run(_run_request(d))

    return d.to_dict()


async def _run_request(d: RequestModel):
    try:
        # html requester
        html_requester = HtmlRequester(
            url=d.url,
            request_method=d.method,
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

        # update request
        d.status = REQUEST_STATUS_SUCCESS
        d.html = html_requester.html
        d.html_highlighted = detector.html
        d.results = detector.results
        d.save()

    except Exception as e:
        err_lines = traceback.format_exception(type(e), e, e.__traceback__)
        err = ''.join(err_lines)
        logging.error(err)

        # update request
        d.status = REQUEST_STATUS_ERROR
        d.error = err
        d.save()
