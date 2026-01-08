#!/bin/bash
# GIFIA GitHub 仓库初始化脚本
# 用于快速设置 GitHub 仓库和推送代码

set -e

echo "🚀 GIFIA GitHub 仓库初始化脚本"
echo "================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "agent_v4_living_scout.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查 Git 是否已初始化
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    
    # 创建 .gitignore（如果不存在）
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# 环境变量
.env
config.py

# IDE
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db

# 临时文件
*.log
*.tmp
seed_cases_preview.json
EOF
        echo "✅ 创建 .gitignore"
    fi
    
    # 添加所有文件
    git add .
    git commit -m "Initial commit: GIFIA v4.0"
    echo "✅ Git 仓库已初始化并提交"
else
    echo "✅ Git 仓库已存在"
fi

# 检查远程仓库
if git remote | grep -q "origin"; then
    echo "✅ 远程仓库已配置"
    git remote -v
else
    echo ""
    echo "📝 请提供 GitHub 仓库 URL"
    echo "   例如: https://github.com/你的用户名/gifia.git"
    read -p "GitHub 仓库 URL: " repo_url
    
    if [ -z "$repo_url" ]; then
        echo "❌ 错误: 仓库 URL 不能为空"
        exit 1
    fi
    
    git remote add origin "$repo_url"
    echo "✅ 远程仓库已添加: $repo_url"
fi

# 检查当前分支
current_branch=$(git branch --show-current 2>/dev/null || echo "main")
echo ""
echo "📋 当前分支: $current_branch"

# 询问是否推送
echo ""
read -p "是否现在推送到 GitHub? (y/n): " push_confirm

if [ "$push_confirm" = "y" ] || [ "$push_confirm" = "Y" ]; then
    echo ""
    echo "📤 推送到 GitHub..."
    
    # 添加所有更改
    git add .
    
    # 检查是否有未提交的更改
    if ! git diff --staged --quiet; then
        git commit -m "Update: Add GitHub Actions workflow"
    fi
    
    # 推送
    git push -u origin "$current_branch"
    
    echo ""
    echo "✅ 代码已推送到 GitHub!"
    echo ""
    echo "📋 下一步:"
    echo "   1. 在 GitHub 仓库页面，进入 Settings → Secrets and variables → Actions"
    echo "   2. 添加以下 5 个 Secrets:"
    echo "      - TAVILY_API_KEY"
    echo "      - GEMINI_API_KEY"
    echo "      - DEEPSEEK_API_KEY"
    echo "      - SUPABASE_URL"
    echo "      - SUPABASE_KEY"
    echo "   3. 进入 Actions 标签，手动触发一次测试运行"
    echo ""
    echo "📖 详细指南请查看: GITHUB_ACTIONS_SETUP.md"
else
    echo ""
    echo "⏸️  已跳过推送"
    echo "   你可以稍后手动运行: git push -u origin $current_branch"
fi

echo ""
echo "✅ 脚本执行完成!"
