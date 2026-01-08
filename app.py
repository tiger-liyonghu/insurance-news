"""
GIFIA v2.0 - 全球反保险欺诈联盟云端情报站
现代科技风看板 - 多智能体协作系统展示
"""

import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime
import re

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="GIFIA | 全球保险欺诈情报库",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 自定义 CSS 样式 ====================

st.markdown("""
<style>
    /* ===== 全局样式重置 ===== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* ===== 主题色彩变量 ===== */
    :root {
        --primary-blue: #0052CC;
        --dark-gray: #1A1C1E;
        --light-gray: #F8F9FA;
        --border-color: #E1E4E8;
        --shadow: 0 2px 8px rgba(0, 82, 204, 0.1);
    }
    
    /* ===== Sticky Header 样式 ===== */
    .main-header {
        background: linear-gradient(135deg, #0052CC 0%, #1A1C1E 100%);
        padding: 1.5rem 2rem;
        margin: -2rem -2rem 2rem -2rem;
        border-radius: 0;
        box-shadow: 0 4px 12px rgba(0, 82, 204, 0.2);
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .header-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .status-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: white;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #00D9FF;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* ===== 数据概览卡片样式 ===== */
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 82, 204, 0.1);
        border: 1px solid #E1E4E8;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
    }
    
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 82, 204, 0.15);
    }
    
    .stats-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        color: #666;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stats-value {
        color: #0052CC;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* ===== 情报卡片样式 ===== */
    .intelligence-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 82, 204, 0.1);
        border: 1px solid #E1E4E8;
        margin-bottom: 1.5rem;
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .intelligence-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 82, 204, 0.15);
    }
    
    .card-header {
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid #E1E4E8;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, #F8F9FA 0%, white 100%);
    }
    
    .card-region {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        color: #1A1C1E;
        font-size: 1rem;
    }
    
    .region-flag {
        font-size: 1.2rem;
    }
    
    .card-tag {
        background: #0052CC;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .card-body {
        padding: 1.5rem;
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1A1C1E;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    .card-meta {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem;
        background: #F8F9FA;
        border-radius: 8px;
    }
    
    .meta-icon {
        font-size: 1.2rem;
    }
    
    .meta-label {
        font-size: 0.75rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .meta-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1A1C1E;
        margin-top: 0.2rem;
    }
    
    /* ===== Expander 深度内容区样式 ===== */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #0052CC 0%, #1A7BF5 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .streamlit-expanderContent {
        background: #E8F4FD !important;
        padding: 1.5rem !important;
        border-radius: 0 0 12px 12px !important;
        border: 1px solid #B3D9FF !important;
        line-height: 1.8 !important;
    }
    
    /* ===== 响应式设计 ===== */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .status-badge {
            margin-top: 1rem;
        }
        
        .card-meta {
            grid-template-columns: 1fr;
        }
        
        .stats-card {
            margin-bottom: 1rem;
        }
    }
    
    /* ===== 隐藏 Streamlit 默认元素 ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== 环境变量和数据库初始化 ====================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@st.cache_resource
def init_supabase():
    """初始化 Supabase 连接（使用缓存避免重复连接）"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("⚠️ 错误: 缺少 Supabase 配置 (SUPABASE_URL, SUPABASE_KEY)")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# ==================== 数据获取函数 ====================

@st.cache_data(ttl=300)  # 缓存5分钟
def fetch_latest_cases(limit: int = 6) -> list:
    """
    从 Supabase 获取最新的案例（按创建时间倒序）
    
    参数:
        limit: 返回案例数量限制
    
    返回:
        案例列表
    """
    try:
        result = supabase.table('fraud_cases')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        st.error(f"❌ 获取数据失败: {str(e)}")
        return []


@st.cache_data(ttl=600)  # 缓存10分钟
def fetch_all_cases() -> list:
    """获取所有案例（用于统计）"""
    try:
        result = supabase.table('fraud_cases').select('*').order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        return []


def format_datetime(dt_str: str) -> str:
    """格式化日期时间字符串"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y年%m月%d日 %H:%M')
    except:
        return dt_str


def format_datetime_short(dt_str: str) -> str:
    """格式化日期时间为简短格式"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        delta = now - dt
        
        if delta.days == 0:
            if delta.seconds < 3600:
                return f"{delta.seconds // 60}分钟前"
            else:
                return f"{delta.seconds // 3600}小时前"
        elif delta.days < 7:
            return f"{delta.days}天前"
        else:
            return dt.strftime('%m月%d日')
    except:
        return dt_str


def get_region_emoji(region: str) -> str:
    """根据地区返回国旗 Emoji"""
    region_lower = region.lower()
    
    emoji_map = {
        '美国': '🇺🇸', 'usa': '🇺🇸', 'united states': '🇺🇸',
        '中国': '🇨🇳', 'china': '🇨🇳',
        '英国': '🇬🇧', 'uk': '🇬🇧', 'united kingdom': '🇬🇧',
        '日本': '🇯🇵', 'japan': '🇯🇵',
        '德国': '🇩🇪', 'germany': '🇩🇪',
        '法国': '🇫🇷', 'france': '🇫🇷',
        '加拿大': '🇨🇦', 'canada': '🇨🇦',
        '澳大利亚': '🇦🇺', 'australia': '🇦🇺',
        '新加坡': '🇸🇬', 'singapore': '🇸🇬',
        '香港': '🇭🇰', 'hong kong': '🇭🇰',
        '台湾': '🇹🇼', 'taiwan': '🇹🇼',
    }
    
    for key, emoji in emoji_map.items():
        if key in region_lower:
            return emoji
    
    return '🌍'  # 默认地球图标


def get_unique_regions_count(all_cases: list) -> int:
    """统计不同国家/地区的数量"""
    regions = set()
    for case in all_cases:
        region = case.get('region', '未知')
        if region != '未知':
            regions.add(region)
    return len(regions)


def extract_amount(result_text: str) -> str:
    """从判决结果中提取金额"""
    if not result_text or result_text == '未知' or result_text == '暂无结果':
        return '未知'
    
    # 匹配常见金额格式
    patterns = [
        r'[\$£€¥]\s*(\d+(?:[.,]\d{3})*(?:\.[0-9]{2})?)\s*(?:万|million|million|亿|billion)?',
        r'(\d+(?:[.,]\d{3})*(?:\.[0-9]{2})?)\s*(?:美元|元|万|million|million|亿|billion)',
        r'罚款[：:]\s*(\d+(?:[.,]\d{3})*(?:\.[0-9]{2})?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, result_text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return '未知'


# ==================== 主页面渲染 ====================

def main():
    """主页面渲染函数"""
    
    # ========== Sticky Header ==========
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div>
                <h1 class="header-title">🛡️ GIFIA | 全球保险欺诈情报库</h1>
                <p class="header-subtitle">基于多智能体协作的全球理赔风险监控系统，由 Yonghu LI 主理。</p>
            </div>
            <div class="status-badge">
                <div class="status-dot"></div>
                <span>System Live (Every 60m)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== 数据加载 ==========
    with st.spinner("🔄 正在加载最新情报数据..."):
        all_cases = fetch_all_cases()
        cases = fetch_latest_cases(limit=6)
    
    # ========== 数据概览卡片 ==========
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unique_regions = get_unique_regions_count(all_cases)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-icon">🌍</div>
            <div class="stats-label">监控国家</div>
            <div class="stats-value">{unique_regions}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_cases = len(all_cases)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-icon">📊</div>
            <div class="stats-label">累计案例</div>
            <div class="stats-value">{total_cases}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        last_update = format_datetime_short(cases[0].get('created_at', '')) if cases else '无数据'
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-icon">🕐</div>
            <div class="stats-label">最近更新</div>
            <div class="stats-value" style="font-size: 1.5rem;">{last_update}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== 情报卡片流 ==========
    if not cases:
        st.warning("⚠️ 数据库中暂无案例，请先运行 agent_v2.py 抓取数据")
        st.info("💡 提示: 运行 `python3 agent_v2.py` 开始抓取案例")
        return
    
    st.markdown("## 📰 最新情报（最近6个案例）")
    st.markdown("---")
    
    for idx, case in enumerate(cases):
        region = case.get('region', '未知')
        event = case.get('event', '未知事件')
        time_str = case.get('time', '未知时间')
        characters = case.get('characters', '未知')
        result = case.get('result', '暂无结果')
        process = case.get('process', '暂无详细经过')
        source_url = case.get('source_url', '')
        created_at = case.get('created_at', '')
        
        # 提取金额
        amount = extract_amount(result)
        
        # 地区 Emoji
        region_emoji = get_region_emoji(region)
        
        # 卡片
        st.markdown(f"""
        <div class="intelligence-card">
            <div class="card-header">
                <div class="card-region">
                    <span class="region-flag">{region_emoji}</span>
                    <span>{region}</span>
                </div>
                <div class="card-tag">{event}</div>
            </div>
            <div class="card-body">
                <div class="card-title">{event}</div>
                <div class="card-meta">
                    <div class="meta-item">
                        <div>
                            <div class="meta-icon">👥</div>
                            <div class="meta-label">涉案方</div>
                            <div class="meta-value">{characters[:40]}{'...' if len(characters) > 40 else ''}</div>
                        </div>
                    </div>
                    <div class="meta-item">
                        <div>
                            <div class="meta-icon">💰</div>
                            <div class="meta-label">涉案金额</div>
                            <div class="meta-value">{amount}</div>
                        </div>
                    </div>
                    <div class="meta-item">
                        <div>
                            <div class="meta-icon">⏰</div>
                            <div class="meta-label">发生时间</div>
                            <div class="meta-value">{time_str}</div>
                        </div>
                    </div>
                    <div class="meta-item">
                        <div>
                            <div class="meta-icon">⚖️</div>
                            <div class="meta-label">判决结果</div>
                            <div class="meta-value">{result[:30]}{'...' if len(result) > 30 else ''}</div>
                        </div>
                    </div>
                </div>
        """, unsafe_allow_html=True)
        
        # 深度内容区（使用 Expander）
        with st.expander("🔍 点击展开：作案经过与破绽深度分析", expanded=(idx == 0)):
            st.markdown(f"""
            <div style="line-height: 1.8; color: #1A1C1E;">
            {process.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            if source_url:
                st.markdown(f"🔗 [查看原文链接]({source_url})", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== 底部信息 ==========
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0; font-size: 0.9rem;">
        <p><strong>🛡️ GIFIA - 全球反保险欺诈联盟</strong> | 云端情报站</p>
        <p>数据每小时自动更新 | Powered by Tavily AI + Gemini 1.5 Pro + Supabase</p>
        <p>© 2025 - 反欺诈专家 Yonghu LI</p>
    </div>
    """, unsafe_allow_html=True)


# ==================== 用户上传页面 ====================

def submission_page():
    """用户提交情报页面"""
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div>
                <h1 class="header-title">📤 提交情报</h1>
                <p class="header-subtitle">上传理赔卷宗或案例文档，经过专家审核后入库</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 导入用户上传模块
    try:
        from user_submission_module import validate_submission, deidentify_pii, extract_case_from_submission
        from supabase import create_client
        
        supabase_client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    except ImportError:
        st.error("❌ 用户上传模块未找到")
        return
    
    # 文件上传
    st.markdown("### 📄 上传文件")
    st.markdown("支持格式：PDF、DOCX（理赔卷宗或案例文档）")
    
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['pdf', 'docx'],
        help="上传理赔卷宗或案例文档"
    )
    
    if uploaded_file:
        # 读取文件内容
        file_content = None
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                file_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
            except ImportError:
                st.error("❌ 需要安装 PyPDF2: pip install PyPDF2")
                return
            except Exception as e:
                st.error(f"❌ PDF 读取失败: {str(e)}")
                return
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                from docx import Document
                doc = Document(uploaded_file)
                file_content = "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                st.error("❌ 需要安装 python-docx: pip install python-docx")
                return
            except Exception as e:
                st.error(f"❌ DOCX 读取失败: {str(e)}")
                return
        
        if not file_content:
            st.warning("⚠️ 未能从文件中提取文本内容")
            return
        
        st.success(f"✅ 文件读取成功（{len(file_content)} 字符）")
        
        # 专家准入闸门
        with st.spinner("🔍 正在验证内容（专家准入闸门）..."):
            is_valid, validation_result = validate_submission(file_content)
        
        if not is_valid:
            st.error("❌ 验证失败：内容不符合保险欺诈/逆选择/滥用定义")
            st.json(validation_result)
            return
        
        st.success("✅ 验证通过")
        
        fraud_type = validation_result.get('fraud_type', '未知')
        line_of_business = validation_result.get('line_of_business', '未知')
        confidence = validation_result.get('confidence', 0)
        
        st.info(f"""
        **验证结果**：
        - 欺诈类型：{fraud_type}
        - 险种：{line_of_business}
        - 置信度：{confidence:.2%}
        """)
        
        # 自动脱敏
        with st.spinner("🔒 正在自动脱敏（识别并遮蔽 PII 信息）..."):
            deidentified_content, pii_found = deidentify_pii(file_content)
        
        st.success("✅ 脱敏完成")
        
        if pii_found:
            st.warning(f"⚠️ 发现并已遮蔽 {sum(len(v) for v in pii_found.values())} 条 PII 信息")
            with st.expander("查看脱敏详情"):
                st.json(pii_found)
        
        # 结构化提取
        with st.spinner("📊 正在提取结构化案例信息..."):
            case_data = extract_case_from_submission(deidentified_content, line_of_business)
        
        if not case_data:
            st.error("❌ 案例提取失败")
            return
        
        st.success("✅ 案例提取成功")
        
        # 预览
        st.markdown("### 📋 提取结果预览")
        st.json(case_data)
        
        # 确认提交
        if st.button("✅ 确认提交到数据库", type="primary"):
            try:
                insert_data = {
                    'time': case_data.get('Time', '未知'),
                    'region': case_data.get('Region', '未知'),
                    'characters': case_data.get('Characters', '未知'),
                    'event': case_data.get('Event', '未知'),
                    'process': case_data.get('Process', '未知'),
                    'result': case_data.get('Result', '未知'),
                    'source_url': case_data.get('Source_URL', ''),
                    'created_at': case_data.get('Created_at'),
                    'source': 'user_submission',
                    'line_of_business': line_of_business,
                    'fraud_type': fraud_type,
                }
                
                result = supabase_client.table('fraud_cases').insert(insert_data).execute()
                
                if result.data:
                    st.success("🎉 提交成功！案例已入库")
                    st.balloons()
                else:
                    st.error("❌ 提交失败")
            except Exception as e:
                st.error(f"❌ 提交失败: {str(e)}")


# ==================== 页面路由 ====================

if __name__ == "__main__":
    # 简单的页面路由
    page = st.sidebar.selectbox("选择页面", ["🏠 首页", "📤 提交情报"])
    
    if page == "🏠 首页":
        main()
    elif page == "📤 提交情报":
        submission_page()
