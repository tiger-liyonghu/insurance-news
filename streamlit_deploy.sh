#!/bin/bash
# Streamlit Cloud 快速部署脚本

echo "🚀 GIFIA v5.0 - Streamlit Cloud 部署准备"
echo "========================================"
echo ""

# 检查是否已安装 streamlit
if ! command -v streamlit &> /dev/null; then
    echo "📦 安装 Streamlit..."
    pip3 install streamlit
fi

# 检查是否已登录
echo "🔐 检查 Streamlit Cloud 登录状态..."
streamlit whoami 2>/dev/null

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  未登录 Streamlit Cloud"
    echo "请运行: streamlit login"
    echo ""
    echo "然后访问: https://streamlit.io/cloud"
    echo "或运行: streamlit deploy app_v5_redesigned.py"
else
    echo ""
    echo "✅ 已登录 Streamlit Cloud"
    echo ""
    echo "📤 准备部署..."
    echo ""
    echo "部署命令:"
    echo "  streamlit deploy app_v5_redesigned.py"
    echo ""
    echo "或访问 Streamlit Cloud Dashboard:"
    echo "  https://share.streamlit.io/"
fi

echo ""
echo "📋 部署前检查清单:"
echo "  [ ] 代码已推送到 GitHub"
echo "  [ ] 已配置 Streamlit Cloud Secrets"
echo "  [ ] app_v5_redesigned.py 文件存在"
echo ""
