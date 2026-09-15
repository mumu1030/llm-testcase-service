from fastapi import APIRouter,HTTPException    
from models import GenerateRequest, HistoryRecord
from services.llm_client import call_llm_safe
from services.prompt_builder import build_test_case_prompt
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["测试用例"])

history_db = []
next_id = 1

@router.get("/history") #查询生成历史（用内存存储即可）
def history():
    return history_db

@router.get("/history/{record_id}") #查询单条生成记录
def get_record(record_id:int):
    for record in history_db:
        if record.id == record_id:
            return record
    raise HTTPException(status_code=404, detail=f"记录 {record_id} 不存在")

@router.delete("/history/{record_id}") #删除某条生成记录
def delete_record(record_id:int):
    for record in history_db:
        if record.id == record_id:
            history_db.remove(record)
            return{"message":"删除成功"}
    raise HTTPException(status_code=404, detail=f"记录 {record_id} 不存在")

@router.post("/generate") #生成测试用例
def generate(req:GenerateRequest):
    global next_id
    cases = {} # 键=类型名，值=AI生成的markdown，跟 HistoryRecord.cases 的格式对上
    for t in req.test_types: # 遍历 ["normal", "exception", "boundary"]
        prompt = build_test_case_prompt(req.feature,req.platform,t,req.case_count)   # 步骤1：拼一条精准的 promp
        result = call_llm_safe(prompt)  # 步骤2：把拼好的 prompt 交给（llm_client），调 DeepSeek 拿结果
        cases[t] = result
   
    record = HistoryRecord(
        id=next_id,
        feature=req.feature,
        platform=req.platform,
        test_types=req.test_types,
        case_count=req.case_count,
        cases=cases,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    history_db.append(record)        # ① 把对象塞进抽屉
    next_id = next_id + 1            # ② 发号器加一
    return record

@router.get("/history/{record_id}/export") #把结果导出为Markdown文本
def export_markdown(record_id:int):
    for record in history_db:
        if record.id == record_id:
            md = f"# {record.feature} {record.platform} 测试用例\n\n"
            for t,c in record.cases.items():
                md += f"## {t}\n\n{c}\n\n"
            return md
    raise HTTPException(status_code=404, detail=f"记录 {record_id} 不存在")