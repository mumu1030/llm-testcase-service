from fastapi import FastAPI
from routers.testcase import router

app = FastAPI(title = "LLM自动生成测试用例V1")
app.include_router(router) #

#健康检查
@app.get("/")
def root():
    return{"message":"服务运行中","status":"ok"}