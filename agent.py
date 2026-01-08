"""
Global Insurance Fraud Intelligence Agent (GIFIA) - 云端情报站
自动化抓取脚本：使用 Tavily 搜索 + Gemini 提取 + Supabase 存储
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
from supabase import create_client, Client
import google.generativeai as genai
from tavily import TavilyClient
from openai import OpenAI

# 从环境变量或配置文件读取 API Key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # 备份引擎：DeepSeek
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 初始化客户端
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Gemini 模型配置（使用 1.5 Pro 或 Flash）
# 模型将在 extract_case_info_with_gemini 函数中初始化


def get_ai_analysis(prompt: str) -> Optional[str]:
    """
    通用AI分析函数：优先使用 Gemini，失败或限额后自动切换到 DeepSeek 备份引擎
    返回纯文本字符串（期望为JSON字符串）；失败返回 None
    """
    # 1) 尝试 Gemini
    try:
        # 选择可用的 Gemini 模型
        models_to_try = [
            "models/gemini-2.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-flash-latest",
        ]
        last_err = None
        for model_name in models_to_try:
            try:
                print("[Gemini] 正在分析案例...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = (response.text or "").strip()
                if text:
                    return text
            except Exception as e:
                last_err = str(e)
                # 若是限额/速率等错误，则直接进入备份引擎
                if any(k in str(e).lower() for k in ["quota", "rate", "429", "exceeded", "limit"]):
                    print("⚠️ Gemini 限额或速率限制，正在切换至 DeepSeek 备份引擎...")
                    break
                # 其他错误，尝试下一个模型
                continue
        if last_err and not any(k in last_err.lower() for k in ["quota", "rate", "429", "exceeded", "limit"]):
            # Gemini 其他错误，仍尝试 DeepSeek
            print(f"⚠️ Gemini 异常: {last_err[:120]} ... 正在切换至 DeepSeek 备份引擎...")
    except Exception as e:
        print(f"⚠️ Gemini 初始化失败: {str(e)}，切换至 DeepSeek 备份引擎...")

    # 2) 尝试 DeepSeek（OpenAI 兼容接口）
    try:
        if not DEEPSEEK_API_KEY:
            print("❌ DeepSeek 备份引擎未配置（缺少 DEEPSEEK_API_KEY）")
            return None
        print("[DeepSeek] 正在接管任务...")
        ds_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        completion = ds_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位资深保险反欺诈分析师，擅长从长文中抽取严格结构化信息。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else None
    except Exception as e:
        print(f"❌ DeepSeek 备份引擎失败: {str(e)}")
        return None


def search_fraud_cases(query: str = "Global insurance fraud case 2025 2026", max_results: int = 10) -> List[Dict]:
    """
    使用 Tavily API 搜索全球保险欺诈案例
    
    参数:
        query: 搜索关键词
        max_results: 最大返回结果数
    
    返回:
        搜索结果列表，每个结果包含 URL 和内容摘要
    """
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",  # 深度搜索模式
            max_results=max_results,
            include_domains=None,  # 不限制域名
            include_answer=True,  # 包含答案摘要
            include_raw_content=False,  # 不包含原始HTML内容
        )
        
        results = []
        for item in response.get('results', []):
            results.append({
                'url': item.get('url', ''),
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'score': item.get('score', 0)
            })
        
        print(f"✅ 搜索到 {len(results)} 个结果")
        return results
    except Exception as e:
        print(f"❌ Tavily 搜索失败: {str(e)}")
        return []


def get_gemini_model():
    """
    获取可用的 Gemini 模型（优先使用 Flash，如果不可用则使用 Pro）
    使用最新的 Gemini 2.5 或 2.0 模型
    """
    # 按优先级顺序尝试模型（使用带 models/ 前缀的完整名称）
    models_to_try = [
        'models/gemini-2.5-flash',      # 最新的 Flash 模型
        'models/gemini-2.0-flash',      # Gemini 2.0 Flash
        'models/gemini-flash-latest',   # 最新 Flash
        'models/gemini-2.5-pro',        # 最新的 Pro 模型
        'models/gemini-pro-latest',     # 最新 Pro
    ]
    last_error = None
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            # 简单测试调用以验证模型是否可用
            model.generate_content("test")
            print(f"✅ 使用 Gemini 模型: {model_name}")
            return model
        except Exception as e:
            last_error = str(e)
            continue
    
    # 如果所有模型都失败，返回最新的 Flash 作为默认
    print(f"⚠️ 警告: 无法验证 Gemini 模型，使用默认模型 models/gemini-flash-latest")
    if last_error:
        print(f"   最后的错误信息: {last_error[:200]}")
    return genai.GenerativeModel('models/gemini-flash-latest')


def extract_case_info_with_gemini(url: str, title: str, content: str) -> Optional[Dict]:
    """
    使用 AI 引擎（Gemini 主引擎 + DeepSeek 备份引擎）从搜索结果中提取结构化的案例信息
    实现 Failover 机制：当 Gemini 限额或出错时，自动切换到 DeepSeek
    
    参数:
        url: 原始链接
        title: 标题
        content: 内容摘要（可以是 Firecrawl 的 Markdown 全文或搜索摘要）
    
    返回:
        结构化字典，包含所有必需字段，如果提取失败则返回 None
    """
    prompt = f"""
