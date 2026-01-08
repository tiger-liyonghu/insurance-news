"""
GIFIA - 种子案例库提取器
从深度研究报告中提取案例，构建50个核心种子案例库
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from supabase import create_client, Client
import google.generativeai as genai
from tavily import TavilyClient
from openai import OpenAI

# 尝试导入 docx 库
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️ python-docx 未安装，无法读取 Word 文档")
    print("请运行: pip install python-docx")

# ==================== 环境变量配置 ====================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 初始化客户端
genai.configure(api_key=GEMINI_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ==================== Word 文档提取 ====================

def extract_text_from_docx(file_path: str) -> str:
    """从 Word 文档中提取文本"""
    if not DOCX_AVAILABLE:
        return ""
    
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    except Exception as e:
        print(f"❌ 读取 Word 文档失败 {file_path}: {str(e)}")
        return ""


def extract_cases_from_reports(report_files: List[str]) -> List[Dict]:
    """
    从研究报告中提取案例
    
    参数:
        report_files: Word 文档文件路径列表
    
    返回:
        提取的案例列表
    """
    all_text = ""
    
    # 读取所有报告
    for file_path in report_files:
        if os.path.exists(file_path):
            print(f"📄 正在读取: {os.path.basename(file_path)}")
            text = extract_text_from_docx(file_path)
            all_text += f"\n\n=== {os.path.basename(file_path)} ===\n\n{text}"
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    if not all_text:
        print("❌ 未能从报告中提取任何文本")
        return []
    
    # 使用 Gemini 提取案例
    print(f"\n🧠 使用 AI 从报告中提取案例...")
    print(f"   报告总长度: {len(all_text)} 字符")
    
    prompt = f"""
你是一位全球寿险与健康险反欺诈专家（SIU 资深调查员）。请从以下深度研究报告中提取所有具体的保险欺诈案例。

【研究报告内容】
{all_text[:100000]}  # 限制长度避免超出 token 限制

【提取任务】
请提取报告中提到的所有具体案例，包括但不限于：
- "DMERx 10亿美元案"
- "无锡虹桥医院案"
- "台湾干冰截肢案"
- "英国医生 Neil Hopper 自残案"
- "泰国悬崖/杀妻骗保案"
- "印度 Star 24 假实验室案"
- 以及其他所有具体案例

【输出格式】
请以 JSON 数组格式输出，每个案例包含以下字段：
{{
    "case_name": "案例名称",
    "time": "时间（YYYY-MM-DD 或 YYYY年MM月DD日）",
    "region": "地区（国家及城市）",
    "characters": "涉案人/实体",
    "line_of_business": "险种（医疗险/重疾险/定期寿险等）",
    "fraud_type": "欺诈定性（Fraud/Abuse/Waste）",
    "modus_operandi": "舞弊手法（MO - 详述如何造假）",
    "red_flags": "红旗指标（预警信号）",
    "investigative_tips": "调查突破点",
    "underwriting_advice": "风控/核保建议",
    "result": "判决结果",
    "source_reference": "报告中的引用或页码"
}}

【要求】
- 只提取具体的案例，不要提取通用描述
- 如果某个字段信息缺失，填写"信息缺失"
- 输出纯 JSON 数组，不要包含任何 Markdown 标记
- 尽可能提取所有案例

