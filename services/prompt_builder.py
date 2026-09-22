def build_test_case_prompt(feature,platform="Android",test_type="normal",case_count=2,example_case=None):
    """构建测试用例prompt
    feature:功能名称
    platform: 平台,Android/iOS/Web
    test_type:  normal/exception/boundary/security
    case_count: 生成用例数量
    example_case: 用例参考范例
    """

    type_guide = {
        "normal": f"重点覆盖正常业务流程，包含{case_count}条核心场景",
        "exception": f"重点覆盖异常场景（网络/服务器/参数异常），共{case_count}条",
        "boundary":  f"重点覆盖边界值（最大/最小/空值/特殊字符），共{case_count}条",
        "security":  f"重点覆盖安全场景（越权/注入/敏感信息泄露），共{case_count}条",
    }

    #-----默认参考范例（如果用户没传example_case,用这个的）
    if example_case is None:
        example_case = (
             "| 编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |\n"
             "|------|---------|---------|---------|---------|-------|\n"
             "| TC-PAY-EX-001 | 扫码支付-网络超时场景 | "
             "1.App版本v5.2.1已安装 "
             "2.已登录且余额>100元 "
             "3.WiFi网络延迟>5秒 | "
             "1.打开扫码页面 2.扫描有效商户码 "
             "3.输入金额10元 4.点击确认支付 "
             "5.在请求发送后立即断开网络 | "
             "页面5秒内弹出[网络异常，请检查网络后重试]提示，"
             "不扣款，支付按钮恢复可点击状态 | P1 |"
    )
    #---拼接返回prompt
    return (
        f"【角色】你是一名拥有10年经验的资深测试架构师,"
        f"精通{platform}端自动化测试和探索性测试，"
        f"擅长发现深层缺陷。\n\n"

        f"【参考范例】请严格模仿以下范例的格式和细节程度:\n\n"
        f"{example_case}\n\n"

        f"【思考步骤】请先分析再编写:\n"
        f"1.列出{feature}在{platform}端的3个关键异常风险点\n"
        f"2.将风险点转化为具体测试场景\n"
        f"3.为每个场景编写完整用例\n\n"

        f"【任务】为{platform}端-{feature}设计{case_count}条用例\n\n"

        f"【要求】{type_guide.get(test_type, type_guide['normal'])}\n\n" ## 如果传的test_type不存在，不报错，返回 normal 的值（兜底）

        f"【格式约束】\n"
        f"1.必须用markdown表格,含6列:编号/标题/前置条件/步骤/预期/优先级\n"
        f"2.前置条件三要素:App版本+网络状态+数据准备\n"
        f"3.预期结果必须可量化验证,禁用模糊描述\n"
        f"4.步骤用1.2.3编号,每步不超过1句话\n"
        f"5.优先级标注判定理由"
    )