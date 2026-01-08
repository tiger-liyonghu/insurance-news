"""
Global Insurance Fraud Intelligence Agent (GIFIA) v3.0 - 云端情报站
深度协作模式：Scout -> Researcher -> Analyst -> Validator
自动化抓取脚本：使用 Firecrawl + Gemini 1.5 Pro 深度研究
"""

import os
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from supabase import create_client, Client
import google.generativeai as genai
from tavily import TavilyClient
from openai import OpenAI

# 尝试导入 Firecrawl（兼容不同的导入方式）
try:
    from firecrawl import FirecrawlApp
except ImportError:
    try:
        from firecrawl.firecrawl import FirecrawlApp
    except ImportError:
        try:
            from firecrawl_py import FirecrawlApp
        except ImportError:
            FirecrawlApp = None

# ==================== 环境变量配置 ====================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # 备份引擎：DeepSeek
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")  # 新增：Firecrawl API
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 初始化客户端
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# 初始化 Firecrawl App（如果 API Key 存在）
firecrawl_app = None
if FIRECRAWL_API_KEY and FirecrawlApp:
    try:
        firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    except Exception as e:
        print(f"⚠️ Firecrawl 初始化失败: {str(e)}")
        firecrawl_app = None

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ==================== Agent 1: The Scout (侦察员) ====================

class ScoutAgent:
    """
    侦察员 Agent：负责搜索高质量的保险欺诈案例
    使用 Tavily API 执行高级搜索
    """
    
    def __init__(self, tavily_client: TavilyClient):
        self.client = tavily_client
        
        # 专业关键词：确保找到具体案例而非通用文章
        self.case_specific_keywords = [
            'charged with fraud',
            'convicted of fraud',
            'fraud case',
            'fraud scheme',
            'arrested for insurance fraud',
            'sentenced for insurance fraud'
        ]
        
        # 保险类型关键词：只关注寿险、健康险、意外险
        self.insurance_types = [
            'life insurance fraud',
            'health insurance fraud',
            'accident insurance fraud',
            'medical insurance fraud',
            'disability insurance fraud'
        ]
        
        # 排除关键词：排除财产保险
        self.exclude_keywords = [
            'property insurance',
            'auto insurance fraud',
            'car insurance fraud',
            'vehicle insurance'
        ]
    
    def build_query(self) -> str:
        """构建增强的搜索查询"""
        essential_case_keywords = " OR ".join(self.case_specific_keywords[:3])
        essential_insurance_types = " OR ".join(self.insurance_types[:3])
        enhanced_query = f"{essential_case_keywords} {essential_insurance_types} -property insurance -auto insurance 2025 2026"
        
        if len(enhanced_query) > 400:
            enhanced_query = "life insurance fraud case OR health insurance fraud case OR accident insurance fraud case -property -auto 2025 2026"
        
        return enhanced_query
    
    def search(self, max_results: int = 15) -> List[Dict]:
        """
        搜索全球保险欺诈案例（高级模式）
        
        返回:
            搜索结果列表，按质量分数排序
        """
        try:
            enhanced_query = self.build_query()
            
            print(f"🔍 [Scout] 正在执行高级搜索...")
            print(f"   📋 关键词: {enhanced_query[:120]}...")
            
            response = self.client.search(
                query=enhanced_query,
                search_depth="advanced",  # 高级搜索模式
                max_results=max_results,
                include_domains=None,
                include_answer=True,
                include_raw_content=False,
            )
            
            results = []
            for item in response.get('results', []):
                url = item.get('url', '')
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                
                # 过滤通用文章和财产保险
                should_exclude = False
                generic_keywords = ['market report', 'market size', 'industry outlook', 'forecast', 'trends']
                for keyword in generic_keywords:
                    if keyword in title or keyword in content:
                        should_exclude = True
                        break
                
                for exclude_keyword in self.exclude_keywords:
                    if exclude_keyword in title or exclude_keyword in content:
                        should_exclude = True
                        break
                
                has_case_keyword = any(kw in title or kw in content for kw in self.case_specific_keywords)
                
                if not should_exclude and has_case_keyword:
                    results.append({
                        'url': url,
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'score': item.get('score', 0)
                    })
            
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            print(f"✅ [Scout] 搜索完成：找到 {len(results)} 个符合条件的案例")
            return results
            
        except Exception as e:
            print(f"❌ [Scout] 搜索失败: {str(e)}")
            return []


