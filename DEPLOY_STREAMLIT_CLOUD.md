# 🚀 Streamlit Cloud 部署指南

## 当前本地运行

**本地地址**: http://localhost:8501

（仅在你的电脑上可访问）

---

## 部署到 Streamlit Cloud（公开访问）

### 步骤 1: 准备 GitHub 仓库

确保代码已推送到 GitHub：
- 仓库：https://github.com/tiger-liyonghu/insurance-news
- 主文件：`app_v5_redesigned.py`

### 步骤 2: 访问 Streamlit Cloud

1. 访问：https://streamlit.io/cloud
2. 使用 GitHub 账号登录
3. 点击 "New app"

### 步骤 3: 配置应用

**应用设置**：
- **Repository**: `tiger-liyonghu/insurance-news`
- **Branch**: `main`
- **Main file path**: `app_v5_redesigned.py`
- **App URL**: 可以自定义（如：`gifia-v5`）

### 步骤 4: 配置 Secrets

在 Streamlit Cloud 中设置环境变量：

1. 进入应用设置（Settings）
2. 点击 "Secrets"
3. 添加以下 Secrets：

```toml
SUPABASE_URL = "https://wgprfrzbhdopznmkzwqu.supabase.co"
SUPABASE_KEY = "你的_SUPABASE_KEY"
TAVILY_API_KEY = "你的_TAVILY_API_KEY"
GEMINI_API_KEY = "你的_GEMINI_API_KEY"
DEEPSEEK_API_KEY = "你的_DEEPSEEK_API_KEY"
```

### 步骤 5: 部署

1. 点击 "Deploy"
2. 等待部署完成（通常 1-2 分钟）
3. 获取公开 URL

**部署后的 URL 格式**：
```
https://gifia-v5.streamlit.app
```
或
```
https://insurance-news-tiger-liyonghu.streamlit.app
```

---

## 快速部署命令（如果使用 Streamlit CLI）

```bash
# 安装 Streamlit CLI（如果还没有）
pip install streamlit

# 登录 Streamlit Cloud
streamlit login

# 部署应用
streamlit deploy app_v5_redesigned.py
```

---

## 部署后检查清单

- [ ] 应用可以正常访问
- [ ] 数据可以正常加载
- [ ] 筛选器功能正常
- [ ] Agent 状态显示正常
- [ ] 所有 Secrets 已配置

---

## 其他部署选项

### 选项 1: Vercel / Netlify

如果使用 Vercel 或 Netlify，需要：
1. 将 Streamlit 应用转换为静态网站（使用 `streamlit-static`）
2. 或使用 Docker 容器部署

### 选项 2: 自有服务器

如果使用自有服务器：
1. 安装 Streamlit
2. 使用 Nginx 反向代理
3. 配置 SSL 证书

---

## 推荐：Streamlit Cloud（最简单）

**优势**：
- ✅ 免费
- ✅ 自动 HTTPS
- ✅ 自动更新（GitHub push 后自动部署）
- ✅ 无需服务器配置

**部署后，你将获得类似这样的公开 URL**：
```
https://your-app-name.streamlit.app
```

---

**按照上述步骤部署后，告诉我你的 Streamlit Cloud URL！** 🚀
