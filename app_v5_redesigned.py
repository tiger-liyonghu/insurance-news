"""
GIFIA v5.0 - 重构版前端（参考 Chainalysis & CAIF 设计理念）
- 多维过滤系统（实时联动）
- CAIF 简报风格卡片
- Top 10 数据流控
- 24/7 Agent 状态指示灯
"""

import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
import re

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="GIFIA v5.0 | 全球保险欺诈情报库",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 环境变量配置 ====================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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
        --border-radius: 12px;
        --accent-red: #DC3545;
        --success-green: #28A745;
        --warning-yellow: #FFC107;
    }
    
    /* ===== Sticky Header ===== */
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
    
    .header-left {
        flex: 1;
    }
    
    .header-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* ===== Agent 状态指示灯 ===== */
    .agent-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        color: white;
    }
    
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    .status-dot.live {
        background: var(--success-green);
        box-shadow: 0 0 10px var(--success-green);
    }
    
    .status-dot.pending {
        background: var(--warning-yellow);
        box-shadow: 0 0 10px var(--warning-yellow);
    }
    
    .status-dot.offline {
        background: #DC3545;
        box-shadow: 0 0 10px #DC3545;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
    }
    
    /* ===== 数据概览卡片 ===== */
    .stats-dashboard {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        text-align: center;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-blue);
    }
    
    /* ===== CAIF 风格案例卡片 ===== */
    .case-card-caif {
        background: white;
        border-radius: var(--border-radius);
        padding: 0;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        transition: transform 0.2s, box-shadow 0.2s;
        overflow: hidden;
    }
    
    .case-card-caif:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 82, 204, 0.15);
    }
    
    .card-header-caif {
        background: linear-gradient(135deg, var(--dark-gray) 0%, #2A2C2E 100%);
        padding: 1rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .card-header-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .card-flag {
        font-size: 1.5rem;
    }
    
    .card-region-name {
        color: white;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .card-business-tag {
        background: var(--primary-blue);
        color: white;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .card-body-caif {
        padding: 1.5rem;
    }
    
    .card-mo-title {
        color: var(--accent-red);
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-mo-content {
        color: var(--dark-gray);
        line-height: 1.8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .expert-insight-container {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 1.25rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-blue);
        margin-top: 1rem;
    }
    
    .expert-insight-label {
        font-weight: 700;
        color: var(--primary-blue);
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .expert-insight-content {
        color: var(--dark-gray);
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    /* ===== 侧边栏样式 ===== */
    .sidebar-section {
        margin-bottom: 2rem;
    }
    
    .sidebar-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--dark-gray);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* ===== 响应式设计 ===== */
    @media (max-width: 768px) {
        .stats-dashboard {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== 数据库连接 ====================

@st.cache_resource
def init_supabase():
    """初始化 Supabase 连接"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("⚠️ 错误: 缺少 Supabase 配置")
        st.info("💡 请在 Streamlit Cloud Settings → Secrets 中配置 SUPABASE_URL 和 SUPABASE_KEY")
        st.stop()
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Supabase 连接失败: {str(e)}")
        st.info("💡 请检查 Secrets 中的 SUPABASE_URL 和 SUPABASE_KEY 是否正确")
        st.stop()

# 延迟初始化，避免在导入时就失败
supabase: Client = None

def get_supabase():
    """获取 Supabase 客户端（延迟初始化）"""
    global supabase
    if supabase is None:
        supabase = init_supabase()
    return supabase

# ==================== 工具函数 ====================

def get_region_name(region_iso: str) -> str:
    """根据 ISO 代码获取地区名称"""
    region_map = {
        'US': '美国', 'GB': '英国', 'CN': '中国',
        'TH': '泰国', 'SG': '新加坡', 'MY': '马来西亚',
        'AE': '阿联酋', 'SA': '沙特阿拉伯',
    }
    return region_map.get(region_iso, region_iso)


def get_region_emoji(region_iso: str) -> str:
    """根据 ISO 代码获取国旗 Emoji"""
    emoji_map = {
        'US': '🇺🇸', 'GB': '🇬🇧', 'CN': '🇨🇳',
        'TH': '🇹🇭', 'SG': '🇸🇬', 'MY': '🇲🇾',
        'AE': '🇦🇪', 'SA': '🇸🇦',
    }
    return emoji_map.get(region_iso, '🌍')


def get_agent_status() -> dict:
    """
    获取 Agent 运行状态
    检查最近一次数据更新时间
    """
    try:
        db = get_supabase()
        if not db:
            return {'status': 'offline', 'text': 'Agent Offline', 'emoji': '🔴'}
        
        result = db.table('fraud_cases')\
            .select('created_at')\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if result.data and len(result.data) > 0:
            last_update_str = result.data[0].get('created_at')
            if last_update_str:
                try:
                    last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
                    now = datetime.now(last_update.tzinfo) if last_update.tzinfo else datetime.now()
                    delta = now - last_update
                    
                    if delta.total_seconds() < 3600:  # 1小时内
                        return {'status': 'live', 'text': 'Agent Live', 'emoji': '🟢'}
                    elif delta.total_seconds() < 7200:  # 2小时内
                        return {'status': 'pending', 'text': 'Agent Pending', 'emoji': '🟡'}
                    else:
                        return {'status': 'offline', 'text': 'Agent Offline', 'emoji': '🔴'}
                except:
                    pass
        
        return {'status': 'offline', 'text': 'Agent Offline', 'emoji': '🔴'}
    except:
        return {'status': 'offline', 'text': 'Agent Offline', 'emoji': '🔴'}


# ==================== 数据获取函数 ====================

@st.cache_data(ttl=300)
def fetch_cases_with_filters(
    region_isos: list = None,
    business_lines: list = None,
    limit: int = 100
) -> list:
    """
    根据筛选条件获取案例（支持多选）
    
    参数:
        region_isos: 地区代码列表（如：['US', 'GB']）
        business_lines: 业务条线列表（如：['寿险', '医疗']）
        limit: 返回数量限制
    
    返回:
        案例列表
    """
    try:
        db = get_supabase()
        if not db:
            return []
        
        query = db.table('fraud_cases').select('*')
        
        # 应用地区筛选（多选）
        if region_isos and len(region_isos) > 0:
            query = query.in_('region_iso', region_isos)
        
        # 应用业务条线筛选（多选）
        if business_lines and len(business_lines) > 0:
            query = query.in_('business_line', business_lines)
        
        # 排序和限制
        result = query.order('created_at', desc=True).limit(limit).execute()
        
        return result.data if result.data else []
    except Exception as e:
        error_msg = str(e)
        # 如果是字段不存在的错误，提供更友好的提示
        if 'does not exist' in error_msg or '42703' in error_msg:
            st.error("❌ 数据库表结构未更新到 v5.0")
            st.info("💡 请在 Supabase SQL Editor 中执行 `migrate_to_v5.sql` 迁移脚本")
        else:
            st.error(f"❌ 获取数据失败: {error_msg}")
        return []


@st.cache_data(ttl=600)
def get_available_filters() -> dict:
    """获取可用的筛选选项"""
    try:
        db = get_supabase()
        if not db:
            return {'regions': [], 'business_lines': []}
        
        result = db.table('fraud_cases').select('region_iso, business_line').execute()
        
        if not result.data:
            return {'regions': [], 'business_lines': []}
        
        regions = sorted(set([c.get('region_iso') for c in result.data if c.get('region_iso')]))
        business_lines = sorted(set([c.get('business_line') for c in result.data if c.get('business_line')]))
        
        return {
            'regions': regions,
            'business_lines': business_lines
        }
    except:
        return {'regions': [], 'business_lines': []}


# ==================== 渲染函数 ====================

def render_caif_card(case: dict, index: int):
    """渲染 CAIF 风格案例卡片"""
    region_iso = case.get('region_iso', '')
    business_line = case.get('business_line', '未知')
    modus_operandi = case.get('modus_operandi', '')
    expert_insight = case.get('expert_insight', '')
    event = case.get('event', '未知事件')
    process = case.get('process', '')
    time_str = case.get('time', '未知时间')
    result = case.get('result', '暂无结果')
    source_url = case.get('source_url', '')
    
    # 如果没有 modus_operandi，尝试从 process 中提取
    if not modus_operandi and process:
        mo_match = re.search(r'【舞弊手法\(MO\)】\s*(.+?)(?=【|$)', process, re.DOTALL)
        if mo_match:
            modus_operandi = mo_match.group(1).strip()[:200]
    
    card_html = f"""
    <div class="case-card-caif">
        <div class="card-header-caif">
            <div class="card-header-left">
                <span class="card-flag">{get_region_emoji(region_iso)}</span>
                <span class="card-region-name">{get_region_name(region_iso)}</span>
            </div>
            <div class="card-business-tag">{business_line}</div>
        </div>
        
        <div class="card-body-caif">
            <div class="card-mo-title">
                <span>🔴</span>
                <span>舞弊手法 (MO)</span>
            </div>
            <div class="card-mo-content">
                {modus_operandi if modus_operandi else '信息缺失'}
            </div>
            
            {f'''
            <div class="expert-insight-container">
                <div class="expert-insight-label">
                    <span>💡</span>
                    <span>专家启示</span>
                </div>
                <div class="expert-insight-content">
                    {expert_insight if expert_insight else '待补充'}
                </div>
            </div>
            ''' if expert_insight else ''}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # 深度内容（使用 Expander）
    with st.expander(f"🔍 点击展开：完整分析（案例 #{index}）", expanded=False):
        st.markdown(f"""
        **事件**: {event}
        
        **时间**: {time_str}
        
        **结果**: {result}
        
        **完整分析**:
        """)
        st.markdown(f"""
        <div style="line-height: 1.8; color: #1A1C1E; white-space: pre-wrap;">
        {process.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        if source_url:
            st.markdown(f"🔗 [查看原文链接]({source_url})", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


# ==================== 主页面 ====================

def main():
    """主页面渲染函数"""
    
    # ========== Sticky Header with Agent Status ==========
    agent_status = get_agent_status()
    status_class = agent_status['status']
    status_text = agent_status['text']
    
    st.markdown(f"""
    <div class="main-header">
        <div class="header-content">
            <div class="header-left">
                <h1 class="header-title">🛡️ GIFIA v5.0 | 全球保险欺诈情报库</h1>
                <p class="header-subtitle">基于多智能体协作的全球理赔风险监控系统，由 Yonghu LI 主理</p>
            </div>
            <div class="agent-status">
                <div class="status-dot {status_class}"></div>
                <span>{status_text} 24/7</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== 侧边栏：多维过滤系统（参考 Chainalysis）==========
    with st.sidebar:
        st.markdown("## 🔍 多维筛选器")
        
        # 获取可用选项
        filters = get_available_filters()
        
        # 全球地区筛选（多选复选框）
        st.markdown("### 🌍 全球地区")
        region_options = ['US', 'GB', 'CN', 'TH', 'SG', 'MY', 'AE', 'SA']
        selected_regions = []
        
        # 全选/全不选
        select_all_regions = st.checkbox("全选", key="select_all_regions", value=False)
        if select_all_regions:
            selected_regions = region_options
        else:
            for region in region_options:
                if st.checkbox(
                    f"{get_region_emoji(region)} {get_region_name(region)}",
                    key=f"region_{region}",
                    value=region in filters['regions']  # 默认选中已有数据的地区
                ):
                    selected_regions.append(region)
        
        st.markdown("---")
        
        # L&H 业务线筛选（多选复选框）
        st.markdown("### 📋 L&H 业务线")
        business_line_options = ['寿险', '医疗', '重疾']
        selected_business_lines = []
        
        select_all_business = st.checkbox("全选", key="select_all_business", value=True)
        if select_all_business:
            selected_business_lines = business_line_options
        else:
            for bl in business_line_options:
                if st.checkbox(bl, key=f"business_{bl}", value=True):
                    selected_business_lines.append(bl)
        
        st.markdown("---")
        
        # 统计信息
        st.markdown("### 📊 统计")
        all_cases = fetch_cases_with_filters()
        filtered_cases = fetch_cases_with_filters(
            region_isos=selected_regions if selected_regions else None,
            business_lines=selected_business_lines if selected_business_lines else None
        )
        
        st.metric("总案例数", len(all_cases))
        st.metric("筛选后", len(filtered_cases))
    
    # ========== 数据加载 ==========
    with st.spinner("🔄 正在加载数据..."):
        cases = fetch_cases_with_filters(
            region_isos=selected_regions if selected_regions else None,
            business_lines=selected_business_lines if selected_business_lines else None,
            limit=100
        )
    
    # ========== Intelligence Dashboard ==========
    st.markdown("## 📊 Intelligence Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unique_regions = len(set([c.get('region_iso') for c in all_cases if c.get('region_iso')]))
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">监控国家</div>
            <div class="stat-value">{unique_regions}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">累计案例</div>
            <div class="stat-value">{len(all_cases)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if all_cases:
            last_update_str = all_cases[0].get('created_at', '')
            try:
                last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
                now = datetime.now(last_update.tzinfo) if last_update.tzinfo else datetime.now()
                delta = now - last_update
                if delta.total_seconds() < 3600:
                    time_text = f"{int(delta.total_seconds() / 60)}分钟前"
                elif delta.total_seconds() < 86400:
                    time_text = f"{int(delta.total_seconds() / 3600)}小时前"
                else:
                    time_text = f"{delta.days}天前"
            except:
                time_text = "未知"
        else:
            time_text = "无数据"
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">最近更新</div>
            <div class="stat-value" style="font-size: 1.5rem;">{time_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== Case Intelligence (Top 10 原则) ==========
    if not cases:
        st.warning("⚠️ 未找到符合条件的案例")
        return
    
    st.markdown(f"## 📰 Case Intelligence (Top 10)")
    st.markdown("---")
    
    # Top 10 完整展示
    top_cases = cases[:10]
    remaining_cases = cases[10:]
    
    for idx, case in enumerate(top_cases, 1):
        render_caif_card(case, idx)
    
    # 其余案例：使用 expander 折叠（参考 Sentry）
    if remaining_cases:
        with st.expander(f"📋 查看更多案例（{len(remaining_cases)} 个）", expanded=False):
            for idx, case in enumerate(remaining_cases, 11):
                render_caif_card(case, idx)
    
    # ========== 底部信息 ==========
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0; font-size: 0.9rem;">
        <p><strong>🛡️ GIFIA v5.0 - 全球反保险欺诈联盟</strong> | 24/7 动态情报防御系统</p>
        <p>数据每30分钟自动更新 | Powered by Tavily AI + Gemini 1.5 Pro + Supabase</p>
        <p>© 2025 - 反欺诈专家 Yonghu LI</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