现在请开始提取：
"""

    try:
        # 使用 Gemini 提取（带 Failover）
        text = None
        last_error = None
        
        # 尝试 Gemini
        try:
            print("   [Gemini] 正在分析报告...")
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content(prompt)
            text = response.text.strip()
        except Exception as e:
            last_error = str(e)
            error_str = str(e).lower()
            if any(k in error_str for k in ["quota", "rate", "429", "exceeded", "limit"]):
                print("   ⚠️ Gemini 限额，切换至 DeepSeek 备份引擎...")
            else:
                print(f"   ⚠️ Gemini 异常: {str(e)[:100]}，切换至 DeepSeek...")
        
        # 如果 Gemini 失败，尝试 DeepSeek
        if not text and DEEPSEEK_API_KEY:
            try:
                print("   [DeepSeek] 正在接管任务...")
                ds_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
                completion = ds_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一位全球寿险与健康险反欺诈专家（SIU 资深调查员），擅长从长文中提取具体案例。"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                )
                text = (completion.choices[0].message.content or "").strip()
            except Exception as e2:
                print(f"   ❌ DeepSeek 也失败: {str(e2)[:100]}")
                raise Exception(f"所有 AI 引擎都失败: Gemini={last_error}, DeepSeek={str(e2)}")
        
        if not text:
            raise Exception("AI 引擎未返回任何内容")
        
        # 清理可能的 Markdown 代码块标记
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # 清理控制字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # 解析 JSON
        cases = json.loads(text)
        
        if not isinstance(cases, list):
            cases = [cases]
        
        print(f"✅ 从报告中提取到 {len(cases)} 个案例")
        return cases
        
    except Exception as e:
        print(f"❌ 提取失败: {str(e)}")
        print(f"   原始响应前500字符: {text[:500] if 'text' in locals() else 'N/A'}")
        return []


# ==================== 外部补充 ====================

def search_additional_cases(keywords: List[str], target_count: int = 50) -> List[Dict]:
    """
    使用 Tavily 搜索补充案例，直到达到目标数量
    
    参数:
        keywords: 搜索关键词列表
        target_count: 目标案例数量
    
    返回:
        补充的案例列表
    """
    if not tavily_client:
        print("⚠️ Tavily 未配置，跳过外部搜索")
        return []
    
    all_cases = []
    
    for keyword in keywords:
        if len(all_cases) >= target_count:
            break
        
        try:
            print(f"\n🔍 搜索关键词: {keyword}")
            response = tavily_client.search(
                query=f"{keyword} insurance fraud case",
                search_depth="advanced",
                max_results=10,
                include_answer=True,
            )
            
            for item in response.get('results', []):
                if len(all_cases) >= target_count:
                    break
                
                # 这里可以调用 deep_research_flow 进行深度分析
                # 暂时只收集 URL 和标题
                case_info = {
                    'case_name': item.get('title', ''),
                    'source_url': item.get('url', ''),
                    'content': item.get('content', ''),
                }
                all_cases.append(case_info)
        
        except Exception as e:
            print(f"❌ 搜索失败 {keyword}: {str(e)}")
            continue
    
    print(f"✅ 外部搜索补充 {len(all_cases)} 个案例")
    return all_cases


# ==================== 结构化转换 ====================

def convert_to_seed_case_format(case_data: Dict) -> Dict:
    """
    将提取的案例转换为种子案例格式
    
    参数:
        case_data: 原始案例数据
    
    返回:
        标准化的种子案例数据
    """
    # 构建 Process 字段（按照 SIU 格式）
    process_parts = []
    
    # 风险画像
    scenario = f"投保时间：{case_data.get('time', '信息缺失')}\n"
    scenario += f"保额：{case_data.get('coverage_amount', '信息缺失')}\n"
    scenario += f"出险间隔：{case_data.get('claim_interval', '信息缺失')}"
    process_parts.append(f"【风险画像】\n{scenario}")
    
    # 舞弊手法
    mo = case_data.get('modus_operandi', '信息缺失')
    process_parts.append(f"【舞弊手法(MO)】\n{mo}")
    
    # 红旗指标
    red_flags = case_data.get('red_flags', '信息缺失')
    process_parts.append(f"【红旗指标(Red Flags)】\n{red_flags}")
    
    # 核查手段建议
    investigation = case_data.get('investigative_tips', '信息缺失')
    process_parts.append(f"【核查手段建议】\n{investigation}")
    
    # 核保/风控启示
    advice = case_data.get('underwriting_advice', '信息缺失')
    process_parts.append(f"【核保/风控启示】\n{advice}")
    
    process = "\n\n".join(process_parts)
    
    # 构建标准格式
    seed_case = {
        'Time': case_data.get('time', '未知'),
        'Region': case_data.get('region', '未知'),
        'Characters': case_data.get('characters', '未知'),
        'Event': case_data.get('case_name', case_data.get('event', '未知')),
        'Process': process,
        'Result': case_data.get('result', '未知'),
        'Source_URL': case_data.get('source_url', f"internal_report_{case_data.get('case_name', 'unknown')}"),
        'Created_at': datetime.now().isoformat(),
        # 新字段
        'line_of_business': case_data.get('line_of_business', '未知'),
        'fraud_type': case_data.get('fraud_type', '未知'),
        'modus_operandi': case_data.get('modus_operandi', '未知'),
        'red_flags': case_data.get('red_flags', '未知'),
        'investigative_tips': case_data.get('investigative_tips', '未知'),
        'underwriting_advice': case_data.get('underwriting_advice', '未知'),
        'is_seed_case': True,
        'last_shown_at': None,
    }
    
    return seed_case


# ==================== 数据库操作 ====================

def save_seed_cases_to_db(cases: List[Dict]) -> int:
    """
    批量保存种子案例到数据库
    
    参数:
        cases: 种子案例列表
    
    返回:
        成功保存的数量
    """
    if not supabase:
        print("❌ Supabase 未初始化")
        return 0
    
    saved_count = 0
    
    for case in cases:
        try:
            insert_data = {
                'time': case.get('Time', '未知'),
                'region': case.get('Region', '未知'),
                'characters': case.get('Characters', '未知'),
                'event': case.get('Event', '未知'),
                'process': case.get('Process', '未知'),
                'result': case.get('Result', '未知'),
                'source_url': case.get('Source_URL', ''),
                'created_at': case.get('Created_at', datetime.now().isoformat()),
                # 新字段
                'line_of_business': case.get('line_of_business'),
                'fraud_type': case.get('fraud_type'),
                'modus_operandi': case.get('modus_operandi'),
                'red_flags': case.get('red_flags'),
                'investigative_tips': case.get('investigative_tips'),
                'underwriting_advice': case.get('underwriting_advice'),
                'is_seed_case': case.get('is_seed_case', True),
                'last_shown_at': case.get('last_shown_at'),
            }
            
            result = supabase.table('fraud_cases').insert(insert_data).execute()
            
            if result.data:
                saved_count += 1
                print(f"✅ 保存种子案例: {case.get('Event', '未知')}")
            else:
                print(f"⚠️ 保存失败: {case.get('Event', '未知')}")
        
        except Exception as e:
            print(f"❌ 保存失败 {case.get('Event', '未知')}: {str(e)}")
            continue
    
    return saved_count


# ==================== 主流程 ====================

def main():
    """主函数：提取并构建50个种子案例库"""
    print("=" * 70)
    print("🌱 GIFIA - 种子案例库提取器")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 检查依赖
    if not DOCX_AVAILABLE:
        print("\n❌ 错误: python-docx 未安装")
        print("请运行: pip install python-docx")
        return
    
    # 检查 API Key
    if not GEMINI_API_KEY:
        print("❌ 错误: GEMINI_API_KEY 未设置")
        return
    
    if not supabase:
        print("❌ 错误: Supabase 未配置")
        return
    
    # 1. 从报告中提取案例
    print("\n" + "=" * 70)
    print("📚 步骤1: 从研究报告中提取案例")
    print("=" * 70)
    
    report_files = [
        "全球医疗保险反欺诈深度研究报告.docx",
        "全球寿险欺诈深度研究报告.docx",
        "全球重大疾病保险欺诈生态研究.docx",
        "全球长期定期寿险产品深度研究报告.docx",
    ]
    
    # 转换为绝对路径
    base_dir = "/Users/tigerli/Desktop/全球反保险欺诈联盟"
    report_files = [os.path.join(base_dir, f) for f in report_files]
    
    extracted_cases = extract_cases_from_reports(report_files)
    
    # 2. 转换为种子案例格式
    print(f"\n📋 步骤2: 转换案例格式（共 {len(extracted_cases)} 个）")
    seed_cases = []
    for case in extracted_cases:
        seed_case = convert_to_seed_case_format(case)
        seed_cases.append(seed_case)
    
    # 3. 如果不足50个，外部补充
    target_count = 50
    if len(seed_cases) < target_count:
        print(f"\n🔍 步骤3: 外部搜索补充案例（当前 {len(seed_cases)}/{target_count}）")
        
        keywords = [
            "Upcoding",
            "Unbundling",
            "Shadow Patients",
            "Pseudocide",
            "Incontestability Clause",
            "DMERx fraud",
            "medical insurance fraud case",
            "life insurance fraud case",
            "critical illness fraud",
        ]
        
        additional_cases = search_additional_cases(keywords, target_count - len(seed_cases))
        # TODO: 对 additional_cases 进行深度分析（调用 deep_research_flow）
        # 暂时跳过，等待用户确认
    
    # 4. 生成预览清单
    print(f"\n📊 步骤4: 生成预览清单（共 {len(seed_cases)} 个案例）")
    preview_file = "seed_cases_preview.json"
    with open(preview_file, 'w', encoding='utf-8') as f:
        json.dump(seed_cases, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 预览清单已保存到: {preview_file}")
    print(f"\n📋 案例预览（前10个）:")
    for i, case in enumerate(seed_cases[:10], 1):
        print(f"   {i}. {case.get('Event', '未知')} - {case.get('Region', '未知')}")
    
    print(f"\n{'='*70}")
    print("⏸️  请检查预览清单，确认后运行以下命令入库：")
    print("   python3 seed_cases_extractor.py --import")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if "--import" in sys.argv:
        # 导入模式：从预览文件读取并入库
        print("=" * 70)
        print("📥 导入模式：从预览文件读取并入库")
        print("=" * 70)
        
        preview_file = "seed_cases_preview.json"
        if not os.path.exists(preview_file):
            print(f"❌ 预览文件不存在: {preview_file}")
            print("请先运行提取模式生成预览清单")
            sys.exit(1)
        
        with open(preview_file, 'r', encoding='utf-8') as f:
            seed_cases = json.load(f)
        
        print(f"📋 从预览文件读取 {len(seed_cases)} 个案例")
        
        # 转换为标准格式
        formatted_cases = []
        for case in seed_cases:
            formatted_case = convert_to_seed_case_format(case)
            formatted_cases.append(formatted_case)
        
        # 保存到数据库
        print(f"\n💾 开始批量保存到数据库...")
        saved_count = save_seed_cases_to_db(formatted_cases)
        
        print(f"\n{'='*70}")
        print(f"✅ 导入完成：成功保存 {saved_count}/{len(formatted_cases)} 个种子案例")
        print("=" * 70)
    else:
        # 提取模式：生成预览清单
        main()