# ==================== Agent 2: The Researcher (深度抓取员) ====================

class ResearcherAgent:
    """
    深度抓取员 Agent：使用 Firecrawl 抓取 Markdown 格式的全文
    严禁只看摘要，必须获取完整内容
    """
    
    def __init__(self, firecrawl_app: Optional[FirecrawlApp]):
        self.app = firecrawl_app
    
    def scrape_url(self, url: str) -> Optional[Dict]:
        """
        使用 Firecrawl 抓取 URL 的 Markdown 格式全文
        
        参数:
            url: 目标网页 URL
        
        返回:
            包含 Markdown 全文的字典，或 None（如果失败）
        """
        if not self.app:
            print(f"❌ [Researcher] Firecrawl API Key 未设置")
            return None
        
        try:
            print(f"📥 [Researcher] 正在深度扫描: {url[:80]}...")
            print(f"   🔄 调用 Firecrawl 提取 Markdown 全文...")
            
            # 调用 FirecrawlApp 的 scrape 方法
            # Firecrawl 的正确调用方式：app.scrape(url) - 只传 URL
            result = self.app.scrape(url)
            
            # Firecrawl 返回 Document 对象
            if result:
                # 尝试获取 markdown 内容
                markdown_content = None
                
                # 方法1: 直接访问 markdown 属性
                if hasattr(result, 'markdown'):
                    try:
                        markdown_content = result.markdown
                    except:
                        pass
                
                # 方法2: 通过 dict() 方法访问（Firecrawl v2 的方式）
                if not markdown_content and hasattr(result, 'dict'):
                    try:
                        result_dict = result.dict()
                        markdown_content = result_dict.get('markdown', '') or result_dict.get('content', '')
                    except:
                        pass
                
                # 方法3: 如果是字典格式
                if not markdown_content and isinstance(result, dict):
                    markdown_content = result.get('markdown') or result.get('content', '')
                
                # 方法4: 尝试访问 __dict__
                if not markdown_content:
                    try:
                        result_dict = result.__dict__ if hasattr(result, '__dict__') else {}
                        markdown_content = result_dict.get('markdown') or result_dict.get('content', '')
                    except:
                        pass
                
                if markdown_content and len(markdown_content) > 0:
                    content_length = len(markdown_content)
                    
                    print(f"✅ [Researcher] 深度扫描完成: 获取 {content_length} 字符 Markdown 全文")
                    
                    if content_length < 500:
                        print(f"⚠️ [Researcher] 警告: 内容过短 ({content_length} 字符)，可能未完全抓取")
                    
                    # 获取元数据（如果有）
                    metadata = {}
                    if hasattr(result, 'metadata'):
                        metadata = result.metadata if isinstance(result.metadata, dict) else {}
                    elif isinstance(result, dict):
                        metadata = result.get('metadata', {})
                    
                    return {
                        'url': url,
                        'markdown_content': markdown_content,
                        'content_length': content_length,
                        'metadata': metadata
                    }
                else:
                    print(f"❌ [Researcher] 抓取失败: 未返回 Markdown 内容")
                    print(f"   返回结果类型: {type(result)}")
                    if hasattr(result, '__dict__'):
                        print(f"   返回结果属性: {list(result.__dict__.keys())[:5]}")
                    return None
            else:
                print(f"❌ [Researcher] 抓取失败: 返回结果为 None")
                return None
                
        except Exception as e:
            print(f"❌ [Researcher] 深度扫描失败: {str(e)}")
            return None


# ==================== Agent 3: The Analyst (深度分析师) ====================

