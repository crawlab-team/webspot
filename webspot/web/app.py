import logging
import os.path
import traceback

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, insert
from sqlalchemy.exc import NoResultFound
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from webspot.db.session import get_session
from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.models.page import PageModel
from webspot.models.request import RequestModel

root_path = os.path.abspath(os.path.dirname(__file__))

app = FastAPI()

app.mount('/static', StaticFiles(directory=os.path.join(root_path, 'static')), name='static')

templates = Jinja2Templates(directory=root_path)


@app.get('/', response_class=HTMLResponse)
async def detect(request: Request):
    url = request.query_params.get('url')
    if url is None or url == '':
        return templates.TemplateResponse('index.html', {
            'request': request,
        })

    try:
        # create and run a detector
        detector = PlainListDetector(url=request.query_params.get('url'))
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


@app.get('/requests')
async def requests(request: Request):
    session = get_session()
    stmt = select(RequestModel, PageModel) \
        .join(PageModel, PageModel.id == RequestModel.page_id)
    res = session.execute(stmt)
    return {
        'requests': [{
            'id': r.RequestModel.id,
            'page_id': r.PageModel.id,
            'page_url': r.PageModel.url,
        } for r in res],
    }
