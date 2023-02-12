import sqlalchemy
from sqlalchemy.exc import NoResultFound

from webspot.db.session import get_session
from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.models.page import PageModel
from webspot.models.request import RequestModel


async def save_page_request(detector: PlainListDetector, url: str):
    session = get_session()
    p = session.query(PageModel).filter(PageModel.url == url).one()
    if p is None:
        p = PageModel(url=url)
        session.add(p)
    session.execute(sqlalchemy.insert(RequestModel).values(
        page_id=p.id,
        html=detector.html_base64,
        results=detector.results_base64,
    ))
    session.commit()
