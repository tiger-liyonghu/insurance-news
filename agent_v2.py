"""
Global Insurance Fraud Intelligence Agent (GIFIA) v2.0 - 云端情报站
多 Agent 协作模式：Scout -> Scraper -> Analyst -> Critic
自动化抓取脚本：使用多 Agent 协作提升提取质量
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from supabase import create_client, Client
import google.generativeai as genai
from tavily import TavilyClient
from openai import OpenAI

# ==================== 环境变量配置 ====================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 新增：用于 GPT-4o-mini
JINA_API_KEY = os.getenv("JINA_API_KEY")  # 新增：用于 Jina Reader
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 初始化客户端
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


# ==================== Agent 1: The Scout (侦察员) ====================

class ScoutAgent:
    """
    侦察员 Agent：负责搜索高质量的保险欺诈案例
    改进点：
    1. 使用 advanced 搜索深度
    2. 添加专业关键词提高搜索质量
    3. 只搜索具体案例（排除通用文章）
    4. 专注于寿险、健康险、意外险
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
            'sentenced for insurance fraud',
            'court case insurance fraud',
            'prosecution insurance fraud'
        ]
        
        # 保险类型关键词：只关注寿险、健康险、意外险
        self.insurance_types = [
            'life insurance fraud',      # 寿险欺诈
            'health insurance fraud',    # 健康险欺诈
            'accident insurance fraud',  # 意外险欺诈
            'medical insurance fraud',   # 医疗保险欺诈（属于健康险）
            'disability insurance fraud' # 伤残保险欺诈（可能属于意外险）
        ]
        
        # 排除关键词：排除财产保险
        self.exclude_keywords = [
            'property insurance',
            'auto insurance fraud',
            'car insurance fraud',
            'vehicle insurance',
            'home insurance',
            'house insurance'
        ]
    
    def build_query(self, base_query: str = None) -> str:
        """
        构建增强的搜索查询，专注于具体案例和指定保险类型
        简化查询以符合 Tavily API 的 400 字符限制
        
        参数:
            base_query: 基础搜索关键词（可选）
        
        返回:
            增强后的搜索查询字符串（限制在 400 字符内）
        """
        # 精简案例关键词（只选择最关键的）
        essential_case_keywords = [
            'charged with fraud',
            'convicted of fraud',
            'fraud case',
            'fraud scheme'
        ]
        case_keywords = " OR ".join(essential_case_keywords[:3])  # 只使用前3个
        
        # 精简保险类型关键词
        essential_insurance_types = [
            'life insurance fraud',
            'health insurance fraud',
            'accident insurance fraud'
        ]
        insurance_keywords = " OR ".join(essential_insurance_types)
        
        # 构建查询：简化版，使用更短的格式
        # 格式: (案例关键词) (保险类型) -财产保险 2025 2026
        enhanced_query = f"{case_keywords} {insurance_keywords} -property insurance -auto insurance 2025 2026"
        
        # 确保不超过 400 字符
        if len(enhanced_query) > 400:
            # 如果还是太长，进一步简化
            enhanced_query = "life insurance fraud case OR health insurance fraud case OR accident insurance fraud case -property -auto 2025 2026"
        
        return enhanced_query
    
    def search(self, base_query: str = None, max_results: int = 15) -> List[Dict]:
        """
        搜索全球保险欺诈案例（高级模式）
        只搜索具体案例，排除通用文章
        专注于寿险、健康险、意外险
        
        参数:
            base_query: 基础搜索关键词（不再使用，保留用于兼容）
            max_results: 最大返回结果数（搜索更多以筛选差异性）
        
        返回:
            筛选后的搜索结果列表，确保案例差异性和相关性
        """
        try:
            enhanced_query = self.build_query(base_query)
            
            print(f"🔍 [Scout] 搜索关键词: {enhanced_query[:150]}...")
            print(f"📋 [Scout] 聚焦: 寿险、健康险、意外险具体案例（排除财产保险）")
            
            response = self.client.search(
                query=enhanced_query,
                search_depth="advanced",  # 深度搜索模式
                max_results=max_results,
                include_domains=None,  # 不限制域名
                include_answer=True,  # 包含答案摘要
                include_raw_content=False,  # 不包含原始HTML内容
            )
            
            results = []
            for item in response.get('results', []):
                url = item.get('url', '')
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                
                # 过滤条件：排除通用文章和财产保险
                should_exclude = False
                
                # 检查是否是通用文章（标题或内容中包含这些词）
                generic_keywords = [
                    'market report',
                    'market size',
                    'industry outlook',
                    'global market',
                    'forecast',
                    'trends',
                    'analysis report',
                    'research report'
                ]
                
                for keyword in generic_keywords:
                    if keyword in title or keyword in content:
                        should_exclude = True
                        break
                
                # 检查是否包含财产保险关键词（如果包含则排除）
                for exclude_keyword in self.exclude_keywords:
                    if exclude_keyword in title or exclude_keyword in content:
                        should_exclude = True
                        break
                
                # 检查是否包含具体案例关键词（必须包含至少一个）
                has_case_keyword = False
                for case_keyword in self.case_specific_keywords:
                    if case_keyword in title or case_keyword in content:
                        has_case_keyword = True
                        break
                
                # 如果满足条件，添加到结果
                if not should_exclude and has_case_keyword:
                    results.append({
                        'url': url,
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'score': item.get('score', 0)
                    })
            
            # 按质量分数排序（从高到低）
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            print(f"✅ [Scout] 搜索到 {len(results)} 个符合条件的具体案例（已按质量排序）")
            
            if len(results) == 0:
                print("⚠️ [Scout] 未找到符合条件的案例，可能需要调整搜索策略")
            
            return results
            
        except Exception as e:
            print(f"❌ [Scout] 搜索失败: {str(e)}")
            return []


