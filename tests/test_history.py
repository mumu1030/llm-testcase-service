import allure
from api import get_record, delete_record, export_record

@allure.feature("历史记录接口")
@allure.title("获取历史记录,200")
def test_get_existing_record(make_record):
    r = get_record(make_record)
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == make_record

@allure.feature("历史记录接口") #业务模块
@allure.title("删除历史记录，删除后查不到") #用例标题
def test_delete_existing_record(make_record):
    r = delete_record(make_record)
    assert r.status_code == 200
    assert r.json()["message"] == "删除成功"

    r2 = get_record(make_record)
    assert r2.status_code == 404

@allure.feature("历史记录接口")
@allure.title("导出历史记录")
def test_export_existing_record(make_record):
    r = export_record(make_record)
    assert r.status_code == 200
    body = r.json()
    assert body == "# 造假数据 iOS 测试用例\n\n"

@allure.feature("历史记录接口")
@allure.title("查询不存在的记录返回404")
def test_get_missing_record():
    r = get_record(9999)
    assert r.status_code == 404
    body = r.json()
    assert body["detail"] == "记录 9999 不存在"

@allure.feature("历史记录接口")
@allure.title("查询非数字ID返回422")
def test_get_invalid_id():
    r = get_record("abc")
    assert r.status_code == 422
    body = r.json()
    assert body["detail"][0]["loc"] == ["path", "record_id"]

@allure.feature("历史记录接口")
@allure.title("删除不存在的记录返回404")
def test_delete_missing_record():
    r = delete_record(9999)
    assert r.status_code == 404
    body = r.json()
    assert body["detail"] == "记录 9999 不存在"

@allure.feature("历史记录接口")
@allure.title("导出不存在的记录返回404")
def test_export_missing_record():
    r = export_record(9999)
    assert r.status_code == 404
    body = r.json()
    assert body["detail"] == "记录 9999 不存在"