class AnalystAgent:
    """
    深度分析师 Agent：使用 Gemini 1.5 Pro 深度分析全文
    特别指令：必须挖掘案件中的"破绽细节 (The Red Flag)"
    """
    
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化 Gemini 模型（优先使用 Pro，如果不可用则使用 Flash）"""
        models_to_try = [
            'models/gemini-2.5-flash',  # 优先使用最新 Flash（更稳定）
            'models/gemini-2.0-flash',
            'models/gemini-1.5-pro',  # 如果可用，使用 Pro
            'models/gemini-flash-latest'
        ]
        
        last_error = None
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                # 简单测试调用
                response = model.generate_content("test")
                self.model = model
                print(f"✅ [Analyst] 使用 Gemini 模型: {model_name}")
                return
            except Exception as e:
                last_error = str(e)
                continue
        
        # 如果都失败，使用最新 Flash 作为默认（即使可能失败）
        print(f"⚠️ [Analyst] 无法验证模型，使用默认模型 models/gemini-2.5-flash")
        if last_error:
            print(f"   最后的错误: {last_error[:100]}")
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def analyze(self, url: str, title: str, markdown_content: str) -> Optional[Dict]:
        """
        深度分析案例，提取结构化信息
        特别强调：必须挖掘"破绽细节 (The Red Flag)"
        
        参数:
            url: 原始链接
            title: 标题
            markdown_content: Firecrawl 抓取的 Markdown 全文
        
        返回:
            结构化案例数据字典
        """
        # 限制内容长度，避免超出 token 限制
        max_length = 50000
        if len(markdown_content) > max_length:
            markdown_content = markdown_content[:max_length] + "\n\n[内容已截断...]"
        
        prompt = f"""
你是一位全球寿险与健康险反欺诈专家（SIU 资深调查员）。请从以下网页的完整 Markdown 内容中，深度分析保险欺诈案例，并按照专业简报格式输出结构化摘要。

【网页信息】
标题: {title}
链接: {url}

【完整 Markdown 内容】
{markdown_content}

【分析任务】
请严格按照以下【简报格式】输出结构化摘要，所有内容必须用中文填写：

1. **Time (时间)**: 事件发生或判决的具体时间
   - 格式：YYYY-MM-DD 或 YYYY年MM月DD日
   - 如果文中没有明确时间，填写"未知"

2. **Region (地区)**: 国家及城市
   - 例如：美国纽约、中国上海、英国伦敦
   - 如果未提及，填写"未知"

3. **Characters (人物/实体)**: 涉案人身份、保险公司、中介或医疗机构
   - 用逗号分隔多个实体
   - 如果未提及，填写"未知"

4. **Event (事件)**: 欺诈类型概括
   - 例如：寿险欺诈、健康险欺诈、医疗保险欺诈、意外险虚假理赔

5. **Process (经过)**: 【重点字段】按照 SIU 专业简报格式，严格使用以下5个标题，禁止使用描述性文字，只输出结构化内容：

   **【风险画像】**
   - 投保时间、投保人信息、投保动机、健康状况声明
   - 保险金额、保险类型、保障范围
   - 出险时间、出险间隔（投保后多久出险）、是否在等待期内、是否在犹豫期内
   - 如果文中未提及，标注"信息缺失"
   
   **【舞弊手法(MO)】**
   - 具体欺诈手段（挂床住院、海外假收据、伪造医疗记录、虚假诊断证明、夸大病情、重复理赔等）
   - 使用的技术、工具、文件、记录
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

6. **Result (结果)**: 判决结果、罚金或法律制裁
   - 包括：刑期、罚款金额、民事赔偿、行业禁入等
   - 如果案件仍在审理中，注明"审理中"
   - 如果未提及结果，填写"未知"

【输出要求】
- 必须以纯 JSON 格式输出，不要包含任何 Markdown 标记或额外说明
- 所有字段都必须填写
- Process 字段必须严格使用5个标题：【风险画像】、【舞弊手法(MO)】、【红旗指标(Red Flags)】、【核查手段建议】、【核保/风控启示】
- Process 字段禁止使用描述性文字，只输出结构化内容，至少 600 字以上
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

