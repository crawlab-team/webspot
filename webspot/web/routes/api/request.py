import threading
import traceback
from typing import List

from bs4 import BeautifulSoup
from fastapi import Body
from html_to_json_enhanced import convert
from starlette.responses import HTMLResponse

from webspot.constants.request_status import REQUEST_STATUS_SUCCESS, REQUEST_STATUS_ERROR
from webspot.detect.utils.highlight_html import embed_highlight, embed_annotate
from webspot.detect.utils.transform_html_links import transform_html_links
from webspot.extract.extract_results import extract_rules
from webspot.graph.graph_loader import GraphLoader
from webspot.models.node import NodeOut, Node
from webspot.models.request import Request, RequestOut
from webspot.request.html_requester import HtmlRequester
from webspot.web.app import app
from webspot.web.logging import logger
from webspot.web.models.payload.node import NodePayload
from webspot.web.models.payload.request import RequestPayload


@app.get('/api/requests')
async def requests(skip: int = 0, limit: int = 10) -> List[RequestOut]:
    """Get all requests."""
    docs = Request.objects[skip:(skip + limit)].order_by('-_id')
    return [d.to_out() for d in docs]


@app.get('/api/requests/{id}')
async def request(id: str) -> RequestOut:
    """Get a request."""
    d = Request.objects(pk=id).first()
    return d.to_out()


@app.get('/api/requests/{id}/html')
async def request_html(id: str, mode: str = 'highlight') -> HTMLResponse:
    """Get a request."""
    d = Request.objects(pk=id).first()
    if mode == 'annotate':
        return HTMLResponse(content=embed_annotate(transform_html_links(d.html_highlighted, d.url)))
    else:
        return HTMLResponse(content=embed_highlight(d.html_highlighted))


@app.get('/api/requests/{id}/nodes/{node_id}')
async def request_node(id: str, node_id: int) -> dict:
    """Get a request."""
    d = Request.objects(pk=id).first()
    json_data = convert(d.html)
    graph_loader = GraphLoader(d.html, json_data)
    graph_loader.run()
    n = graph_loader.get_node_by_id(node_id)
    return n


@app.post('/api/requests/{id}/nodes')
async def request_node(id: str, payload: NodePayload) -> NodeOut:
    """Get a request."""
    d = Request.objects(pk=id).first()
    assert d is not None, f'Request not found for id: {id}'
    soup = BeautifulSoup(d.html, 'html.parser')
    node = soup.select_one(payload.css_selector)
    assert node is not None, f'Node not found for selector: {payload.css_selector}'
    n = Node(
        request_id=id,
        node_id=int(node.attrs['node-id']),
        tag=payload.tag,
    )
    n.save()
    return n.to_out()


@app.post('/api/requests/{id}/nodes/{node_id}')
async def request_node(id: str, node_id: int, payload: NodePayload) -> NodeOut:
    """Get a request."""
    d = Request.objects(pk=id).first()
    assert d is not None, f'Request not found for id: {id}'
    n = Node(
        request_id=id,
        node_id=node_id,
        tag=payload.tag,
    )
    n.save()
    return n.to_out()


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
        update_request(
            d=d,
            status=REQUEST_STATUS_SUCCESS,
            html_requester=html_requester,
            detectors=detectors,
            execution_time=execution_time,
            results=results,
        )

    except Exception as e:
        err_lines = traceback.format_exception(type(e), e, e.__traceback__)
        err = ''.join(err_lines)
        logger.error(err)

        # update request
        d.status = REQUEST_STATUS_ERROR
        d.error = err
        d.save()

    return d


def update_request(d: Request, status: str, **kwargs):
    html_requester = kwargs.get('html_requester')
    detectors = kwargs.get('detectors')
    execution_time = kwargs.get('execution_time')
    results = kwargs.get('results')

    d.status = status
    d.html = html_requester.html_
    html = html_requester.html
    for detector in detectors:
        html = detector.highlight_html(html)
    d.html_highlighted = html
    d.execution_time = execution_time
    d.results = results
    d.save()
