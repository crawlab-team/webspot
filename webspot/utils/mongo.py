import datetime
import json
from bson import ObjectId
from mongoengine.base import BaseDocument


class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseDocument):
            return str(obj.id)
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)


def encode_mongo_document(obj):
    return MongoEncoder().encode(obj)
