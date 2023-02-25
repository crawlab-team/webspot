import json
from datetime import datetime

from mongoengine import Document, StringField, DateTimeField

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

    def to_dict(self, *args, **kwargs):
        use_db_field = kwargs.pop("use_db_field", True)
        doc_json = encode_mongo_document(self.to_mongo(use_db_field))
        return json.loads(doc_json)
