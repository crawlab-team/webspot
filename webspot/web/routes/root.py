import logging
import os
import traceback

from sqlalchemy import select, insert
from sqlalchemy.exc import NoResultFound
from fastapi import Request
from fastapi.responses import HTMLResponse

from webspot.db.session import get_session
from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.models.page import PageModel
from webspot.models.request import RequestModel
from webspot.web.app import app, templates


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
    session = get_session()
    try:
        p = session.scalars(select(PageModel).where(PageModel.url == url)).one()
    except NoResultFound:
        p = session.execute(insert(PageModel).values(url=url).returning(PageModel)).scalar()
    except Exception as e:
        raise e
    session.execute(insert(RequestModel).values(
        page_id=p.id,
        html=detector.html_base64,
        results=detector.results_base64,
    ))
    session.commit()

    return templates.TemplateResponse('index.html', {
        'request': request,
        'url': request.query_params.get('url'),
        'html': detector.html_base64,
        'results': detector.results_base64,
    })
