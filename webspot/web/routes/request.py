from sqlalchemy import select
from fastapi import Request

from webspot.db.session import get_session
from webspot.models.page import PageModel
from webspot.models.request import RequestModel
from webspot.web.app import app


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
