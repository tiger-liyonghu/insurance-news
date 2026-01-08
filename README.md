# 🛡️ 全球反保险欺诈联盟 - 云端情报站 (GIFIA)

> Global Insurance Fraud Intelligence Agent

一个自动化系统，利用 AI Agent 全球搜集保险理赔欺诈案例，每小时自动更新，展示全球最新的深度欺诈案例分析。

## 📋 项目简介

**开发者**: Yonghu LI  
**目标**: 建立自动化网站，每小时更新一次，展示全球最新的 6 个深度欺诈案例  
**核心价值**: 通过对"作案经过"和"破绽分析"的沉淀，建立行业 IP 和反欺诈案例库

## 🛠️ 技术栈

- **语言**: Python 3.10+
- **搜索**: Tavily AI API（全球联网检索）
- **AI 提取**: Google Gemini 1.5 Pro API（长文本提取与结构化）
- **数据库**: Supabase（云端持久化存储，支持查重）
- **前端**: Streamlit（极简 Web 展示页面）
- **自动化**: GitHub Actions（Cron Job，每小时运行一次）

## 📊 数据字段

每个案例包含以下结构化信息：

1. **Time (时间)**: 事件发生或判决的具体时间
2. **Region (地区)**: 国家及城市
3. **Characters (人物/实体)**: 涉案人身份、保险公司、中介或医疗机构
4. **Event (事件)**: 欺诈类型概括
5. **Process (经过)**: 【重点】详细的作案手法、逃避初审的过程、以及被发现的破绽细节
6. **Result (结果)**: 判决结果、罚金或法律制裁
7. **Source_URL (原始链接)**: 信息来源链接
8. **Created_at (入库时间)**: 数据入库时间

## 🚀 快速开始

### 第一步：安装依赖

```bash
pip install -r requirements.txt
```

### 第二步：申请 API Key

#### 1. Tavily API Key（搜索）

- **访问**: https://tavily.com/
- **步骤**:
  1. 注册账号（支持 GitHub/Google 登录）
  2. 进入 Dashboard
  3. 复制你的 API Key
  4. 免费额度：每月 1000 次搜索

#### 2. Google Gemini API Key（AI 提取）

- **访问**: https://makersuite.google.com/app/apikey
- **步骤**:
  1. 使用 Google 账号登录
  2. 点击 "Create API Key"
  3. 选择项目或创建新项目
  4. 复制生成的 API Key
  5. 免费额度：每分钟 15 次请求，每月 1500 次

#### 3. Supabase（数据库）

- **访问**: https://supabase.com/
- **步骤**:
  1. 注册账号（支持 GitHub 登录）
  2. 创建新项目（New Project）
  3. 选择地区（建议选择离你最近的）
  4. 等待项目初始化完成（约 2 分钟）
  5. 进入 Project Settings > API
  6. 复制：
     - **Project URL** (SUPABASE_URL)
     - **anon public key** (SUPABASE_KEY)

#### 4. 创建数据库表

在 Supabase Dashboard 中：

1. 点击左侧菜单 **SQL Editor**
2. 点击 **New Query**
3. 执行以下 SQL 创建表：

