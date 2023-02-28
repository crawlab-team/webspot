import json
from datetime import datetime
from typing import Optional

from mongoengine import Document, StringField, DateTimeField, pre_save
from pydantic import BaseModel

from webspot.utils.mongo import encode_mongo_document


class Base(Document):
    created_at = DateTimeField(default=datetime.utcnow)
    created_by = StringField()
    updated_at = DateTimeField(default=datetime.utcnow)
    updated_by = StringField()

    meta = {
        'abstract': True,
        'allow_inheritance': True,
    }

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.utcnow()

    def to_dict(self, *args, **kwargs):
        use_db_field = kwargs.pop("use_db_field", True)
        doc_json = encode_mongo_document(self.to_mongo(use_db_field))
        return json.loads(doc_json)


class BaseIn(BaseModel):
    created_at: datetime
    created_by: Optional[str]
    updated_at: Optional[datetime]
    updated_by: Optional[str]