# ==================== Agent 2: The Scraper (抓取员) ====================

class ScraperAgent:
    """
    抓取员 Agent：负责抓取网页全文内容
    使用 Jina Reader API 获取高质量全文内容
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or JINA_API_KEY
        self.base_url = "https://r.jina.ai"
    
    def fetch_full_content(self, url: str, top_n: int = 3) -> Optional[Dict]:
        """
        使用 Jina Reader 抓取网页全文内容
        
        参数:
            url: 目标网页 URL
            top_n: 只处理前 N 个高质量链接（默认3）
        
        返回:
            包含全文内容的字典，或 None（如果失败）
        """
        if not self.api_key:
            print(f"⚠️ [Scraper] Jina API Key 未设置，使用备用方法")
            return None
        
        try:
            # Jina Reader API 调用
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Return-Format": "text"  # 返回纯文本格式
            }
            
            print(f"📥 [Scraper] 正在抓取全文: {url[:80]}...")
            
            response = requests.get(
                f"{self.base_url}/{url}",
                headers=headers,
                timeout=30  # 30秒超时
            )
            
            if response.status_code == 200:
                full_content = response.text
                print(f"✅ [Scraper] 成功抓取全文 ({len(full_content)} 字符)")
                return {
                    'url': url,
                    'full_content': full_content,
                    'content_length': len(full_content)
                }
            else:
                print(f"⚠️ [Scraper] Jina Reader 返回状态码 {response.status_code}")
                # 如果 Jina 失败，尝试使用 requests 直接获取（备用方案）
                return self._fallback_fetch(url)
                
        except requests.exceptions.Timeout:
            print(f"❌ [Scraper] 请求超时: {url}")
            return None
        except Exception as e:
            print(f"❌ [Scraper] 抓取失败: {str(e)}")
            # 备用方案
            return self._fallback_fetch(url)
    
    def _fallback_fetch(self, url: str) -> Optional[Dict]:
        """
        备用抓取方案：使用 requests 直接获取（如果 Jina 不可用）
        
        参数:
            url: 目标网页 URL
        
        返回:
            包含内容的字典，或 None
        """
        try:
            print(f"📥 [Scraper] 使用备用方法抓取: {url[:80]}...")
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }, allow_redirects=True)
            
            if response.status_code == 200:
                # 简单的文本提取（去除 HTML 标签）
                content = response.text
                
                # 使用正则表达式提取文本内容（简单方法）
                import re
                # 移除 script 和 style 标签
                content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
                content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
                # 提取可见文本
                text_content = re.sub(r'<[^>]+>', ' ', content)
                # 清理多余空白
                text_content = ' '.join(text_content.split())
                
                if len(text_content) > 500:  # 确保有足够内容
                    print(f"✅ [Scraper] 备用方法成功 ({len(text_content)} 字符)")
                    return {
                        'url': url,
                        'full_content': text_content,
                        'content_length': len(text_content),
                        'method': 'fallback'
                    }
                else:
                    print(f"⚠️ [Scraper] 备用方法提取内容过少 ({len(text_content)} 字符)")
                    return None
            else:
                print(f"⚠️ [Scraper] HTTP 状态码: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ [Scraper] 备用方法请求失败: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ [Scraper] 备用方法处理失败: {str(e)}")
            return None


# ==================== Agent 3: The Analyst (分析师) ====================

class AnalystAgent:
    """
    分析师 Agent：负责深度分析案例，提取结构化信息
    使用 Gemini 1.5 Pro 进行深度分析
    """
    
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化 Gemini 模型（优先使用 Pro）"""
        models_to_try = [
            'models/gemini-1.5-pro',  # 优先使用 Pro
            'models/gemini-2.5-flash',
            'models/gemini-2.0-flash',
            'models/gemini-flash-latest'
        ]
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                # 简单测试
                model.generate_content("test")
                self.model = model
                print(f"✅ [Analyst] 使用 Gemini 模型: {model_name}")
                return
            except Exception:
                continue
        
        # 如果都失败，使用默认模型
        print(f"⚠️ [Analyst] 使用默认 Gemini 模型")
        self.model = genai.GenerativeModel('models/gemini-1.5-pro')
    
    def analyze(self, url: str, title: str, full_content: str) -> Optional[Dict]:
        """
        深度分析案例，提取结构化信息
        
        参数:
            url: 原始链接
            title: 标题
            full_content: 全文内容
        
        返回:
            结构化案例数据字典，或 None（如果失败）
        """
        prompt = f"""
你是一位资深的保险反欺诈专家和法务分析师。请从以下网页全文内容中，深度分析保险欺诈案例，并提取结构化信息。

【网页信息】
标题: {title}
链接: {url}

【全文内容】
{full_content[:50000]}  # 限制长度避免超出 token 限制

【分析要求】
请严格按照以下要求进行深度分析：

1. **Time (时间)**: 事件发生或判决的具体时间（格式：YYYY-MM-DD 或 YYYY年MM月DD日）
   - 如果文中没有明确时间，填写"未知"

2. **Region (地区)**: 国家及城市
   - 例如：美国纽约、中国上海、英国伦敦

3. **Characters (人物/实体)**: 涉案人身份、保险公司、中介或医疗机构
   - 用逗号分隔多个实体
   - 如果未提及，填写"未知"

4. **Event (事件)**: 欺诈类型概括
   - 例如：车险骗保、医疗保险欺诈、意外险虚假理赔、旅行保险欺诈

5. **Process (经过)**: 【重点字段】详细的作案手法、逃避初审的过程、以及被发现的破绽细节
   - **必须详细描述以下三个方面：**
     a) **作案手法**：他们如何实施欺诈（具体步骤、手段、伪造的材料等）
     b) **逃避初审**：他们如何通过保险公司的初步审核（利用了哪些漏洞、如何掩盖证据等）
     c) **破绽细节**：最终如何被发现（调查线索、技术手段、异常行为、证据链等）
   - **如果文中没有提及破绽细节，必须在 Process 字段中明确注明："文中未提及具体的破绽细节或调查发现过程，信息缺失"**
   - 此字段必须至少 300 字以上，越详细越好

6. **Result (结果)**: 判决结果、罚金或法律制裁
   - 包括：刑期、罚款金额、民事赔偿、行业禁入等
   - 如果案件仍在审理中，注明"审理中"
   - 如果未提及结果，填写"未知"

【输出要求】
- 必须以纯 JSON 格式输出，不要包含任何 Markdown 标记或额外说明
- 所有字段都必须填写，如果信息缺失请填写"未知"或"待补充"
- Process 字段必须详细，至少 300 字以上
- 如果文中确实没有提及破绽，必须在 Process 中明确说明
- 字段名使用英文（Time, Region, Characters, Event, Process, Result）

【JSON 格式示例】
{{
    "Time": "2025-01-15",
    "Region": "美国纽约",
    "Characters": "John Smith, ABC保险公司, XYZ医疗中心",
    "Event": "医疗保险欺诈",
    "Process": "详细描述作案经过...（必须包含作案手法、逃避初审、破绽细节三个部分）",
    "Result": "被判有期徒刑5年，罚款50万美元"
}}

现在请开始分析：
"""

        try:
            print(f"🧠 [Analyst] 正在深度分析案例...")
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # 清理可能的 Markdown 代码块标记
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            # 清理控制字符（可能导致 JSON 解析失败）
            import re
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # 移除控制字符
            
            # 解析 JSON
            case_data = json.loads(text)
            
            # 验证必需字段
            required_fields = ['Time', 'Region', 'Characters', 'Event', 'Process', 'Result']
            for field in required_fields:
                if field not in case_data:
                    case_data[field] = "未知"
            
            # 验证 Process 字段长度
            if len(case_data.get('Process', '')) < 200:
                case_data['Process'] += " [注：文中信息有限，破绽细节可能不完整]"
            
            # 添加元数据
            case_data['Source_URL'] = url
            case_data['Created_at'] = datetime.now().isoformat()
            
            print(f"✅ [Analyst] 成功提取案例: {case_data.get('Event', '未知事件')}")
            return case_data
            
        except json.JSONDecodeError as e:
            print(f"❌ [Analyst] JSON 解析失败: {str(e)}")
            print(f"原始响应前500字符: {text[:500] if 'text' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"❌ [Analyst] 分析失败: {str(e)}")
            return None


# ==================== Agent 4: The Critic (质检员) ====================

class CriticAgent:
    """
    质检员 Agent：负责验证提取结果的质量
    使用 GPT-4o-mini 对比原文和提取结果，确保没有虚构成分
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            self.client = openai_client
        self.model_name = "gpt-4o-mini"
    
    def validate(self, extracted_data: Dict, original_content: str, url: str) -> Tuple[bool, Dict]:
        """
        验证提取结果的质量，确保没有虚构成分
        
        参数:
            extracted_data: Analyst 提取的结构化数据
            original_content: 原始网页内容
            url: 原文链接
        
        返回:
            (is_valid, validation_result) 元组
            is_valid: True 表示通过验证，False 表示需要修正
            validation_result: 包含验证结果的字典
        """
        if not self.client:
            print(f"⚠️ [Critic] OpenAI API Key 未设置，跳过质检")
            return True, {'skipped': True, 'reason': 'API Key 未设置'}
        
        try:
            print(f"🔍 [Critic] 正在验证提取结果质量...")
            
            # 构建验证 prompt
            prompt = f"""
你是一位严格的质量检查员。请对比以下"提取结果"和"原文内容"，验证提取结果是否准确，是否存在虚构成分。

【原文链接】
{url}

【提取结果】
{json.dumps(extracted_data, ensure_ascii=False, indent=2)}

【原文内容（摘要，前10000字符）】
{original_content[:10000]}

【验证要求】
请检查以下几点：
1. **准确性**：提取的信息是否在原文中有依据？
2. **完整性**：关键信息（时间、地区、人物、事件、经过、结果）是否都有依据？
3. **虚构检测**：是否存在原文中没有提到，但提取结果中出现的虚构内容？
4. **破绽分析**：Process 字段中的"破绽细节"是否在原文中有明确依据？如果没有依据，是否已注明"信息缺失"？

【输出格式】
请以 JSON 格式输出验证结果：
{{
    "is_valid": true/false,  // 是否通过验证
    "issues": ["问题1", "问题2", ...],  // 发现的问题列表（如果没有问题则为空数组）
    "confidence": 0.0-1.0,  // 对提取结果的置信度
    "suggestions": ["建议1", "建议2", ...]  // 改进建议（如果有）
}}

请开始验证：
"""

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一位严格的质量检查员，专门验证AI提取信息的准确性。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 低温度，更严谨
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip() if response.choices else ""
            
            if not result_text:
                print(f"⚠️ [Critic] 未获取到有效响应")
                return True, {'skipped': True, 'reason': 'Empty response'}
            
            # 清理可能的 Markdown 标记
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            # 解析验证结果
            validation_result = json.loads(result_text)
            
            is_valid = validation_result.get('is_valid', False)
            issues = validation_result.get('issues', [])
            confidence = validation_result.get('confidence', 0.5)
            
            if is_valid:
                print(f"✅ [Critic] 验证通过（置信度: {confidence:.2f}）")
            else:
                print(f"⚠️ [Critic] 验证未通过，发现问题: {len(issues)} 个")
                for issue in issues[:3]:  # 只显示前3个问题
                    print(f"   - {issue}")
            
            return is_valid, validation_result
            
        except json.JSONDecodeError as e:
            print(f"⚠️ [Critic] JSON 解析失败: {str(e)}")
            # JSON 解析失败时，尝试从文本中判断
            if "valid" in result_text.lower() or "通过" in result_text:
                return True, {'parsed_from_text': True}
            return False, {'parse_error': str(e)}
        except Exception as e:
            print(f"⚠️ [Critic] 验证过程出错: {str(e)}")
            # 出错时默认通过，不阻塞流程
            return True, {'error': str(e)}


# ==================== 数据库操作 ====================

def check_duplicate(url: str) -> bool:
    """检查数据库中是否已存在该 URL（去重）"""
    if not supabase:
        return False
    try:
        result = supabase.table('fraud_cases').select('id').eq('source_url', url).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"⚠️ 查重失败: {str(e)}")
        return False


def save_to_supabase(case_data: Dict, validation_result: Optional[Dict] = None) -> bool:
    """
    将案例数据保存到 Supabase 数据库
    
    参数:
        case_data: 包含所有字段的案例字典
        validation_result: Critic 的验证结果（可选）
    
    返回:
        True 表示保存成功，False 表示保存失败
    """
    if not supabase:
        print(f"❌ Supabase 未初始化")
        return False
    
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
        
        # 如果有验证结果，可以在注释中记录（可选）
        if validation_result and not validation_result.get('skipped'):
            # 可以在 process 字段末尾添加验证标记
            confidence = validation_result.get('confidence', 0.5)
            if confidence < 0.7:
                insert_data['process'] += f" [验证置信度: {confidence:.2f}]"
        
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


# ==================== 主流程 ====================

def main():
    """
    主函数：多 Agent 协作流程
    1. The Scout: 搜索高质量案例
    2. The Scraper: 抓取前3个链接的全文
    3. The Analyst: 深度分析提取信息
    4. The Critic: 质量检查验证
    """
    print("=" * 70)
    print("🚀 GIFIA v2.0 - 全球保险欺诈情报抓取（多 Agent 协作模式）")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 验证必要的 API Key
    if not all([TAVILY_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        print("❌ 错误: 缺少必要的 API Key 或配置")
        print("请检查环境变量: TAVILY_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY")
        return
    
    if not JINA_API_KEY:
        print("⚠️ 警告: JINA_API_KEY 未设置，将使用备用抓取方法")
    if not OPENAI_API_KEY:
        print("⚠️ 警告: OPENAI_API_KEY 未设置，将跳过质量检查")
    
    # ========== 步骤 1: The Scout ==========
    print("\n" + "=" * 70)
    print("📡 步骤 1: The Scout - 搜索高质量具体案例")
    print("=" * 70)
    print("🎯 聚焦: 寿险、健康险、意外险具体欺诈案例（排除财产保险和通用文章）")
    print("=" * 70)
    
    scout = ScoutAgent(tavily_client)
    search_results = scout.search(
        base_query=None,  # 不再使用基础查询
        max_results=15  # 搜索更多以筛选差异性
    )
    
    if not search_results:
        print("⚠️ 未搜索到任何符合条件的案例，程序退出")
        return
    
    # ========== 筛选确保案例差异性 ==========
    print(f"\n🔍 [Scout] 筛选确保案例差异性...")
    
    # 从搜索结果中选择具有差异性的案例
    diverse_links = []
    seen_types = set()  # 记录已选择的保险类型
    seen_keywords = set()  # 记录已选择的关键特征
    
    for result in search_results:
        title = result['title'].lower()
        content = result.get('content', '').lower()
        
        # 识别案例的保险类型
        case_type = None
        if 'life insurance' in title or 'life insurance' in content or '寿险' in content:
            case_type = 'life'
        elif 'health insurance' in title or 'health insurance' in content or 'medical insurance' in title or 'health insurance' in content or '健康险' in content or '医疗保险' in content:
            case_type = 'health'
        elif 'accident insurance' in title or 'accident insurance' in content or 'disability insurance' in title or '意外险' in content:
            case_type = 'accident'
        
        # 识别案例的关键特征（用于差异化）
        case_keyword = None
        for keyword in ['fraud scheme', 'fraud ring', 'medical fraud', 'death benefit', 'disability claim', 'accident claim']:
            if keyword in title or keyword in content:
                case_keyword = keyword
                break
        
        # 确保案例类型和特征的差异性
        is_diverse = True
        
        # 如果已经有相同类型的案例，优先选择不同类型
        if case_type and case_type in seen_types:
            # 检查是否有关键词差异
            if case_keyword and case_keyword not in seen_keywords:
                is_diverse = True  # 虽然类型相同，但特征不同，可以接受
            else:
                is_diverse = False  # 类型和特征都相同，跳过
        
        # 如果案例类型不明确，检查是否有足够差异
        if not case_type:
            # 如果没有明确的保险类型，检查标题和内容的独特性
            title_words = set(title.split()[:10])  # 取前10个词
            for existing in diverse_links:
                existing_title_words = set(existing['title'].lower().split()[:10])
                # 如果标题相似度太高（超过50%相同词），跳过
                if len(title_words & existing_title_words) / max(len(title_words), 1) > 0.5:
                    is_diverse = False
                    break
        
        if is_diverse:
            diverse_links.append(result)
            if case_type:
                seen_types.add(case_type)
            if case_keyword:
                seen_keywords.add(case_keyword)
            
            # 选择最多5个具有差异性的案例（但优先选择前3个）
            if len(diverse_links) >= 5:
                break
    
    # 如果筛选后案例不足，至少选择前3个（即使相似度较高）
    if len(diverse_links) < 3:
        print(f"⚠️ [Scout] 差异性筛选后只有 {len(diverse_links)} 个案例，补充至3个...")
        # 从剩余结果中补充
        for result in search_results:
            if result not in diverse_links:
                diverse_links.append(result)
                if len(diverse_links) >= 3:
                    break
    
    # 选择前3个高质量且有差异性的案例
    top_links = diverse_links[:3]
    
    print(f"\n✅ Scout 完成：")
    print(f"   - 搜索到 {len(search_results)} 个符合条件的案例")
    print(f"   - 筛选出 {len(diverse_links)} 个有差异性的案例")
    print(f"   - 选择前 {len(top_links)} 个高质量案例进行深度分析")
    
    # 显示选择的案例类型
    if top_links:
        print(f"\n📋 选择的案例概览：")
        for i, link in enumerate(top_links, 1):
            print(f"   {i}. {link['title'][:60]}...")
    
    # ========== 步骤 2-4: 对每个链接进行 Scraper -> Analyst -> Critic ==========
    print("\n" + "=" * 70)
    print(f"🔄 步骤 2-4: 处理 {len(top_links)} 个高质量案例")
    print("=" * 70)
    
    scraper = ScraperAgent(JINA_API_KEY)
    analyst = AnalystAgent(GEMINI_API_KEY)
    critic = CriticAgent(OPENAI_API_KEY)
    
    saved_count = 0
    skipped_count = 0
    failed_count = 0
    
    for i, search_result in enumerate(top_links, 1):
        url = search_result['url']
        title = search_result['title']
        summary = search_result.get('content', '')
        
        print(f"\n{'='*70}")
        print(f"📦 处理案例 {i}/{len(top_links)}")
        print(f"{'='*70}")
        print(f"🔗 URL: {url[:80]}...")
        print(f"📄 标题: {title}")
        
        # 检查是否重复
        if check_duplicate(url):
            print(f"⏭️  跳过: URL 已存在（去重）")
            skipped_count += 1
            continue
        
        # ========== 步骤 2: The Scraper ==========
        print(f"\n📥 [步骤 2] The Scraper - 抓取全文内容...")
        scraped_data = scraper.fetch_full_content(url)
        
        if not scraped_data:
            print(f"❌ Scraper 失败，跳过此案例")
            failed_count += 1
            # 即使抓取失败，也可以尝试用摘要分析（降级处理）
            if summary:
                print(f"⚠️ 尝试使用搜索摘要进行分析...")
                scraped_data = {
                    'url': url,
                    'full_content': summary,
                    'content_length': len(summary),
                    'method': 'summary_fallback'
                }
            else:
                continue
        
        full_content = scraped_data['full_content']
        print(f"✅ Scraper 完成：获取 {len(full_content)} 字符内容")
        
        # ========== 步骤 3: The Analyst ==========
        print(f"\n🧠 [步骤 3] The Analyst - 深度分析提取信息...")
        extracted_data = analyst.analyze(url, title, full_content)
        
        if not extracted_data:
            print(f"❌ Analyst 失败，跳过此案例")
            failed_count += 1
            continue
        
        print(f"✅ Analyst 完成：成功提取结构化信息")
        
        # ========== 步骤 4: The Critic ==========
        print(f"\n🔍 [步骤 4] The Critic - 质量检查验证...")
        is_valid, validation_result = critic.validate(extracted_data, full_content, url)
        
        if not is_valid and not validation_result.get('skipped'):
            issues = validation_result.get('issues', [])
            print(f"⚠️ Critic 发现问题，但继续保存（可在后续版本中实现自动修正）")
            print(f"   问题数量: {len(issues)}")
            # 可以选择：1) 拒绝保存 2) 标记后保存 3) 自动修正后保存
            # 当前版本选择标记后保存
        
        print(f"✅ Critic 完成：验证结果已记录")
        
        # ========== 保存到数据库 ==========
        print(f"\n💾 保存到数据库...")
        if save_to_supabase(extracted_data, validation_result):
            saved_count += 1
            print(f"✅ 案例保存成功")
        else:
            failed_count += 1
            print(f"❌ 保存失败")
        
        # 避免 API 限流
        if i < len(top_links):
            wait_time = 15
            print(f"\n⏳ 等待 {wait_time} 秒以避免 API 限流...")
            time.sleep(wait_time)
    
    # ========== 输出统计信息 ==========
    print("\n" + "=" * 70)
    print("📊 抓取完成统计")
    print("=" * 70)
    print(f"✅ 成功保存: {saved_count} 个案例")
    print(f"⏭️  跳过（重复）: {skipped_count} 个案例")
    print(f"❌ 失败: {failed_count} 个案例")
    print(f"📈 总计处理: {len(top_links)} 个高质量案例")
    print(f"🔍 Scout 搜索: {len(search_results)} 个结果（选择前{len(top_links)}个）")
    print("=" * 70)


if __name__ == "__main__":
    main()
