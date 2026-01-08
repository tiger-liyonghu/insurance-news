#!/usr/bin/env python3
"""
GitHub Actions 环境诊断脚本
用于检查所有依赖和配置是否正确
"""

import os
import sys

def check_environment():
    """检查环境变量"""
    print("=" * 70)
    print("🔍 GitHub Actions 环境诊断")
    print("=" * 70)
    
    errors = []
    warnings = []
    
    # 检查必需的 API Keys
    required_keys = {
        'TAVILY_API_KEY': 'Tavily API',
        'GEMINI_API_KEY': 'Gemini API',
        'SUPABASE_URL': 'Supabase URL',
        'SUPABASE_KEY': 'Supabase Key',
    }
    
    print("\n📋 检查环境变量:")
    for key, name in required_keys.items():
        value = os.getenv(key)
        if value:
            print(f"  ✅ {key}: 已设置 ({value[:10]}...)")
        else:
            print(f"  ❌ {key}: 未设置")
            errors.append(f"缺少 {name} ({key})")
    
    # 检查可选的 API Keys
    optional_keys = {
        'DEEPSEEK_API_KEY': 'DeepSeek API (可选)',
    }
    
    for key, name in optional_keys.items():
        value = os.getenv(key)
        if value:
            print(f"  ✅ {key}: 已设置 ({value[:10]}...)")
        else:
            print(f"  ⚠️  {key}: 未设置（可选）")
            warnings.append(f"{name} 未设置（Failover 将不可用）")
    
    # 检查 Python 版本
    print(f"\n🐍 Python 版本: {sys.version}")
    if sys.version_info < (3, 10):
        warnings.append(f"Python 版本 {sys.version_info.major}.{sys.version_info.minor} 可能不兼容（推荐 3.10+）")
    
    # 检查依赖包
    print("\n📦 检查依赖包:")
    required_packages = {
        'tavily': 'tavily-python',
        'supabase': 'supabase',
        'google.generativeai': 'google-generativeai',
        'openai': 'openai',
        'requests': 'requests',
    }
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✅ {package}: 已安装")
        except ImportError:
            print(f"  ❌ {package}: 未安装")
            errors.append(f"缺少依赖包: {package}")
    
    # 测试导入 agent_v4_living_scout（不初始化客户端）
    print("\n📄 检查脚本文件:")
    try:
        # 临时移除环境变量，避免导入时初始化失败
        import importlib
        import sys
        
        # 保存原始环境变量
        original_env = {}
        for key in ['TAVILY_API_KEY', 'GEMINI_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']:
            original_env[key] = os.environ.get(key)
        
        # 尝试导入（即使 API key 无效也应该能导入）
        import agent_v4_living_scout
        print("  ✅ agent_v4_living_scout.py: 可以导入")
        
        # 恢复环境变量
        for key, value in original_env.items():
            if value:
                os.environ[key] = value
                
    except Exception as e:
        print(f"  ❌ agent_v4_living_scout.py: 导入失败 - {str(e)}")
        errors.append(f"脚本导入失败: {str(e)}")
    
    # 测试基本功能
    print("\n🧪 测试基本功能:")
    
    # 测试 Tavily
    if os.getenv('TAVILY_API_KEY'):
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
            print("  ✅ Tavily 客户端: 可以初始化")
        except Exception as e:
            print(f"  ❌ Tavily 客户端: 初始化失败 - {str(e)}")
            errors.append(f"Tavily 初始化失败: {str(e)}")
    
    # 测试 Gemini
    if os.getenv('GEMINI_API_KEY'):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            print("  ✅ Gemini 客户端: 可以配置")
        except Exception as e:
            print(f"  ❌ Gemini 客户端: 配置失败 - {str(e)}")
            errors.append(f"Gemini 配置失败: {str(e)}")
    
    # 测试 Supabase
    if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
        try:
            from supabase import create_client
            client = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_KEY')
            )
            # 尝试一个简单查询来验证
            try:
                result = client.table('fraud_cases').select('id').limit(1).execute()
                print("  ✅ Supabase 客户端: 可以初始化并连接")
            except Exception as e:
                error_msg = str(e).lower()
                if 'invalid' in error_msg or '401' in error_msg or '403' in error_msg:
                    print(f"  ⚠️  Supabase API Key 可能无效: {str(e)[:80]}")
                    warnings.append("Supabase API Key 可能无效，请检查 Secrets")
                else:
                    print(f"  ⚠️  Supabase 连接测试失败: {str(e)[:80]}")
                    warnings.append(f"Supabase 连接问题: {str(e)[:80]}")
        except Exception as e:
            print(f"  ❌ Supabase 客户端: 初始化失败 - {str(e)[:80]}")
            errors.append(f"Supabase 初始化失败: {str(e)[:80]}")
    
    # 总结
    print("\n" + "=" * 70)
    if errors:
        print("❌ 发现以下错误:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print("\n⚠️  请修复以上错误后重试")
        return 1
    elif warnings:
        print("⚠️  发现以下警告:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print("\n✅ 基本配置正确，但建议修复警告")
        print("💡 警告不会阻止脚本运行，可以继续执行")
        return 0  # 警告不阻止执行
    else:
        print("✅ 所有检查通过！环境配置正确")
        return 0

if __name__ == "__main__":
    exit_code = check_environment()
    sys.exit(exit_code)
