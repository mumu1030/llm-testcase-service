import pytest
import allure
import yaml
from pathlib import Path
from api import generate

DATA_FILE = Path(__file__).parent / "data" / "generate_cases.yaml" #数据绝对路径

with open(DATA_FILE,"r",encoding="utf-8") as f:
    CASES = yaml.safe_load(f)

@allure.feature("用例生成接口")
@allure.title("参数校验:{case[name]}")
@pytest.mark.parametrize("case",CASES,ids=[c["name"] for c in CASES])
def test_generate_error(case):
    r = generate(case["body"])
    assert r.status_code == 422

@allure.feature("用例生成接口")
@allure.title("case_count取上限3(空类型,不调模型)")
def test_generate_count_max(cleanup):
    r = generate({"feature":"login","platform":"Android","test_types":[],"case_count":3})
    assert r.status_code == 200
    body = r.json()
    cleanup.append(body["id"])

@allure.feature("用例生成接口")
@allure.title("参数校验错误要定位到具体字段")
def test_generate_error_detail_points_to_field():
    r = generate({"feature":"login","platform":"Android","test_types":["normal"],"case_count":9999})
    assert r.status_code == 422
    body = r.json()
    assert body["detail"][0]["loc"][1] == "case_count"

@allure.feature("用例生成接口")
@allure.title("单类型生成（调1次模型)")
@pytest.mark.llm
@pytest.mark.flaky(reruns=0)
def test_generate_one_type(cleanup):
    r = generate({"feature":"登录","platform":"iOS","test_types":["normal"],"case_count":1})
    assert r.status_code == 200
    body = r.json()
    assert body["feature"] == "登录"
    assert body["platform"] == "iOS"
    assert body["test_types"] == ["normal"]
    assert body["case_count"] == 1
    assert len(body["cases"]) == 1
    assert len(body["cases"]["normal"]) > 100
    cleanup.append(body["id"])

@allure.feature("用例生成接口")
@allure.title("最小参数生成(走默认值,调4次模型)")
@pytest.mark.llm
@pytest.mark.flaky(reruns=0)
def test_generate_minimal(cleanup):
    r = generate({"feature":"登录"})
    assert r.status_code == 200
    body = r.json()
    assert body["feature"] == "登录"
    assert body["platform"] == "Android"
    assert set(body["test_types"]) == {"normal", "exception", "boundary", "security"} #无序比较
    assert body["case_count"] == 2
    assert len(body["cases"]) == 4
    assert len(body["cases"]["normal"]) > 100
    cleanup.append(body["id"])