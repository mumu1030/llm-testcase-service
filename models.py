from pydantic import BaseModel,Field

class GenerateRequest(BaseModel):
    feature:str = Field(...,min_length=1)
    platform:str = "Android"
    test_types:list[str] = ["normal","exception","boundary","security"]
    case_count:int = Field(default=5, ge=1)  # ge=1 表示必须 >= 1

class HistoryRecord(BaseModel):
    id: int
    feature:str
    platform:str
    test_types:list[str]
    case_count:int 
    cases:dict[str,str]
    created_at:str