你是一位全球寿险与健康险反欺诈专家（SIU 资深调查员）。请从以下网页信息中深度分析保险欺诈案例，并按照专业简报格式输出结构化摘要。

网页标题: {title}
网页链接: {url}
网页内容摘要:
{content}

【分析任务】
请严格按照以下【简报格式】输出结构化摘要，所有内容必须用中文填写：

1. **Time (时间)**: 事件发生或判决的具体时间（格式：YYYY-MM-DD 或 YYYY年MM月DD日）
2. **Region (地区)**: 国家及城市（例如：美国纽约、中国上海）
3. **Characters (人物/实体)**: 涉案人身份、保险公司、中介或医疗机构（用逗号分隔）
4. **Event (事件)**: 欺诈类型概括（例如：寿险欺诈、健康险欺诈、医疗保险欺诈）

5. **Process (经过)**: 【重点】按照 SIU 专业简报格式，严格使用以下5个标题，禁止使用描述性文字，只输出结构化内容：

   **【风险画像】**
   - 投保时间、投保人信息、投保动机
   - 保险金额、保险类型、保障范围
   - 出险时间、出险间隔（投保后多久出险）、是否在等待期内
   - 如果文中未提及，标注"信息缺失"
   
   **【舞弊手法(MO)】**
   - 具体欺诈手段（挂床住院、海外假收据、伪造医疗记录、虚假诊断证明、夸大病情、重复理赔等）
   - 使用的技术、工具、文件
   - 涉及的人员、机构
   - 如果文中未提及，标注"信息缺失"
   
   **【红旗指标(Red Flags)】**
   - 理赔中触发的警报（病历逻辑矛盾、财务状况不符、时间线异常、医疗记录不一致、诊断与症状不符、医院资质可疑等）
   - 系统检测到的异常指标
   - 人工审核发现的疑点
   - **这是重点字段，必须详细列出，如果文中未提及，明确标注"信息缺失"**
   
   **【核查手段建议】**
   - 确证方式（医保大数据比对、线下走访、第三方调查、财务审计、医疗记录验证、专家会诊、背景调查等）
   - 使用的技术手段（数据挖掘、行为分析、网络追踪等）
   - 证据收集方法
   - 如果文中未提及，标注"信息缺失"
   
   **【核保/风控启示】**
   - 前端核保预警价值
   - 应建立的风控规则（投保后短期内出险预警、特定医院黑名单、大额理赔二次审核等）
   - 前端风险识别方法（投保人财务状况核查、医疗记录交叉验证、等待期监控等）
   - 系统化改进建议
   - 如果文中未提及，可基于案例特点给出专业建议

6. **Result (结果)**: 判决结果、罚金或法律制裁（包括金额、刑期等）

【输出要求】
- 必须以纯 JSON 格式输出，不要包含任何 Markdown 标记或额外说明
- 所有字段都必须填写，如果信息缺失请填写"未知"或"待补充"
- Process 字段必须严格使用5个标题：【风险画像】、【舞弊手法(MO)】、【红旗指标(Red Flags)】、【核查手段建议】、【核保/风控启示】
- Process 字段禁止使用描述性文字，只输出结构化内容，至少 500 字以上
- 字段名使用英文（Time, Region, Characters, Event, Process, Result）

【JSON 格式示例】
{{
    "Time": "2025-01-15",
    "Region": "美国纽约",
    "Characters": "John Smith, ABC保险公司, XYZ医疗中心",
    "Event": "医疗保险欺诈",
    "Process": "【风险画像】\\n投保时间：2024年6月\\n保额：50万美元\\n出险间隔：投保后3个月\\n\\n【舞弊手法(MO)】\\n伪造海外医疗收据\\n虚假诊断证明\\n\\n【红旗指标(Red Flags)】\\n医疗记录时间与出入境记录不符\\n理赔金额异常偏高\\n\\n【核查手段建议】\\n医保大数据比对\\n出入境记录核查\\n\\n【核保/风控启示】\\n建立投保后6个月内大额理赔预警机制",
    "Result": "被判有期徒刑5年，罚款50万美元"
}}

