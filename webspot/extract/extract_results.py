from datetime import datetime
from typing import List

from webspot.constants.detector import DETECTOR_PAGINATION, DETECTOR_PLAIN_LIST
from webspot.constants.html_request_method import HTML_REQUEST_METHOD_REQUEST
from webspot.detect.detectors.pagination import PaginationDetector
from webspot.detect.detectors.plain_list import PlainListDetector
from webspot.graph.graph_loader import GraphLoader
from webspot.request.html_requester import HtmlRequester


def extract_rules(
    url: str = None,
    method: str = None,
    duration: int = None,
    html: str = None,
    detectors: List[str] = None,
):
    if method is None or method == '':
        method = HTML_REQUEST_METHOD_REQUEST

    if detectors is None:
        detectors = [DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION]

    execution_time = {
        'html_requester': None,
        'graph_loader': None,
        'detectors': {},
    }

    # html requester
    tic = datetime.now()
    html_requester = HtmlRequester(
        url=url,
        html=html,
        request_method=method,
        request_rod_duration=duration,
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
    results = {}
    detectors_ = []
    for detector_name in detectors:
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
        results[detector_name] = [r.dict() for r in detector.results]

        # add to detectors_
        detectors_.append(detector)

        # execution time
        execution_time['detectors'][detector_name] = round((datetime.now() - tic).total_seconds() * 1000)

    return results, execution_time, html_requester, graph_loader, detectors_
