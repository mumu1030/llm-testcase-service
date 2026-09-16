# LLM 自动生成测试用例服务（llm-testcase-service）

一个基于 **FastAPI** 的后端服务：输入「功能名 + 平台」，调用 **DeepSeek** 大模型自动生成结构化测试用例（Markdown 表格），并提供生成历史的查询、删除、导出能力。

> 项目定位：可作为独立工具使用，也可作为 **Dify 等 AI 工作流中 HTTP 节点的后端 API**。

---

## 功能特性

| 能力 | 说明 |
|------|------|
| 一键生成 | 支持 normal（正向）/ exception（异常）/ boundary（边界）/ security（安全）四类用例 |
| 结构化输出 | 通过 prompt 约束模型输出 6 列 Markdown 表格：编号 / 标题 / 前置条件 / 测试步骤 / 预期结果 / 优先级 |
| 先思考后编写 | prompt 内置「风险点分析 → 场景转化 → 用例编写」三步推理链，输出更贴合业务 |
| 历史管理 | 内存存储，支持查询列表、查询单条、删除 |
| 一键导出 | 将某次生成结果拼接成完整 Markdown 文本 |
| 稳定性 | LLM 调用带自动重试：超时重试、429 限流指数退避 |
| 自动文档 | FastAPI 自带交互式接口文档（Swagger UI），无需手写 |
| 接口测试 | 附 Postman 集合（10 个请求 / 32 条断言，含正常与异常流程），支持 Collection Runner 与 Newman 命令行执行 |

---

## 技术栈

- **Python** 3.9+（开发环境 3.13）
- **FastAPI** 0.140 + **Uvicorn**（Web 框架与 ASGI 服务器）
- **Pydantic v2**（请求/响应数据校验）
- **requests**（调用 LLM HTTP 接口）
- **python-dotenv**（管理密钥）
- **DeepSeek API**（`deepseek-chat` 模型）
- **Postman / Newman**（接口测试集合与命令行执行，依赖 Node.js）

---

## 目录结构

```
llm-testcase-service/
├── main.py                                   # 服务入口：创建 app、注册路由
├── models.py                                 # Pydantic 数据模型（请求体 / 记录结构）
├── routers/
│   ├── __init__.py
│   └── testcase.py                           # 测试用例相关路由（5 个接口）
├── services/
│   ├── __init__.py
│   ├── llm_client.py                         # 大模型调用客户端（含重试机制）
│   └── prompt_builder.py                     # prompt 构建器（拼装提示词）
├── postman/
│   └── llm-testcase-service.postman_collection.json   # 接口测试集合（10 请求 / 32 断言）
├── tests/                                    # 预留：自动化测试目录
├── requirements.txt                          # 依赖清单
├── .env                                      # 密钥配置（已在 .gitignore 中忽略）
└── .gitignore
```

**分层设计**：路由层（routers）只负责收请求、回响应；业务能力放在服务层（services），便于复用和替换模型。

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```
DEEPSEEK_API_KEY=你的密钥
```

> 密钥申请地址：https://platform.deepseek.com/
> `.env` 已在 `.gitignore` 中忽略，不会被提交到仓库。

### 3. 启动服务

```bash
uvicorn main:app --reload
```

启动成功后访问：

- 接口文档（推荐先看这个）：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/

---

## 接口清单

基础路径：`http://127.0.0.1:8000`

| # | 方法 | 路径 | 说明 |
|---|------|------|------|
| 1 | POST | `/api/v1/generate` | 生成测试用例并存入历史 |
| 2 | GET | `/api/v1/history` | 查询全部生成历史 |
| 3 | GET | `/api/v1/history/{record_id}` | 查询单条记录 |
| 4 | DELETE | `/api/v1/history/{record_id}` | 删除单条记录 |
| 5 | GET | `/api/v1/history/{record_id}/export` | 导出该记录的 Markdown 文本 |

### 请求示例

`POST /api/v1/generate`

