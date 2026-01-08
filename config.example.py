"""
配置文件示例 v2.0 - 多 Agent 协作模式
请复制此文件为 config.py 并填入你的 API Key
或者在环境变量中设置这些值（推荐方式）
"""

import os

# ==================== 必需配置 ====================

# Tavily API Key (The Scout - 搜索)
# 申请地址: https://tavily.com/
TAVILY_API_KEY = "your_tavily_api_key_here"

# Google Gemini API Key (The Analyst - 深度分析)
# 申请地址: https://makersuite.google.com/app/apikey
# 推荐使用: Gemini 1.5 Pro（更好的长文本处理能力）
GEMINI_API_KEY = "your_gemini_api_key_here"

# Supabase 配置 (数据库存储)
# 申请地址: https://supabase.com/
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your_supabase_anon_key_here"

# ==================== v3.0 必需配置 ====================

# Firecrawl API Key (The Researcher - 深度抓取)
# 申请地址: https://firecrawl.dev/
# 说明: 用于深度抓取 Markdown 格式全文（必需）
FIRECRAWL_API_KEY = "your_firecrawl_api_key_here"

# ==================== Failover 备份引擎配置 ====================

# DeepSeek API Key (备份引擎 - 当 Gemini 限额时自动切换)
# 申请地址: https://platform.deepseek.com/
# 说明: 当 Gemini 达到限额或出错时，自动切换到 DeepSeek 作为备份引擎
# Base URL: https://api.deepseek.com
# 模型: deepseek-chat
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

# ==================== 可选配置（v2.0 兼容） ====================

# Jina Reader API Key (The Scraper - 全文抓取)
# 申请地址: https://jina.ai/
# 说明: v2.0 版本使用，v3.0 使用 Firecrawl 替代
JINA_API_KEY = "your_jina_api_key_here"

# OpenAI API Key (The Critic - 质量检查)
# 申请地址: https://platform.openai.com/api-keys
# 说明: v2.0 版本使用，v3.0 使用 Validator Agent 替代
OPENAI_API_KEY = "your_openai_api_key_here"

# ==================== 环境变量设置（推荐） ====================
# 在命令行中执行（Linux/macOS）：
# export TAVILY_API_KEY="your_key"
# export GEMINI_API_KEY="your_key"
# export SUPABASE_URL="your_url"
# export SUPABASE_KEY="your_key"
# export JINA_API_KEY="your_key"  # 可选
# export OPENAI_API_KEY="your_key"  # 可选

# Windows (PowerShell):
# $env:TAVILY_API_KEY="your_key"
# $env:GEMINI_API_KEY="your_key"
# $env:SUPABASE_URL="your_url"
# $env:SUPABASE_KEY="your_key"
# $env:JINA_API_KEY="your_key"  # 可选
# $env:OPENAI_API_KEY="your_key"  # 可选
