from typing import Optional, List

from pydantic import BaseModel, Field

from webspot.constants.detector import DETECTOR_PLAIN_LIST, DETECTOR_PAGINATION


class NodePayload(BaseModel):
    css_selector: Optional[str] = Field(
        title='CSS Selector',
        description='The CSS selector to use to find the node.',
    )
    tag: Optional[str] = Field(
        title='Tag',
        description='The tag annotated to the node.',
    )