```json
{
  "feature": "login",
  "platform": "Android",
  "test_types": ["normal", "exception", "boundary", "security"],
  "case_count": 5
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `feature` | string | ✅ | - | 功能名称，如 `login`、`扫码支付` |
| `platform` | string | ❌ | `Android` | 平台：`Android` / `iOS` / `Web` |
| `test_types` | string[] | ❌ | 四类全选 | 用例类型，可任选组合 |
| `case_count` | int | ❌ | `5` | 每类生成的用例条数，最小 1 |

### 响应示例（截断）

```json
{
  "id": 1,
  "feature": "login",
  "platform": "Android",
  "test_types": ["normal", "exception"],
  "case_count": 5,
  "cases": {
    "normal": "| 编号 | 用例标题 | ... |",
    "exception": "| 编号 | 用例标题 | ... |"
  },
  "created_at": "2026-09-15 10:32:31"
}
```

### 错误处理

请求不存在的记录时返回 404：

```json
{ "detail": "记录 1 不存在" }
```

---

## 接口测试

测试集合位于 `postman/`，包含 **10 个请求 / 32 条断言**，覆盖正常流程与异常流程两条主线。

### 用 Postman 调试

1. 打开 Postman → **Import** → 选择本仓库中的
   `postman/llm-testcase-service.postman_collection.json`
2. 集合已内置变量 `base_url`（默认 `http://127.0.0.1:8000`），
   如需更换端口，只改变量即可，所有请求会一起生效。
3. 集合分为两个文件夹：

   | 文件夹 | 请求 | 验证目标 |
   |--------|------|---------|
   | **正常流程** | 01 生成用例 → 02 查询历史列表 → 03 查询单条记录 → 04 导出 Markdown → 05 删除记录 | 功能正确性与跨接口数据一致性 |
   | **异常流程** | E1 参数越界 → E2 缺必填 → E3 参数值为空 → E4 下限为 0 → E5 查询不存在的记录 | 参数校验（422）与业务兜底（404）|

4. **⚠️ 请求之间有依赖，必须按顺序执行**：`01 生成用例` 会把返回的 `id` 写入集合变量
   `record_id`，后续请求通过 `{{record_id}}` 引用。单独执行 03/04/05 会因变量缺失而失败。
5. 删除是破坏性操作，排在正常流程**最后**；导出必须排在删除**之前**。
6. 每个请求的断言写在 **Scripts → Post-response**，执行后在 **Test Results** 查看绿勾/红叉。

### 用 Collection Runner 批量执行

点击集合右侧 `...` → **Run collection**，会按顺序执行全部 10 个请求、32 条断言。

### 用 Newman 命令行执行

[Newman](https://github.com/postmanlabs/newman) 是 Postman 官方的命令行执行工具，读取同一份集合文件，
适用于本地批量回归，也可接入 CI 流水线：

```bash
npm install -g newman

newman run postman/llm-testcase-service.postman_collection.json \
  --env-var "base_url=http://127.0.0.1:8000" \
  -r cli,json \
  --reporter-json-export reports/newman-report.json
```

预期输出（`--env-var` 用于给 `{{base_url}}` 传值，命令行环境下无需依赖 Postman 界面）：

```
requests      10    failed 0
assertions    32    failed 0
```

> 注：`01 生成用例` 会真实调用大模型，单次耗时数秒；其余请求均为毫秒级，整轮约 4～20 秒。

---

## 说明与限制

- **数据存储**：当前使用内存存储（列表），**服务重启后历史数据会清空**。V1 版本定位为接口打通与验证，持久化（SQLite / MySQL）列入后续计划。
- **生成耗时**：`test_types` 每多一类，就会多调用一次模型，四类全选时耗时较长（取决于模型响应速度），属正常现象。
- **导出方式**：当前导出接口返回 Markdown 文本字符串，尚未实现文件下载（`Content-Disposition`）。
- **兼容性**：全部代码已通过 Python 3.9 语法编译检测，3.9 及以上版本均可运行。

---

## 后续计划

- [ ] 接入 SQLite 持久化，历史数据不丢失
- [ ] 导出接口升级为文件下载（`.md` 文件）
- [ ] 补充 `tests/` 下的接口自动化测试
- [ ] 支持连通性校验与自定义模型（不用 DeepSeek 时的适配）