现在请开始专业分析，**特别关注审计破绽 (Red Flags) 的挖掘**：
"""

        try:
            print(f"🧠 [Analyst] 正在分析卷宗...")
            print(f"   📄 分析内容: {len(markdown_content)} 字符 Markdown 全文")
            print(f"   💡 特别关注：破绽细节 (The Red Flag) 挖掘...")
            
            # 使用 Failover 机制（Gemini 主引擎 + DeepSeek 备份引擎）
            text = self._get_ai_analysis_with_failover(prompt)
            
            if not text:
                print(f"❌ AI 分析失败（主引擎和备份引擎都失败）")
                return None
            
            text = text.strip()
            
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
            case_data = json.loads(text)
            
            # 验证必需字段
            required_fields = ['Time', 'Region', 'Characters', 'Event', 'Process', 'Result']
            for field in required_fields:
                if field not in case_data:
                    case_data[field] = "未知"
            
            # 验证 Process 字段长度
            process = case_data.get('Process', '')
            if len(process) < 400:
                case_data['Process'] += "\n\n[注：提取的内容可能不完整，建议查看原文]"
            
            # 检查是否包含破绽细节
            red_flag_keywords = ['破绽', '发现', '调查', '证据', '异常', 'red flag', 'detection', 'investigation']
            has_red_flag = any(keyword in process.lower() for keyword in red_flag_keywords)
            if not has_red_flag:
                case_data['Process'] += "\n\n⚠️ 注意：文中未详细描述破绽细节或调查发现过程，信息缺失"
            
            # 添加元数据
            case_data['Source_URL'] = url
            case_data['Created_at'] = datetime.now().isoformat()
            
            print(f"✅ [Analyst] 分析完成: {case_data.get('Event', '未知事件')}")
            return case_data
            
        except json.JSONDecodeError as e:
            print(f"❌ [Analyst] JSON 解析失败: {str(e)}")
            print(f"   原始响应前500字符: {text[:500] if 'text' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"❌ [Analyst] 分析失败: {str(e)}")
            return None


# ==================== Agent 4: The Validator (校验员) ====================

class ValidatorAgent:
    """
    校验员 Agent：检查提取结果的完整性
    检查6个维度，如果经过描述太简单，标记为"低质量"并建议重试
    """
    
    def validate(self, extracted_data: Dict) -> Tuple[bool, Dict]:
        """
        校验提取结果的完整性和质量
        
        参数:
            extracted_data: Analyst 提取的结构化数据
        
        返回:
            (is_valid, validation_result) 元组
            is_valid: True 表示通过验证，False 表示低质量
            validation_result: 包含验证结果的字典
        """
        try:
            print(f"🔍 [Validator] 正在校验提取结果质量...")
            
            issues = []
            scores = {}
            
            # 检查6个维度
            required_fields = ['Time', 'Region', 'Characters', 'Event', 'Process', 'Result']
            
            for field in required_fields:
                value = extracted_data.get(field, '')
                
                # 检查字段是否存在且非空
                if not value or value in ['未知', '待补充', '']:
                    issues.append(f"字段 {field} 缺失或为空")
                    scores[field] = 0
                else:
                    scores[field] = 1
            
            # 特别检查 Process 字段的质量
            process = extracted_data.get('Process', '')
            process_score = 0
            process_issues = []
            
            if len(process) < 400:
                process_issues.append(f"Process 字段过短 ({len(process)} 字符，要求至少 400 字符)")
                process_score = 0.3
            elif len(process) < 600:
                process_score = 0.6
            else:
                process_score = 1.0
            
            # 检查是否包含三个关键部分
            required_parts = ['作案', '逃避', '破绽']
            for part in required_parts:
                if part not in process:
                    process_issues.append(f"Process 缺少 '{part}' 部分")
                    process_score = max(0, process_score - 0.2)
            
            # 检查破绽细节
            red_flag_keywords = ['破绽', '发现', '调查', '证据', '异常', 'red flag']
            has_red_flag = any(keyword in process.lower() for keyword in red_flag_keywords)
            if not has_red_flag or '信息缺失' in process:
                process_issues.append("Process 缺少破绽细节 (The Red Flag)")
                process_score = max(0, process_score - 0.3)
            
            if process_issues:
                issues.extend(process_issues)
            
            scores['Process'] = process_score
            
            # 计算总体质量分数
            overall_score = sum(scores.values()) / len(scores)
            
            # 判断是否通过验证（总分 >= 0.7 且 Process >= 0.6）
            is_valid = overall_score >= 0.7 and process_score >= 0.6
            
            validation_result = {
                'is_valid': is_valid,
                'overall_score': overall_score,
                'process_score': process_score,
                'scores': scores,
                'issues': issues,
                'suggestions': []
            }
            
            if not is_valid:
                if process_score < 0.6:
                    validation_result['suggestions'].append("Process 字段质量不足，建议重试下一个链接")
                if overall_score < 0.7:
                    validation_result['suggestions'].append("整体质量不足，建议重新提取")
            
            if is_valid:
                print(f"✅ [Validator] 验证通过 (质量分数: {overall_score:.2f}, Process: {process_score:.2f})")
            else:
                print(f"⚠️ [Validator] 验证未通过 (质量分数: {overall_score:.2f}, Process: {process_score:.2f})")
                print(f"   问题: {len(issues)} 个")
                for issue in issues[:3]:
                    print(f"   - {issue}")
            
            return is_valid, validation_result
            
        except Exception as e:
            print(f"⚠️ [Validator] 验证过程出错: {str(e)}")
            # 出错时默认通过，不阻塞流程
            return True, {'error': str(e), 'is_valid': True}


# ==================== 查重机制 ====================

def calculate_similarity(str1: str, str2: str) -> float:
    """计算两个字符串的相似度（0-1）"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def check_duplicate(url: str, title: str = "") -> Tuple[bool, Optional[str]]:
    """
    检查数据库中是否已存在相似的案例（基于 URL 或标题相似度）
    
    参数:
        url: 案例 URL
        title: 案例标题
    
    返回:
        (is_duplicate, reason) 元组
        is_duplicate: True 表示重复
        reason: 重复原因
    """
    if not supabase:
        return False, None
    
    try:
        # 方法1: 检查 URL 是否完全一致
        result = supabase.table('fraud_cases').select('id, source_url, event').eq('source_url', url).execute()
        if result.data and len(result.data) > 0:
            return True, "URL 完全匹配"
        
        # 方法2: 如果提供了标题，检查标题相似度
        if title:
            all_cases = supabase.table('fraud_cases').select('id, event, source_url').limit(100).execute()
            
            if all_cases.data:
                for existing_case in all_cases.data:
                    existing_title = existing_case.get('event', '')
                    
                    # 计算标题相似度
                    similarity = calculate_similarity(title, existing_title)
                    
                    # 如果相似度超过 85%，认为是重复
                    if similarity > 0.85:
                        return True, f"标题相似度 {similarity:.2%}"
        
        return False, None
        
    except Exception as e:
        print(f"⚠️ 查重失败: {str(e)}")
        return False, None


