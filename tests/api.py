import requests
import allure
import logging
from config import BASE_URL,TIMEOUT

logger = logging.getLogger(__name__)

def _attach(r,payload=None):#把请求和响应塞进allure报告
    allure.attach(f"{r.request.method} {r.request.url}","请求信息",allure.attachment_type.TEXT)
    if payload is not None:
        allure.attach(str(payload),"请求体",allure.attachment_type.TEXT)
    allure.attach(r.text,"响应体",allure.attachment_type.JSON)
    logger.info("%s %s -> %s",r.request.method,r.request.url,r.status_code) 

def _send(method,url,payload=None):
    try:
        r = requests.request(method,url,json=payload,timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error("%s %s 请求失败: %s", method,url,e)
        raise
    _attach(r,payload)
    return r

@allure.step("调用生成用例接口")
def generate(payload): #POST/api/v1/generate
    return _send("POST",f"{BASE_URL}/api/v1/generate",payload)

@allure.step("获取历史记录列表")
def list_history(): #Get/api/v1/history
    return _send("GET",f"{BASE_URL}/api/v1/history")
 

@allure.step("查询历史记录 {rid}")
def get_record(rid): #Get/api/v1/history/{rid}
    return _send("GET",f"{BASE_URL}/api/v1/history/{rid}")

@allure.step("删除历史记录 {rid}")
def delete_record(rid): #Delete/api/v1/history/{rid}
    return _send("DELETE",f"{BASE_URL}/api/v1/history/{rid}")

@allure.step("导出历史记录 {rid}")
def export_record(rid): #Get/api/v1/history/{rid}/export
    return _send("GET",f"{BASE_URL}/api/v1/history/{rid}/export")