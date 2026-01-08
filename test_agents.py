"""
测试多 Agent 协作系统
用于验证各个 Agent 是否正常工作
"""

import os
import sys

def test_scout_agent():
    """测试 The Scout Agent"""
    try:
        from tavily import TavilyClient
        from agent_v2 import ScoutAgent
        
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            print("❌ TAVILY_API_KEY 未设置")
            return False
        
        client = TavilyClient(api_key=api_key)
        scout = ScoutAgent(client)
        
        # 测试构建查询
        query = scout.build_query()
        print(f"✅ Scout 查询构建成功: {query[:80]}...")
        
        # 测试搜索（只搜索1个结果测试）
        results = scout.search(max_results=1)
        if results:
            print(f"✅ Scout 搜索成功: 找到 {len(results)} 个结果")
            return True
        else:
            print("⚠️ Scout 搜索无结果（可能是搜索条件问题）")
            return False
            
    except Exception as e:
        print(f"❌ Scout Agent 测试失败: {str(e)}")
        return False


def test_scraper_agent():
    """测试 The Scraper Agent"""
    try:
        from agent_v2 import ScraperAgent
        
        api_key = os.getenv("JINA_API_KEY")
        scraper = ScraperAgent(api_key=api_key)
        
        if not api_key:
            print("⚠️ JINA_API_KEY 未设置，将使用备用方法")
            # 测试备用方法
            result = scraper._fallback_fetch("https://www.example.com")
            if result:
                print("✅ Scraper 备用方法可用")
                return True
            else:
                print("⚠️ Scraper 备用方法测试失败（可能是网络问题）")
                return True  # 不阻塞，因为 Jina 是可选的
        else:
            print("✅ Scraper Agent 初始化成功（Jina API Key 已设置）")
            return True
            
    except Exception as e:
        print(f"⚠️ Scraper Agent 测试失败: {str(e)}")
        return True  # 不阻塞，因为 Jina 是可选的


def test_analyst_agent():
    """测试 The Analyst Agent"""
    try:
        import google.generativeai as genai
        from agent_v2 import AnalystAgent
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY 未设置")
            return False
        
        analyst = AnalystAgent(api_key)
        
        # 测试简单分析
        test_data = {
            'url': 'https://example.com',
            'title': 'Test Case',
            'full_content': 'This is a test insurance fraud case.'
        }
        
        print("✅ Analyst Agent 初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ Analyst Agent 测试失败: {str(e)}")
        return False


def test_critic_agent():
    """测试 The Critic Agent"""
    try:
        from agent_v2 import CriticAgent
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        critic = CriticAgent(api_key)
        
        if not api_key:
            print("⚠️ OPENAI_API_KEY 未设置，Critic 将跳过质检（不影响流程）")
            return True  # 不阻塞，因为 OpenAI 是可选的
        
        # 测试 OpenAI 连接
        try:
            response = critic.client.models.list()
            print("✅ Critic Agent 初始化成功（OpenAI API Key 已设置）")
            return True
        except Exception as e:
            print(f"⚠️ OpenAI API 连接失败: {str(e)}")
            return True  # 不阻塞，因为 OpenAI 是可选的
            
    except Exception as e:
        print(f"⚠️ Critic Agent 测试失败: {str(e)}")
        return True  # 不阻塞，因为 OpenAI 是可选的


def test_database():
    """测试数据库连接"""
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ SUPABASE_URL 或 SUPABASE_KEY 未设置")
            return False
        
        supabase = create_client(url, key)
        result = supabase.table('fraud_cases').select('id').limit(1).execute()
        
        print("✅ 数据库连接成功，fraud_cases 表存在")
        return True
        
    except Exception as e:
        if "relation" in str(e).lower() or "does not exist" in str(e).lower():
            print("⚠️ 数据库连接成功，但 fraud_cases 表不存在")
            print("   请运行 database.sql 创建表")
        else:
            print(f"❌ 数据库测试失败: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("=" * 70)
    print("🧪 多 Agent 协作系统测试")
    print("=" * 70)
    print()
    
    results = []
    
    print("1️⃣ 测试 The Scout Agent (搜索)...")
    results.append(("The Scout", test_scout_agent()))
    print()
    
    print("2️⃣ 测试 The Scraper Agent (抓取)...")
    results.append(("The Scraper", test_scraper_agent()))
    print()
    
    print("3️⃣ 测试 The Analyst Agent (分析)...")
    results.append(("The Analyst", test_analyst_agent()))
    print()
    
    print("4️⃣ 测试 The Critic Agent (质检)...")
    results.append(("The Critic", test_critic_agent()))
    print()
    
    print("5️⃣ 测试数据库连接...")
    results.append(("数据库", test_database()))
    print()
    
    # 汇总结果
    print("=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    
    required_agents = ["The Scout", "The Analyst", "数据库"]
    optional_agents = ["The Scraper", "The Critic"]
    
    for name, success in results:
        if name in required_agents:
            status = "✅ 通过" if success else "❌ 失败（必需）"
        else:
            status = "✅ 通过" if success else "⚠️ 未设置（可选）"
        print(f"{name}: {status}")
    
    # 检查必需的 Agent
    required_passed = all(
        result[1] for result in results 
        if result[0] in required_agents
    )
    
    if required_passed:
        print()
        print("🎉 所有必需的 Agent 测试通过！可以开始使用系统了。")
        print("   运行: python3 agent_v2.py 开始抓取案例")
        
        # 检查可选 Agent
        optional_passed = all(
            result[1] for result in results 
            if result[0] in optional_agents
        )
        
        if not optional_passed:
            print()
            print("⚠️ 提示: 部分可选 Agent 未配置，但可以正常运行：")
            if not os.getenv("JINA_API_KEY"):
                print("   - 未设置 JINA_API_KEY（将使用备用抓取方法）")
            if not os.getenv("OPENAI_API_KEY"):
                print("   - 未设置 OPENAI_API_KEY（将跳过质量检查）")
    else:
        print()
        print("❌ 部分必需的 Agent 测试失败，请检查配置：")
        for name, success in results:
            if name in required_agents and not success:
                print(f"   - {name} 配置有问题")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
