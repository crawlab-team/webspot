from typing import List, Optional, Dict, Union

from bson import ObjectId
from webspot.models.base import Base, BaseOut


class NodeOut(BaseOut):
    request_id: Optional[str]
    tag: Optional[str]


class Node(Base):
    meta = {'allow_inheritance': True}

    request_id: Optional[ObjectId]
    node_id: Optional[int]
    tag: Optional[str]

    def to_out(self) -> NodeOut:
        return NodeOut(
            id=str(self.id),
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            request_id=str(self.request_id),
            node_id=self.node_id,
            tag=self.tag,
        )
