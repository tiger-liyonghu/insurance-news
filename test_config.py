"""
配置测试脚本
运行此脚本可以验证你的 API Key 和配置是否正确
"""

import os
import sys

def test_tavily_api():
    """测试 Tavily API"""
    try:
        from tavily import TavilyClient
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            print("❌ TAVILY_API_KEY 未设置")
            return False
        client = TavilyClient(api_key=api_key)
        response = client.search(query="test", max_results=1)
        print("✅ Tavily API 连接成功")
        return True
    except Exception as e:
        print(f"❌ Tavily API 测试失败: {str(e)}")
        return False

def test_gemini_api():
    """测试 Gemini API"""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY 未设置")
            return False
        genai.configure(api_key=api_key)
        # 尝试多个模型名称（按优先级顺序，使用完整模型名称）
        models_to_try = [
            'models/gemini-2.5-flash',
            'models/gemini-2.0-flash',
            'models/gemini-flash-latest',
            'models/gemini-2.5-pro',
            'models/gemini-pro-latest'
        ]
        last_error = None
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                print(f"✅ Gemini API 连接成功 (使用模型: {model_name})")
                return True
            except Exception as e:
                last_error = str(e)
                # 如果是 404 错误，继续尝试下一个模型
                if "404" not in str(e):
                    print(f"⚠️ 模型 {model_name} 测试失败: {str(e)[:100]}")
                continue
        print(f"❌ Gemini API 测试失败: {last_error}")
        print("   💡 提示: 请检查 API Key 是否正确，或访问 https://makersuite.google.com/app/apikey 验证")
        return False
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Gemini API 测试失败: {str(e)}")
        if "importlib.metadata" in str(e) or "packages_distributions" in str(e):
            print("   💡 提示: 这是 Python 3.9 的兼容性问题，但不影响实际使用")
            print("   尝试继续运行 agent.py 看看是否能正常工作")
        return False

def test_supabase():
    """测试 Supabase 连接"""
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print("❌ SUPABASE_URL 或 SUPABASE_KEY 未设置")
            return False
        supabase = create_client(url, key)
        # 尝试查询表是否存在
        result = supabase.table('fraud_cases').select('id').limit(1).execute()
        print("✅ Supabase 连接成功，fraud_cases 表存在")
        return True
    except Exception as e:
        if "relation" in str(e).lower() or "does not exist" in str(e).lower():
            print("⚠️ Supabase 连接成功，但 fraud_cases 表不存在")
            print("   请运行 database.sql 创建表")
        else:
            print(f"❌ Supabase 测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 配置测试脚本")
    print("=" * 60)
    print()
    
    results = []
    
    print("1️⃣ 测试 Tavily API...")
    results.append(("Tavily API", test_tavily_api()))
    print()
    
    print("2️⃣ 测试 Gemini API...")
    results.append(("Gemini API", test_gemini_api()))
    print()
    
    print("3️⃣ 测试 Supabase...")
    results.append(("Supabase", test_supabase()))
    print()
    
    # 汇总结果
    print("=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print()
        print("🎉 所有配置测试通过！可以开始使用系统了。")
        print("   运行: python agent.py 开始抓取案例")
        print("   运行: streamlit run app.py 启动 Web 展示页面")
    else:
        print()
        print("⚠️ 部分配置测试失败，请检查:")
        print("   1. 环境变量是否正确设置")
        print("   2. API Key 是否有效")
        print("   3. 网络连接是否正常")
        print("   4. Supabase 表是否已创建（运行 database.sql）")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