# ==================== 数据库操作 ====================

def save_to_supabase(case_data: Dict, validation_result: Optional[Dict] = None) -> bool:
    """将案例数据保存到 Supabase 数据库"""
    if not supabase:
        print(f"❌ Supabase 未初始化")
        return False
    
    try:
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
        
        # 如果有验证结果，添加质量分数标记
        if validation_result:
            overall_score = validation_result.get('overall_score', 1.0)
            if overall_score < 1.0:
                insert_data['process'] += f" [质量分数: {overall_score:.2f}]"
        
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


# ==================== 深度研究流程 ====================

def deep_research_flow(search_results: List[Dict], max_cases: int = 3) -> Dict:
    """
    深度研究流程：串联 Scout -> Researcher -> Analyst -> Validator
    
    参数:
        search_results: Scout 搜索的结果列表
        max_cases: 最多处理的案例数量
    
    返回:
        处理结果统计字典
    """
    print("\n" + "=" * 70)
    print("🔄 开始深度研究流程")
    print("=" * 70)
    
    # 初始化各个 Agent
    researcher = ResearcherAgent(firecrawl_app)
    analyst = AnalystAgent(GEMINI_API_KEY)
    validator = ValidatorAgent()
    
    # 选择前 max_cases 个高质量链接
    top_links = search_results[:max_cases]
    
    saved_count = 0
    skipped_count = 0
    failed_count = 0
    retry_count = 0
    
    for i, search_result in enumerate(top_links, 1):
        url = search_result['url']
        title = search_result['title']
        
        print(f"\n{'='*70}")
        print(f"📦 处理案例 {i}/{len(top_links)}")
        print(f"{'='*70}")
        print(f"🔗 URL: {url[:80]}...")
        print(f"📄 标题: {title}")
        
        # 查重检查
        is_duplicate, reason = check_duplicate(url, title)
        if is_duplicate:
            print(f"⏭️  跳过: 重复案例 ({reason})")
            skipped_count += 1
            continue
        
        # ========== Step 1: Researcher Agent ==========
        print(f"\n📥 [Step 1] Researcher Agent - 深度抓取全文...")
        scraped_data = researcher.scrape_url(url)
        
        if not scraped_data:
            print(f"❌ Researcher 失败，跳过此案例")
            failed_count += 1
            continue
        
        markdown_content = scraped_data['markdown_content']
        print(f"✅ Researcher 完成：获取 {scraped_data['content_length']} 字符 Markdown 全文")
        
        # ========== Step 2: Analyst Agent ==========
        print(f"\n🧠 [Step 2] Analyst Agent - 深度分析提取信息...")
        print(f"   💡 特别关注：破绽细节 (The Red Flag) 挖掘...")
        extracted_data = analyst.analyze(url, title, markdown_content)
        
        if not extracted_data:
            print(f"❌ Analyst 失败，跳过此案例")
            failed_count += 1
            continue
        
        print(f"✅ Analyst 完成：成功提取结构化信息")
        
        # ========== Step 3: Validator Agent ==========
        print(f"\n🔍 [Step 3] Validator Agent - 校验提取质量...")
        is_valid, validation_result = validator.validate(extracted_data)
        
        if not is_valid:
            print(f"⚠️ Validator 未通过验证：质量不足")
            
            # 如果是 Process 字段质量不足，标记为重试
            process_score = validation_result.get('process_score', 0)
            if process_score < 0.6:
                print(f"   💡 建议：Process 字段质量不足，可以重试下一个链接")
                retry_count += 1
                # 可以选择：1) 跳过此案例 2) 标记保存但标注低质量
                # 当前策略：标记保存但标注低质量
                print(f"   📝 标记为低质量案例，但仍保存到数据库")
            else:
                failed_count += 1
                continue
        
        # ========== 保存到数据库 ==========
        print(f"\n💾 保存到数据库...")
        if save_to_supabase(extracted_data, validation_result):
            saved_count += 1
            print(f"✅ 案例保存成功")
        else:
            failed_count += 1
        
        # 避免 API 限流
        if i < len(top_links):
            wait_time = 15
            print(f"\n⏳ 等待 {wait_time} 秒以避免 API 限流...")
            time.sleep(wait_time)
    
    return {
        'saved': saved_count,
        'skipped': skipped_count,
        'failed': failed_count,
        'retry': retry_count,
        'total_processed': len(top_links)
    }


