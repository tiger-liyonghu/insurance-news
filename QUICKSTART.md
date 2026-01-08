# 🚀 快速开始指南

本文档将帮助你在 10 分钟内完成系统设置并开始使用。

## 📋 前置要求

- Python 3.10 或更高版本
- GitHub 账号（用于自动化）
- 网络连接

## ⚡ 5 步快速设置

### 步骤 1: 安装依赖（2 分钟）

```bash
# 克隆或下载项目后，进入项目目录
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2: 申请 API Key（5 分钟）

#### 2.1 Tavily API Key（搜索）

1. 访问：https://tavily.com/
2. 点击 **"Sign Up"**，使用 GitHub/Google 登录
3. 进入 Dashboard，复制 **API Key**

#### 2.2 Gemini API Key（AI 提取）

1. 访问：https://makersuite.google.com/app/apikey
2. 使用 Google 账号登录
3. 点击 **"Create API Key"**
4. 复制生成的 **API Key**

#### 2.3 Supabase（数据库）

1. 访问：https://supabase.com/
2. 点击 **"Start your project"**，使用 GitHub 登录
3. 点击 **"New Project"**
4. 填写项目信息：
   - **Name**: GIFIA（或其他名称）
   - **Database Password**: 设置一个强密码（**务必保存！**）
   - **Region**: 选择离你最近的区域（如 Southeast Asia）
5. 等待项目创建完成（约 2 分钟）
6. 进入 **Settings** > **API**
7. 复制：
   - **Project URL** → 这就是 `SUPABASE_URL`
   - **anon public** key → 这就是 `SUPABASE_KEY`

#### 2.4 创建数据库表

1. 在 Supabase Dashboard 中，点击左侧菜单 **SQL Editor**
2. 点击 **New Query**
3. 打开项目中的 `database.sql` 文件
4. 复制所有 SQL 代码到 Supabase SQL Editor
5. 点击 **Run** 执行

### 步骤 3: 配置环境变量（1 分钟）

#### macOS/Linux：

```bash
# 在命令行中执行（临时设置）
export TAVILY_API_KEY="你的Tavily_API_Key"
export GEMINI_API_KEY="你的Gemini_API_Key"
export SUPABASE_URL="你的Supabase_URL"
export SUPABASE_KEY="你的Supabase_Key"

# 验证设置
echo $TAVILY_API_KEY  # 应该显示你的 Key
```

#### 永久设置（推荐）：

编辑 `~/.zshrc` 或 `~/.bashrc` 文件：

```bash
# 添加以下内容
export TAVILY_API_KEY="你的Tavily_API_Key"
export GEMINI_API_KEY="你的Gemini_API_Key"
export SUPABASE_URL="你的Supabase_URL"
export SUPABASE_KEY="你的Supabase_Key"
```

然后执行：

```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

#### Windows (PowerShell):

```powershell
$env:TAVILY_API_KEY="你的Tavily_API_Key"
$env:GEMINI_API_KEY="你的Gemini_API_Key"
$env:SUPABASE_URL="你的Supabase_URL"
$env:SUPABASE_KEY="你的Supabase_Key"
```

### 步骤 4: 测试配置（1 分钟）

```bash
# 运行测试脚本
python test_config.py
```

如果看到所有 ✅，说明配置正确！

### 步骤 5: 运行系统（1 分钟）

#### 5.1 首次抓取数据

```bash
# 运行抓取脚本
python agent.py
```

等待几分钟，脚本会：
- 搜索全球最新的保险欺诈案例
- 使用 AI 提取结构化信息
- 保存到 Supabase 数据库

#### 5.2 启动 Web 展示页面

```bash
# 在另一个终端窗口运行
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，展示最新的案例！

## 🎉 完成！

你现在已经成功设置了系统。接下来：

### 本地使用

- **抓取数据**: 运行 `python agent.py`（建议每小时运行一次）
- **查看案例**: 运行 `streamlit run app.py`（保持运行即可）

### 自动化部署（可选）

如果你想实现每小时自动抓取，需要：

1. **将代码推送到 GitHub**
2. **设置 GitHub Secrets**（在仓库 Settings > Secrets 中添加 4 个 Key）
3. **启用 GitHub Actions**（在 Actions 标签页）

详细步骤请参考 `README.md` 中的"自动化部署"部分。

## ❓ 遇到问题？

### 问题 1: `pip install` 失败

**解决**: 使用 Python 3.10+，检查网络连接

```bash
python --version  # 应该是 3.10 或更高
```

### 问题 2: API Key 错误

**解决**: 检查环境变量是否正确设置

```bash
echo $TAVILY_API_KEY  # 应该显示你的 Key，不是空的
```

### 问题 3: Supabase 连接失败

**解决**: 
- 检查 URL 和 Key 是否正确（注意不要有多余空格）
- 确认项目状态为 "Active"
- 确认已创建 `fraud_cases` 表（运行 `database.sql`）

### 问题 4: 运行 `agent.py` 没有数据

**解决**: 
- 检查 Tavily API 是否有免费额度剩余
- 查看控制台错误信息
- 尝试减少搜索数量（修改 `max_results` 参数）

## 📚 下一步

- 阅读 `README.md` 了解详细功能
- 自定义搜索关键词（修改 `agent.py` 中的 `query`）
- 调整展示样式（修改 `app.py`）

祝你使用愉快！🎊
