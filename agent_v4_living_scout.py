"""
GIFIA v4.0 - The Living Scout (24/7 全球自动侦察系统)
递归扫描与热点抓取：自动提取外部引用链接，监控热点案例
"""

import os
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse
import requests
from supabase import create_client, Client
import google.generativeai as genai
from tavily import TavilyClient
from openai import OpenAI

# ==================== 环境变量配置 ====================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 初始化客户端
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
genai.configure(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# 监控白名单（.org 和 .gov 域名）
monitored_domains: Set[str] = set()

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
                print("[Gemini] 正在分析...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = (response.text or "").strip()
                if text:
                    return text
            except Exception as e:
                last_err = str(e)
                if any(k in str(e).lower() for k in ["quota", "rate", "429", "exceeded", "limit"]):
                    print("⚠️ Gemini 限额，切换至 DeepSeek...")
                    break
                continue
        if last_err and not any(k in last_err.lower() for k in ["quota", "rate", "429", "exceeded", "limit"]):
            print(f"⚠️ Gemini 异常: {last_err[:120]}，切换至 DeepSeek...")
    except Exception as e:
        print(f"⚠️ Gemini 初始化失败: {str(e)}，切换至 DeepSeek...")

    # 2) 尝试 DeepSeek
    try:
        if not DEEPSEEK_API_KEY:
            print("❌ DeepSeek 未配置")
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
        print(f"❌ DeepSeek 失败: {str(e)}")
        return None


# ==================== 递归扫描：提取外部引用链接 ====================

def extract_external_links(content: str, base_url: str) -> List[str]:
    """
    从内容中提取外部引用链接
    如果是 .org 或 .gov 域名，加入监控白名单
    """
    links = []
    
    # 提取所有 URL
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    found_urls = re.findall(url_pattern, content)
    
    for url in found_urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 检查是否是 .org 或 .gov 域名
            if domain.endswith('.org') or domain.endswith('.gov'):
                links.append(url)
                monitored_domains.add(domain)
                print(f"   ✅ 发现监控域名: {domain}")
        except:
            continue
    
    return links


def load_monitored_domains_from_db() -> Set[str]:
    """从数据库加载已监控的域名"""
    if not supabase:
        return set()
    
    try:
        # 从已保存的案例中提取域名
        result = supabase.table('fraud_cases').select('source_url').limit(1000).execute()
        domains = set()
        
        for row in result.data:
            url = row.get('source_url', '')
            if url:
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    if domain.endswith('.org') or domain.endswith('.gov'):
                        domains.add(domain)
                except:
                    continue
        
        return domains
    except Exception as e:
        print(f"⚠️ 加载监控域名失败: {str(e)}")
        return set()


# ==================== 热点抓取：News 模式搜索 ====================

def search_hotspot_cases() -> List[Dict]:
    """
    使用 Tavily News 模式搜索热点案例
    每30分钟执行一次，发现突发高关注度案例
    """
    if not tavily_client:
        return []
    
    try:
        print("🔥 [Hotspot] 正在搜索热点案例...")
        
        # 热点关键词
        hotspot_keywords = [
            "systemic insurance fraud",
            "massive insurance fraud scheme",
            "insurance fraud corruption",
            "widespread insurance fraud",
            "insurance fraud scandal",
        ]
        
        all_results = []
        
        for keyword in hotspot_keywords:
            try:
                response = tavily_client.search(
                    query=keyword,
                    search_depth="news",  # 使用 news 模式
                    max_results=5,
                    include_answer=True,
                )
                
                for item in response.get('results', []):
                    # 检查关注度（基于分数和时间）
                    score = item.get('score', 0)
                    if score > 0.7:  # 高关注度阈值
                        all_results.append({
                            'url': item.get('url', ''),
                            'title': item.get('title', ''),
                            'content': item.get('content', ''),
                            'score': score,
                            'is_hotspot': True,
                        })
            except Exception as e:
                print(f"⚠️ 热点搜索失败 {keyword}: {str(e)}")
                continue
        
        print(f"✅ [Hotspot] 发现 {len(all_results)} 个热点案例")
        return all_results
        
    except Exception as e:
        print(f"❌ [Hotspot] 热点搜索失败: {str(e)}")
        return []


# ==================== 常规搜索 ====================

def search_fraud_cases(query: str = "Global insurance fraud case 2025 2026", max_results: int = 10) -> List[Dict]:
    """使用 Tavily API 搜索全球保险欺诈案例"""
    if not tavily_client:
        return []
    
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
            include_raw_content=False,
        )
        
        results = []
        for item in response.get('results', []):
            results.append({
                'url': item.get('url', ''),
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'score': item.get('score', 0),
                'is_hotspot': False,
            })
        
        print(f"✅ 搜索到 {len(results)} 个结果")
        return results
    except Exception as e:
        print(f"❌ Tavily 搜索失败: {str(e)}")
        return []


# ==================== 案例提取 ====================

def extract_case_info(url: str, title: str, content: str) -> Optional[Dict]:
    """
    提取案例信息（使用5维度结构化格式）
    """
    prompt = f"""
你是一位全球寿险与健康险反欺诈专家（SIU 资深调查员）。请从以下网页信息中提取保险欺诈案例，并按照专业简报格式输出。

网页标题: {title}
网页链接: {url}
网页内容摘要:
{content}

【分析任务】
请严格按照以下【简报格式】输出，所有内容必须用中文填写：

1. **Time (时间)**: 事件发生或判决的具体时间（格式：YYYY-MM-DD）
2. **Region (地区)**: 国家及城市
3. **Characters (人物/实体)**: 涉案人身份、保险公司、中介或医疗机构
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
- Process 字段必须包含5个标题的详细内容，至少 500 字
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
        case_data['Source_URL'] = url
        case_data['Created_at'] = datetime.now().isoformat()
        
        return case_data
        
    except Exception as e:
        print(f"❌ 提取失败: {str(e)}")
        return None


# ==================== 递归扫描：处理外部链接 ====================

def process_external_links(case_content: str, base_url: str) -> List[Dict]:
    """
    从案例内容中提取外部链接，如果是监控域名则深度抓取
    """
    external_links = extract_external_links(case_content, base_url)
    
    if not external_links:
        return []
    
    print(f"🔗 [Recursive] 发现 {len(external_links)} 个外部链接")
    
    new_cases = []
    for link in external_links[:5]:  # 限制最多处理5个
        try:
            # 检查是否已存在
            if check_duplicate(link):
                continue
            
            # 抓取内容
            response = requests.get(link, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                # 简单提取文本
                content = response.text[:5000]  # 限制长度
                title = link.split('/')[-1]
                
                # 提取案例信息
                case_data = extract_case_info(link, title, content)
                if case_data:
                    new_cases.append(case_data)
                    print(f"   ✅ 从外部链接提取案例: {case_data.get('Event', '未知')}")
        except Exception as e:
            print(f"   ⚠️ 处理外部链接失败 {link}: {str(e)}")
            continue
    
    return new_cases


# ==================== 数据库操作 ====================

def check_duplicate(url: str) -> bool:
    """检查是否已存在"""
    if not supabase:
        return False
    try:
        result = supabase.table('fraud_cases').select('id').eq('source_url', url).execute()
        return len(result.data) > 0
    except:
        return False


def save_to_supabase(case_data: Dict, source: str = 'auto_scout') -> bool:
    """保存到数据库"""
    if not supabase:
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
            'created_at': case_data.get('Created_at', datetime.now().isoformat()),
            'source': source,  # 标记来源
        }
        
        result = supabase.table('fraud_cases').insert(insert_data).execute()
        
        if result.data:
            print(f"✅ 保存成功: {insert_data['event']}")
            return True
        return False
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")
        return False


# ==================== 主流程 ====================

def main():
    """主函数：24/7 自动侦察"""
    print("=" * 70)
    print("🌐 GIFIA v4.0 - The Living Scout (24/7 全球自动侦察)")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 验证配置
    missing_keys = []
    if not TAVILY_API_KEY:
        missing_keys.append("TAVILY_API_KEY")
    if not GEMINI_API_KEY:
        missing_keys.append("GEMINI_API_KEY")
    if not SUPABASE_URL:
        missing_keys.append("SUPABASE_URL")
    if not SUPABASE_KEY:
        missing_keys.append("SUPABASE_KEY")
    
    if missing_keys:
        print(f"❌ 错误: 缺少必要的 API Key: {', '.join(missing_keys)}")
        import sys
        sys.exit(1)
    
    # 加载监控域名
    global monitored_domains
    monitored_domains = load_monitored_domains_from_db()
    print(f"📋 已加载 {len(monitored_domains)} 个监控域名")
    
    saved_count = 0
    skipped_count = 0
    failed_count = 0
    
    # 1. 热点搜索（每30分钟）
    print("\n" + "=" * 70)
    print("🔥 步骤1: 热点案例搜索（News 模式）")
    print("=" * 70)
    
    hotspot_cases = search_hotspot_cases()
    for case in hotspot_cases:
        if check_duplicate(case['url']):
            skipped_count += 1
            continue
        
        case_data = extract_case_info(case['url'], case['title'], case['content'])
        if case_data:
            if save_to_supabase(case_data, source='hotspot'):
                saved_count += 1
                
                # 递归扫描外部链接
                external_cases = process_external_links(case['content'], case['url'])
                for ext_case in external_cases:
                    if save_to_supabase(ext_case, source='recursive'):
                        saved_count += 1
        else:
            failed_count += 1
    
    # 2. 常规搜索
    print("\n" + "=" * 70)
    print("📡 步骤2: 常规案例搜索")
    print("=" * 70)
    
    search_results = search_fraud_cases(max_results=5)
    for result in search_results:
        if check_duplicate(result['url']):
            skipped_count += 1
            continue
        
        case_data = extract_case_info(result['url'], result['title'], result['content'])
        if case_data:
            if save_to_supabase(case_data, source='auto_scout'):
                saved_count += 1
                
                # 递归扫描外部链接
                external_cases = process_external_links(result['content'], result['url'])
                for ext_case in external_cases:
                    if save_to_supabase(ext_case, source='recursive'):
                        saved_count += 1
        else:
            failed_count += 1
    
    # 输出统计
    print("\n" + "=" * 70)
    print("📊 侦察完成统计")
    print("=" * 70)
    print(f"✅ 成功保存: {saved_count} 个案例")
    print(f"⏭️  跳过（重复）: {skipped_count} 个案例")
    print(f"❌ 失败: {failed_count} 个案例")
    print(f"📋 监控域名: {len(monitored_domains)} 个")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
