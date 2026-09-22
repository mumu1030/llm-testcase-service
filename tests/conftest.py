import pytest
from api import generate,delete_record

@pytest.fixture
def cleanup():
    created=[]
    yield created
    for rid in created:
        delete_record(rid)

@pytest.fixture
def make_record(cleanup):
    r = generate({"feature":"造假数据","platform":"iOS","test_types":[],"case_count":1})
    rid = r.json()["id"]
    cleanup.append(rid)
    yield rid