# ==================== 主流程 ====================

def main():
    """主函数：深度协作流程"""
    print("=" * 70)
    print("🚀 GIFIA v3.0 - 全球保险欺诈情报抓取（深度协作模式）")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 验证必要的 API Key
    if not all([TAVILY_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        print("❌ 错误: 缺少必要的 API Key 或配置")
        print("请检查环境变量: TAVILY_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY")
        return
    
    if not FIRECRAWL_API_KEY:
        print("❌ 错误: FIRECRAWL_API_KEY 未设置（必需）")
        print("请设置 FIRECRAWL_API_KEY 环境变量")
        return
    
    # ========== Step 1: Scout Agent ==========
    print("\n" + "=" * 70)
    print("📡 Step 1: Scout Agent - 高级搜索")
    print("=" * 70)
    
    scout = ScoutAgent(tavily_client)
    search_results = scout.search(max_results=15)
    
    if not search_results:
        print("⚠️ 未搜索到任何符合条件的案例，程序退出")
        return
    
    # 选择前3个高质量链接进行深度研究
    print(f"\n✅ Scout 完成：选择前 3 个高质量案例进行深度研究")
    
    # ========== Step 2-4: 深度研究流程 ==========
    results = deep_research_flow(search_results, max_cases=3)
    
    # ========== 输出统计信息 ==========
    print("\n" + "=" * 70)
    print("📊 深度研究完成统计")
    print("=" * 70)
    print(f"✅ 成功保存: {results['saved']} 个案例")
    print(f"⏭️  跳过（重复）: {results['skipped']} 个案例")
    print(f"⚠️  低质量重试: {results['retry']} 个案例")
    print(f"❌ 失败: {results['failed']} 个案例")
    print(f"📈 总计处理: {results['total_processed']} 个高质量案例")
    print(f"🔍 Scout 搜索: {len(search_results)} 个结果")
    print("=" * 70)


if __name__ == "__main__":
    main()
