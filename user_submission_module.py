"""
GIFIA - 用户上传模块 (User Submission & Gatekeeper)
专家准入闸门：验证上传内容，自动脱敏，结构化提取
"""

import os
import json
import re
from typing import Dict, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
from openai import OpenAI

# ==================== 环境变量配置 ====================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# ==================== AI 分析函数（Failover） ====================

def get_ai_analysis(prompt: str) -> Optional[str]:
    """通用AI分析函数：优先使用 Gemini，失败后自动切换到 DeepSeek"""
    # 1) 尝试 Gemini
    try:
        models_to_try = [
            "models/gemini-2.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-flash-latest",
        ]
        last_err = None
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = (response.text or "").strip()
                if text:
                    return text
            except Exception as e:
                last_err = str(e)
                if any(k in str(e).lower() for k in ["quota", "rate", "429", "exceeded", "limit"]):
                    break
                continue
        if last_err:
            print(f"⚠️ Gemini 异常，切换至 DeepSeek...")
    except Exception as e:
        print(f"⚠️ Gemini 初始化失败，切换至 DeepSeek...")

    # 2) 尝试 DeepSeek
    try:
        if not DEEPSEEK_API_KEY:
            return None
        ds_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        completion = ds_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位资深保险反欺诈专家，擅长分析保险欺诈、逆选择和滥用案例。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=3000,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else None
    except Exception as e:
        print(f"❌ DeepSeek 失败: {str(e)}")
        return None


# ==================== 专家准入闸门 ====================

def validate_submission(content: str) -> Tuple[bool, Dict]:
    """
    验证上传内容是否符合保险欺诈/逆选择/滥用定义
    判定险种类型
    
    返回:
        (is_valid, validation_result)
    """
    prompt = f"""
你是一位全球寿险与健康险反欺诈专家。请分析以下上传内容，判断是否符合保险欺诈、逆选择或滥用定义。

【上传内容】
{content[:10000]}  # 限制长度

【分析任务】
1. **是否符合定义**：判断内容是否涉及以下情况之一：
   - Fraud（欺诈）：故意提供虚假信息或伪造事实以获取保险理赔
   - Abuse（滥用）：利用保险制度漏洞获取不当利益
   - Waste（浪费）：不必要的医疗或服务导致保险成本增加
   - Adverse Selection（逆选择）：高风险人群故意投保

2. **险种判定**：判断属于哪类险种：
   - 寿险（Life Insurance）
   - 重疾险（Critical Illness Insurance）
   - 医疗险（Health/Medical Insurance）
   - 其他（Other）

3. **案例质量**：判断是否为具体案例（而非通用描述）

【输出要求】
以 JSON 格式输出：
{{
    "is_valid": true/false,
    "fraud_type": "Fraud/Abuse/Waste/Adverse Selection/None",
    "line_of_business": "寿险/重疾险/医疗险/其他",
    "is_specific_case": true/false,
    "reason": "判断理由",
    "confidence": 0.0-1.0
}}
"""

    try:
        text = get_ai_analysis(prompt)
        if not text:
            return False, {"error": "AI 分析失败"}
        
        # 清理 JSON
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        result = json.loads(text)
        return result.get('is_valid', False), result
        
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False, {"error": str(e)}


# ==================== 自动脱敏 ====================

def deidentify_pii(content: str) -> Tuple[str, Dict]:
    """
    识别并遮蔽 PII 信息（个人身份信息）
    仅保留红旗指标和舞弊细节
    
    返回:
        (脱敏后的内容, PII 信息字典)
    """
    prompt = f"""
你是一位数据隐私专家。请识别以下内容中的 PII（个人身份信息），并生成脱敏版本。

【原始内容】
{content[:10000]}

【PII 类型】
- 姓名（包括中文和英文）
- 身份证号、护照号
- 电话号码
- 邮箱地址
- 地址（详细地址）
- 银行账号
- 其他可识别个人的信息

【脱敏要求】
1. 识别所有 PII 信息
2. 用占位符替换（如：[姓名]、[身份证号]、[电话]等）
3. **保留**：红旗指标、舞弊细节、时间、地点（城市级别）、金额、案件描述
4. **遮蔽**：所有个人身份信息

【输出要求】
以 JSON 格式输出：
{{
    "deidentified_content": "脱敏后的内容",
    "pii_found": {{
        "names": ["姓名1", "姓名2"],
        "id_numbers": ["身份证号1"],
        "phones": ["电话1"],
        "emails": ["邮箱1"],
        "addresses": ["地址1"]
    }}
}}
"""

    try:
        text = get_ai_analysis(prompt)
        if not text:
            return content, {}  # 如果失败，返回原内容
        
        # 清理 JSON
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        result = json.loads(text)
        return result.get('deidentified_content', content), result.get('pii_found', {})
        
    except Exception as e:
        print(f"⚠️ 脱敏失败: {str(e)}，返回原内容")
        return content, {}


# ==================== 结构化提取 ====================

def extract_case_from_submission(content: str, line_of_business: str) -> Optional[Dict]:
    """
    从用户上传内容中提取结构化案例信息
    使用5维度格式
    """
    prompt = f"""
你是一位全球寿险与健康险反欺诈专家（SIU 资深调查员）。请从以下上传内容中提取保险欺诈案例，并按照专业简报格式输出。

【上传内容】（已脱敏）
{content[:15000]}

【险种类型】
{line_of_business}

【分析任务】
请严格按照以下【简报格式】输出，所有内容必须用中文填写：

1. **Time (时间)**: 事件发生或判决的具体时间（格式：YYYY-MM-DD）
2. **Region (地区)**: 国家及城市
3. **Characters (人物/实体)**: 涉案人身份、保险公司、中介或医疗机构（已脱敏，使用占位符）
4. **Event (事件)**: 欺诈类型概括

5. **Process (经过)**: 必须严格使用以下5个标题，禁止描述性文字：

   **【风险画像】**
   投保时间、保额、出险间隔
   
   **【舞弊手法(MO)】**
   具体欺诈手段
   
   **【红旗指标(Red Flags)】**
   触发警报的异常指标
   
   **【核查手段建议】**
   确证方式和调查方法
   
   **【核保/风控启示】**
   预警价值和风控建议

6. **Result (结果)**: 判决结果、罚金或法律制裁

【输出要求】
- 必须以纯 JSON 格式输出
- Process 字段必须包含5个标题的详细内容，至少 600 字
- 字段名使用英文（Time, Region, Characters, Event, Process, Result）

现在请开始分析：
"""

    try:
        text = get_ai_analysis(prompt)
        if not text:
            return None
        
        # 清理 JSON
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        case_data = json.loads(text)
        
        # 验证必需字段
        required_fields = ['Time', 'Region', 'Characters', 'Event', 'Process', 'Result']
        for field in required_fields:
            if field not in case_data:
                case_data[field] = "未知"
        
        # 添加元数据
        case_data['Source_URL'] = f"user_submission_{datetime.now().isoformat()}"
        case_data['Created_at'] = datetime.now().isoformat()
        case_data['line_of_business'] = line_of_business
        
        return case_data
        
    except Exception as e:
        print(f"❌ 提取失败: {str(e)}")
        return None
