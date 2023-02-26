from fastapi.testclient import TestClient

from webspot.web.app import app

client = TestClient(app)
