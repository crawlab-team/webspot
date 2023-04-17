from typing import List

from fastapi import Body

from webspot.constants.request_status import REQUEST_STATUS_SUCCESS
from webspot.detect.utils.transform_html_links import transform_url
from webspot.extract.extract_results import extract_rules
from webspot.models.link_list import LinkListResult, Link
from webspot.models.request import Request
from webspot.web.app import app
from webspot.web.models.payload.request import RequestPayload
from webspot.web.routes.api.request import update_request


@app.post('/api/links')
async def requests(payload: RequestPayload = Body(
    example={
        'url': 'https://quotes.toscrape.com',
        'html': '<html>...</html>',
    }
)) -> List[LinkListResult]:
    d = Request(
        url=payload.url,
        html=payload.html,
        method=payload.method,
        no_async=True,
        detectors=payload.detectors,
        duration=payload.duration,
    )
    d.save()

    # extract rules
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

    # root url
    root_url = d.url

    # link list results
    link_list_results = []

    for i, list_result in enumerate(results['plain_list']):
        # list items selector
        list_items_selector = list_result['selectors']['full_items']['selector']

        # fields
        fields = [f for f in list_result['fields'] if f['type'] == 'link_url']

        # link list result
        link_list_result = LinkListResult()
        link_list_result.name = list_result['name']
        link_list_result.confidence = list_result['score']
        link_list_result.list = []

        # link list
        link_list_result_list = []

        # text lengths to order max-text-length list
        text_lengths = []

        # iterate fields
        for f in fields:
            link_list = []
            text_length = 0

            # items elements
            el_items = graph_loader.soup.select(list_items_selector)

            # iterate items
            for el_item in el_items:
                link_list_result_link = Link()
                el_item_field = el_item.select_one(f['selector'])
                if not el_item_field:
                    continue
                url = el_item_field.attrs.get('href')
                if not url:
                    continue
                link_list_result_link.url = transform_url(root_url, url)
                link_list_result_link.text = el_item_field.get_text(strip=True)
                link_list.append(link_list_result_link)
                text_length += len(link_list_result_link.text)

            # if text_length / len(el_items) > 80:
            #     continue

            text_lengths.append(text_length)
            link_list_result_list.append(link_list)

        if len(text_lengths) == 0:
            continue

        # get element of link_list_result_list with max text length
        max_text_length_index = text_lengths.index(max(text_lengths))
        link_list_result.list = link_list_result_list[max_text_length_index]

        if len(link_list_result.list) > 0:
            link_list_results.append(link_list_result)

    return link_list_results
