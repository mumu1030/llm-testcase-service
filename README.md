# LLM 自动生成测试用例服务（llm-testcase-service）

一个基于 **FastAPI** 的后端服务：输入「功能名 + 平台」，调用 **DeepSeek** 大模型自动生成结构化测试用例（Markdown 表格），并提供生成历史的查询、删除、导出能力。

> 项目定位：可作为独立工具使用，也可作为 **Dify 等 AI 工作流中 HTTP 节点的后端 API**。
> 工程配套：除服务本身外，仓库内还包含两套测试资产 —— **Postman 集合**（手工/批量回归）与 **pytest 自动化框架**（分层 + 数据驱动 + Allure 报告）。

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
| 自动化测试 | pytest 框架，**18 条接口用例**（11 条生成 + 7 条历史），分层设计 + YAML 数据驱动 + Allure 报告 |
| 手工回归 | 附 Postman 集合（10 个请求 / 32 条断言），支持 Collection Runner 与 Newman 命令行执行 |

---

## 技术栈

**服务端**

- **Python** 3.9+（开发环境 3.13）
- **FastAPI** 0.140 + **Uvicorn**（Web 框架与 ASGI 服务器）
- **Pydantic v2**（请求/响应数据校验）
- **requests**（调用 LLM HTTP 接口）
- **python-dotenv**（管理密钥）
- **DeepSeek API**（`deepseek-chat` 模型）

**测试端**