```sql
-- 创建保险欺诈案例表
CREATE TABLE IF NOT EXISTS fraud_cases (
    id BIGSERIAL PRIMARY KEY,
    time TEXT NOT NULL,
    region TEXT NOT NULL,
    characters TEXT NOT NULL,
    event TEXT NOT NULL,
    process TEXT NOT NULL,
    result TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,  -- 唯一约束，用于去重
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引以提高查询速度
CREATE INDEX IF NOT EXISTS idx_fraud_cases_created_at ON fraud_cases(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fraud_cases_source_url ON fraud_cases(source_url);

-- 添加更新时间的触发器（可选）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_fraud_cases_updated_at 
    BEFORE UPDATE ON fraud_cases 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

### 第三步：配置环境变量

#### 方式1：使用环境变量（推荐）

在命令行中设置（Linux/macOS）：

```bash
export TAVILY_API_KEY="your_tavily_key"
export GEMINI_API_KEY="your_gemini_key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your_supabase_key"
```

Windows (PowerShell):

```powershell
$env:TAVILY_API_KEY="your_tavily_key"
$env:GEMINI_API_KEY="your_gemini_key"
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_KEY="your_supabase_key"
```

#### 方式2：创建配置文件

1. 复制 `config.example.py` 为 `config.py`
2. 填入你的 API Key
3. 修改 `agent.py` 和 `app.py` 导入配置（不推荐，安全性较低）

### 第四步：本地测试

#### 1. 运行抓取脚本

```bash
python agent.py
```

这将：
- 搜索全球最新的保险欺诈案例
- 使用 Gemini 提取结构化信息
- 保存到 Supabase 数据库（自动去重）

#### 2. 运行 Web 展示页面

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，展示最新的 6 个案例。

## 🔄 自动化部署

### GitHub Actions 配置

#### 1. 设置 GitHub Secrets

在 GitHub 仓库中：

1. 进入 **Settings** > **Secrets and variables** > **Actions**
2. 点击 **New repository secret**
3. 添加以下 4 个 Secrets：
   - `TAVILY_API_KEY`
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

#### 2. 启用 GitHub Actions

1. 确保 `.github/workflows/auto_scraper.yml` 文件已提交
2. 进入 **Actions** 标签页
3. 首次运行需要手动点击 "Run workflow"

#### 3. Cron 时间设置

工作流默认每小时执行一次（UTC 时间）。如需调整，编辑 `.github/workflows/auto_scraper.yml` 中的 Cron 表达式。

### Streamlit Cloud 部署

#### 1. 准备工作

1. 将代码推送到 GitHub 仓库
2. 确保 `requirements.txt` 已提交

#### 2. 部署步骤

1. **访问 Streamlit Cloud**: https://share.streamlit.io/
2. **使用 GitHub 登录**
3. **点击 "New app"**
4. **配置应用**:
   - **Repository**: 选择你的仓库
   - **Branch**: `main` 或 `master`
   - **Main file path**: `app.py`
5. **配置 Secrets**:
   - 点击 **Advanced settings**
   - 添加以下 Secrets（与 GitHub Secrets 相同）:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
   - ⚠️ **注意**: `app.py` 只需要 Supabase 的配置，不需要 Tavily 和 Gemini（因为抓取在 GitHub Actions 中完成）
6. **点击 Deploy**

#### 3. 访问你的应用

部署完成后，Streamlit Cloud 会提供一个公开 URL，例如：
```
https://your-app-name.streamlit.app
```

## 📁 项目结构

```
全球反保险欺诈联盟/
├── agent.py              # 抓取脚本（Tavily + Gemini + Supabase）
├── app.py                # Streamlit Web 展示页面
├── requirements.txt      # Python 依赖包
├── config.example.py     # 配置文件示例
├── README.md            # 本文件
└── .github/
    └── workflows/
        └── auto_scraper.yml  # GitHub Actions 自动化配置
```

## 🔍 代码说明

### agent.py 核心功能

1. **`search_fraud_cases()`**: 使用 Tavily API 搜索全球保险欺诈案例
2. **`extract_case_info_with_gemini()`**: 使用 Gemini 1.5 Pro 提取结构化信息
3. **`check_duplicate()`**: 检查 URL 是否已存在（去重）
4. **`save_to_supabase()`**: 保存案例到 Supabase 数据库

### app.py 核心功能

1. **`fetch_latest_cases()`**: 从 Supabase 获取最新的 6 个案例
2. **主页面**: 使用 Streamlit 展示案例卡片，重点展示"作案经过"
3. **侧边栏**: 显示数据统计和地区分布

## ⚠️ 注意事项

1. **API 限流**: 
   - Tavily: 每月 1000 次（免费版）
   - Gemini: 每分钟 15 次请求
   - 代码中已添加 2 秒延迟避免限流

2. **数据去重**: 
   - 使用 `source_url` 作为唯一标识
   - 数据库已设置唯一约束

3. **成本控制**: 
   - 每小时运行一次，每天最多 24 次
   - 每次搜索约 10 个结果，每天约 240 次搜索（在免费额度内）

4. **错误处理**: 
   - 所有 API 调用都有异常处理
   - 失败案例会被记录但不会中断流程

## 🐛 常见问题

### Q1: 运行 agent.py 报错 "缺少 API Key"

**A**: 请确保已设置所有环境变量，或检查 `config.py` 配置。

### Q2: Supabase 连接失败

**A**: 
- 检查 Project URL 和 Key 是否正确
- 确认项目状态为 "Active"
- 检查防火墙是否阻止连接

### Q3: Gemini 提取失败或返回空数据

**A**:
- 检查 API Key 是否有效
- 确认免费额度未用尽
- 查看控制台错误信息，可能需要调整 prompt

### Q4: GitHub Actions 不执行

**A**:
- 确认已启用 GitHub Actions
- 检查 `.github/workflows/` 目录是否正确
- 查看 Actions 标签页的错误日志

### Q5: Streamlit 页面显示空白

**A**:
- 确认 Supabase 中有数据（先运行 agent.py）
- 检查 Streamlit Cloud 的 Secrets 配置
- 查看 Streamlit Cloud 的日志输出

## 📝 更新日志

- **2025-01**: 初始版本发布
  - 支持 Tavily 搜索
  - 集成 Gemini 1.5 Pro 提取
  - Supabase 存储
  - Streamlit 展示
  - GitHub Actions 自动化

## 📄 许可证

本项目仅供学习和研究使用。

## 👤 作者

**Yonghu LI** - 资深保险专家

---

如有问题，欢迎提交 Issue 或 Pull Request！
