import requests
import allure
from config import BASE_URL,TIMEOUT

def _attach(r,payload=None):#把请求和响应塞进allure报告
    allure.attach(f"{r.request.method} {r.request.url}","请求信息",allure.attachment_type.TEXT)
    if payload is not None:
        allure.attach(str(payload),"请求体",allure.attachment_type.TEXT)
    allure.attach(r.text,"响应体",allure.attachment_type.JSON)

@allure.step("调用生成用例接口")
def generate(payload): #POST/api/v1/generate
    r = requests.post(f"{BASE_URL}/api/v1/generate", json=payload,timeout=TIMEOUT)
    _attach(r,payload)
    return r

@allure.step("获取历史记录列表")
def list_history(): #Get/api/v1/history
    r = requests.get(f"{BASE_URL}/api/v1/history",timeout=TIMEOUT)
    _attach(r)
    return r

@allure.step("查询历史记录 {rid}")
def get_record(rid): #Get/api/v1/history/{rid}
    r = requests.get(f"{BASE_URL}/api/v1/history/{rid}",timeout=TIMEOUT)
    _attach(r)
    return r

@allure.step("删除历史记录 {rid}")
def delete_record(rid): #Delete/api/v1/history/{rid}
    r = requests.delete(f"{BASE_URL}/api/v1/history/{rid}",timeout=TIMEOUT)
    _attach(r)
    return r

@allure.step("导出历史记录 {rid}")
def export_record(rid): #Get/api/v1/history/{rid}/export
    r = requests.get(f"{BASE_URL}/api/v1/history/{rid}/export",timeout=TIMEOUT)
    _attach(r)
    return r