现在请开始专业分析：
"""

    try:
        # 通过统一接口执行（含主从备份切换）
        text = get_ai_analysis(prompt)
        if not text:
            raise ValueError("AI 引擎未返回任何内容")
        
        # 清理可能的 Markdown 代码块标记
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # 解析 JSON
        case_data = json.loads(text)
        
        # 验证必需字段
        required_fields = ['Time', 'Region', 'Characters', 'Event', 'Process', 'Result']
        for field in required_fields:
            if field not in case_data:
                case_data[field] = "未知"
        
        # 添加元数据
        case_data['Source_URL'] = url
        case_data['Created_at'] = datetime.now().isoformat()
        
        print(f"✅ 成功提取案例: {case_data.get('Event', '未知事件')}")
        return case_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败 (URL: {url}): {str(e)}")
        print(f"原始响应前500字符: {text[:500] if 'text' in locals() else 'N/A'}")
        return None
    except Exception as e:
        print(f"❌ AI 提取失败 (URL: {url}): {str(e)}")
        return None


def check_duplicate(url: str) -> bool:
    """
    检查数据库中是否已存在该 URL（去重）
    
    参数:
        url: 要检查的 URL
    
    返回:
        True 表示已存在（重复），False 表示不存在（新案例）
    """
    try:
        result = supabase.table('fraud_cases').select('id').eq('source_url', url).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"⚠️ 查重失败: {str(e)}")
        return False


def save_to_supabase(case_data: Dict) -> bool:
    """
    将案例数据保存到 Supabase 数据库
    
    参数:
        case_data: 包含所有字段的案例字典
    
    返回:
        True 表示保存成功，False 表示保存失败
    """
    try:
        # 准备插入数据
        insert_data = {
            'time': case_data.get('Time', '未知'),
            'region': case_data.get('Region', '未知'),
            'characters': case_data.get('Characters', '未知'),
            'event': case_data.get('Event', '未知'),
            'process': case_data.get('Process', '未知'),
            'result': case_data.get('Result', '未知'),
            'source_url': case_data.get('Source_URL', ''),
            'created_at': case_data.get('Created_at', datetime.now().isoformat())
        }
        
        # 插入数据库
        result = supabase.table('fraud_cases').insert(insert_data).execute()
        
        if result.data:
            print(f"✅ 成功保存到数据库: {insert_data['event']}")
            return True
        else:
            print(f"⚠️ 保存失败: 无返回数据")
            return False
            
    except Exception as e:
        print(f"❌ 保存到 Supabase 失败: {str(e)}")
        return False


def main():
    """
    主函数：执行完整的抓取流程
    1. 搜索案例
    2. 提取信息
    3. 去重检查
    4. 保存到数据库
    """
    print("=" * 60)
    print("🚀 GIFIA - 全球保险欺诈情报抓取开始")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 验证 API Key
    if not all([TAVILY_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        print("❌ 错误: 缺少必要的 API Key 或配置")
        print("请检查环境变量: TAVILY_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY")
        return
    
    # 步骤1: 搜索案例
    print("\n📡 步骤1: 搜索全球保险欺诈案例...")
    # 注意：考虑到 Gemini API 限流（每分钟5次），建议 max_results 不超过 5
    search_results = search_fraud_cases(
        query="Global insurance fraud case 2025 2026",
        max_results=5  # 减少为 5 个，避免限流
    )
    
    if not search_results:
        print("⚠️ 未搜索到任何结果，程序退出")
        return
    
    # 步骤2: 提取并保存
    print(f"\n🔍 步骤2: 开始提取案例信息（共 {len(search_results)} 个）...")
    saved_count = 0
    skipped_count = 0
    failed_count = 0
    
    for i, result in enumerate(search_results, 1):
        url = result['url']
        title = result['title']
        content = result['content']
        
        print(f"\n--- 处理第 {i}/{len(search_results)} 个案例 ---")
        print(f"URL: {url[:80]}...")
        
        # 检查是否重复
        if check_duplicate(url):
            print(f"⏭️  跳过: URL 已存在（去重）")
            skipped_count += 1
            continue
        
        # 提取案例信息
        case_data = extract_case_info_with_gemini(url, title, content)
        
        if not case_data:
            print(f"❌ 提取失败，跳过")
            failed_count += 1
            continue
        
        # 保存到数据库
        if save_to_supabase(case_data):
            saved_count += 1
        else:
            failed_count += 1
        
        # 避免 API 限流，每处理一个案例后等待15秒
        # Gemini 免费版限制：每分钟 5 次请求，所以每个案例间隔 15 秒
        print(f"⏳ 等待 15 秒以避免 API 限流...")
        time.sleep(15)
    
    # 输出统计信息
    print("\n" + "=" * 60)
    print("📊 抓取完成统计")
    print("=" * 60)
    print(f"✅ 成功保存: {saved_count} 个案例")
    print(f"⏭️  跳过（重复）: {skipped_count} 个案例")
    print(f"❌ 失败: {failed_count} 个案例")
    print(f"📈 总计处理: {len(search_results)} 个搜索结果")
    print("=" * 60)


if __name__ == "__main__":
    main()