- **pytest** 9.1 —— 用例执行
- **allure-pytest** 2.16 + **Allure CLI** 2.46 —— 报告与失败现场还原
- **pytest-rerunfailures** 16.7 —— 失败重试（消除网络抖动造成的假失败）
- **PyYAML** 6.0 —— 数据驱动用例数据
- **Postman / Newman** —— 手工与命令行回归（依赖 Node.js）

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
├── tests/                                    # ⭐ pytest 接口自动化
│   ├── config.py                             # 多环境地址 + 超时（读环境变量）
│   ├── api.py                                # 唯一发送 HTTP 请求的地方（含 Allure 步骤与附件）
│   ├── conftest.py                           # 共享 fixture：cleanup / make_record
│   ├── data/generate_cases.yaml              # 数据驱动的用例数据
│   ├── test_generate.py                      # 用例生成接口：11 条
│   └── test_history.py                       # 历史记录接口：7 条
├── pytest.ini                                # pytest 配置：注册 llm 标记、关闭中文 ID 转义
├── postman/
│   └── llm-testcase-service.postman_collection.json   # 接口测试集合（10 请求 / 32 断言）
├── requirements.txt                          # 服务端依赖清单
├── .env                                      # 密钥配置（已在 .gitignore 中忽略）
└── .gitignore
```

**服务端分层**：路由层（routers）只负责收请求、回响应；业务能力放在服务层（services），便于复用和替换模型。

**测试端分层**（关键设计）：

| 层 | 文件 | 职责 |
|----|------|------|
| 配置层 | `config.py` | 环境地址与超时，全部走环境变量，不硬编码 |
| 接口层 | `api.py` | 封装 5 个接口的请求，**唯一允许写 `requests.` 的地方** |
| 数据层 | `conftest.py`、`data/*.yaml` | 共享 fixture 与用例数据 |
| 用例层 | `test_*.py` | 只做「调接口 + 断言」，不含请求细节 |

> 这样分层的好处：给所有接口统一加超时、加日志、加报告附件，都只需要改 `api.py` **一个文件**，用例文件零改动。

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

需要跑自动化测试时，额外安装测试依赖：

```bash
pip install -r requirements-dev.txt
```

> Allure 报告还需要本机安装 **Allure CLI**（macOS：`brew install allure`）。

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
  "test_types": ["normal", "exception"],
  "case_count": 2
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `feature` | string | ✅ | - | 功能名称，如 `login`、`扫码支付`；空字符串校验不过（422） |
| `platform` | string | ❌ | `Android` | 平台：`Android` / `iOS` / `Web` |
| `test_types` | string[] | ❌ | 四类全选 | 用例类型，可任选组合；**传 `[]` 则不调用模型**，只落一条空记录 |
| `case_count` | int | ❌ | `2` | 每类生成的用例条数，取值范围 **1 ~ 3**（越界返回 422） |

### 响应示例（截断）

```json
{
  "id": 1,
  "feature": "login",
  "platform": "Android",
  "test_types": ["normal", "exception"],
  "case_count": 2,
  "cases": {
    "normal": "| 编号 | 用例标题 | ... |",
    "exception": "| 编号 | 用例标题 | ... |"
  },
  "created_at": "2026-09-15 10:32:31"
}
```

### 错误处理

| 场景 | 状态码 | 响应 |
|------|--------|------|
| 记录不存在 | 404 | `{ "detail": "记录 9999 不存在" }` |
| 请求参数非法（含缺必填、越界、空串） | 422 | `{ "detail": [{ "loc": ["body", "case_count"], ... }] }` |

> 422 的 `detail` 是数组，其中 `loc` 会指明**出错的具体字段名**，便于前端定位。

---

## 自动化测试（pytest）

覆盖 5 个接口，**18 条用例**，覆盖参数校验、业务正确性、异常兜底三类。

### 运行方式

```bash
# 全量 18 条（含 2 条真实调用大模型，约 20 秒）
pytest tests/ -q

# 跳过烧钱/耗时的用例，只跑 16 条（秒级完成）⭐ 日常推荐
pytest tests/ -m "not llm" -q

# 指定环境 / 超时（环境变量驱动，无需改代码）
TEST_ENV=qa TEST_TIMEOUT=5 pytest tests/ -m "not llm" -q

# 实时打印每条请求日志（不管用例过没过）⭐ 排查时用
pytest tests/ -m "not llm" --log-cli-level=INFO -q
```

> ⚠️ 跑之前**必须先启动服务**（`uvicorn main:app --reload`），pytest 只发请求不起服务。

> 📋 **关于日志**：pytest 默认会**收起日志**，只在用例失败时才展示（那段叫 `Captured log`）。
> 日常跑不用管；**排查时加 `--log-cli-level=INFO`** 让它全程可见。
> 接口请求成功与否都会记 INFO，只有网络层异常（连不上 / 超时）才记 ERROR。
>
> ⚠️ **CI 环境务必加上它** —— CI 里没有浏览器打不开 HTML 报告，终端日志是唯一线索。

### 生成 Allure 报告

```bash
# ① 执行并产出原始结果
pytest tests/ -m "not llm" --alluredir=allure-results --clean-alluredir -q

# ② 渲染成网页
allure generate allure-results -o allure-report --clean

# ③ 打开查看
allure open allure-report
```

报告里能看到：

- **Behaviors 分组**：按 `@allure.feature("用例生成接口")` / `("历史记录接口")` 自动归类
- **中文用例标题**：`@allure.title("查询不存在的记录返回404")`
- **失败现场**：每个接口调用都是一个可折叠步骤，里面挂着当时的**请求信息 / 请求体 / 响应体**
  → 失败时不用回终端，直接就能回答「挂在哪一步、发了什么、收了什么」

> `allure-results/` 与 `allure-report/` 是产物目录，已在 `.gitignore` 中忽略。

### 数据驱动

参数校验类用例写在 `tests/data/generate_cases.yaml`，新增一条异常场景**只加 YAML、不动代码**：

```yaml
- name: count超过3
  body:
    feature: login
    platform: iOS
    test_types: [normal]
    case_count: 4
```

> 「缺字段」的正确写法是**该行不写**（而不是写 `field: ""`）—— 服务端对二者走的是两条不同的校验分支。

### 本次自动化的几个设计点

| 设计 | 做法 | 收益 |
|------|------|------|
| 请求出口收敛 | 只有 `api.py` 写 `requests.` | 加超时、加日志、加附件只改一个文件 |
| 造数据 + 自动清理 | `make_record` fixture 依赖 `cleanup` fixture | 用例不依赖脏数据，跑完库是干净的 |
| 慢用例隔离 | `@pytest.mark.llm` 标记 | 日常秒级回归，全量才调模型 |
| 中文标题可用 `-k` 筛 | `pytest.ini` 关闭 ID 转义 | `pytest -k "查询不存在"` 能正常命中 |

---

## 接口测试（Postman / Newman）

手工/命令行回归集合位于 `postman/`，包含 **10 个请求 / 32 条断言**，覆盖正常流程与异常流程两条主线。

> 说明：pytest 与 Postman 是**两套并存**的资产 —— pytest 面向 CI 与可追溯报告，Postman 面向快速手工验证与分享。

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
- **测试依赖**：运行依赖在 `requirements.txt`（服务端），测试依赖在 `requirements-dev.txt`（pytest / allure-pytest / PyYAML / pytest-rerunfailures），两者已分开；后者已包含前者，CI 只装一个文件即可。

---

## 后续计划

- [x] 补充接口自动化测试（pytest 框架，18 条用例 + Allure 报告）
- [ ] 接入 SQLite 持久化，历史数据不丢失
- [ ] 导出接口升级为文件下载（`.md` 文件）
- [x] 测试依赖拆分为 `requirements-dev.txt`，区分运行与开发环境
- [ ] 支持连通性校验与自定义模型（不用 DeepSeek 时的适配）
- [ ] CI 流水线接入：提交即跑 `-m "not llm"`、发布 Allure 报告
