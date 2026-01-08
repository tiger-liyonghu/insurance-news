# 🔧 GitHub Actions 配置详细指南

## 概述

本指南将详细说明如何配置 GitHub Actions，实现 GIFIA Living Scout 的 24/7 自动运行。

---

## 📋 前置条件

1. ✅ 已创建 GitHub 仓库（如果没有，先创建一个）
2. ✅ 已安装 Git
3. ✅ 已准备好所有 API Keys

---

## 步骤 1: 准备 API Keys

在开始之前，确保你有以下 API Keys：

- `TAVILY_API_KEY` - Tavily API Key
- `GEMINI_API_KEY` - Google Gemini API Key
- `DEEPSEEK_API_KEY` - DeepSeek API Key（可选，但推荐）
- `SUPABASE_URL` - Supabase 项目 URL
- `SUPABASE_KEY` - Supabase API Key

---

## 步骤 2: 初始化 Git 仓库（如果还没有）

### 2.1 检查是否已有 Git 仓库

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"
ls -la .git
```

如果看到 `.git` 文件夹，说明已经是 Git 仓库，跳到步骤 3。

### 2.2 如果没有 Git 仓库，初始化一个

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

# 初始化 Git 仓库
git init

# 创建 .gitignore 文件（如果还没有）
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

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: GIFIA v4.0"
```

---

## 步骤 3: 在 GitHub 上创建仓库

### 3.1 登录 GitHub

访问 https://github.com 并登录你的账号

### 3.2 创建新仓库

1. 点击右上角的 **"+"** 按钮
2. 选择 **"New repository"**
3. 填写仓库信息：
   - **Repository name**: `gifia` 或 `global-insurance-fraud-intelligence`
   - **Description**: `全球反保险欺诈联盟 - 24/7 自动侦察系统`
   - **Visibility**: 选择 **Private**（推荐，因为包含 API Keys 配置）
   - **不要**勾选 "Initialize this repository with a README"（我们已经有了文件）
4. 点击 **"Create repository"**

### 3.3 复制仓库 URL

创建后，GitHub 会显示仓库 URL，类似：
```
https://github.com/你的用户名/gifia.git
```

---

## 步骤 4: 连接本地仓库到 GitHub

### 4.1 添加远程仓库

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

# 添加远程仓库（替换为你的实际 URL）
git remote add origin https://github.com/你的用户名/gifia.git

# 验证远程仓库
git remote -v
```

### 4.2 推送代码到 GitHub

```bash
# 确保所有文件已添加
git add .

# 提交更改
git commit -m "Add GIFIA v4.0 with GitHub Actions"

# 推送到 GitHub（首次推送）
git push -u origin main
```

**注意**: 如果默认分支是 `master` 而不是 `main`，使用：
```bash
git push -u origin master
```

---

## 步骤 5: 配置 GitHub Secrets

### 5.1 进入仓库设置

1. 在 GitHub 仓库页面，点击 **"Settings"** 标签（在仓库顶部导航栏）
2. 在左侧菜单中找到 **"Secrets and variables"**
3. 点击 **"Actions"**

### 5.2 添加 Secrets

点击 **"New repository secret"** 按钮，逐个添加以下 Secrets：

#### Secret 1: TAVILY_API_KEY
- **Name**: `TAVILY_API_KEY`
- **Value**: 你的 Tavily API Key（例如：`tvly-dev-...`）
- 点击 **"Add secret"**

#### Secret 2: GEMINI_API_KEY
- **Name**: `GEMINI_API_KEY`
- **Value**: 你的 Gemini API Key（例如：`AIzaSy...`）
- 点击 **"Add secret"**

#### Secret 3: DEEPSEEK_API_KEY
- **Name**: `DEEPSEEK_API_KEY`
- **Value**: 你的 DeepSeek API Key（例如：`sk-...`）
- 点击 **"Add secret"**

#### Secret 4: SUPABASE_URL
- **Name**: `SUPABASE_URL`
- **Value**: 你的 Supabase 项目 URL（例如：`https://xxx.supabase.co`）
- 点击 **"Add secret"**

#### Secret 5: SUPABASE_KEY
- **Name**: `SUPABASE_KEY`
- **Value**: 你的 Supabase API Key（例如：`sb_publishable_...`）
- 点击 **"Add secret"**

### 5.3 验证 Secrets

添加完成后，你应该看到 5 个 Secrets 在列表中：
- ✅ TAVILY_API_KEY
- ✅ GEMINI_API_KEY
- ✅ DEEPSEEK_API_KEY
- ✅ SUPABASE_URL
- ✅ SUPABASE_KEY

---

## 步骤 6: 推送 GitHub Actions 配置文件

### 6.1 确认 workflow 文件存在

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"
ls -la .github/workflows/
```

应该看到 `living_scout.yml` 文件。

### 6.2 推送 workflow 文件

```bash
# 添加 workflow 文件
git add .github/workflows/living_scout.yml

# 提交
git commit -m "Add GitHub Actions workflow for Living Scout"

# 推送
git push origin main
```

---

## 步骤 7: 验证 GitHub Actions 是否启用

### 7.1 检查 Actions 标签

1. 在 GitHub 仓库页面，点击 **"Actions"** 标签
2. 你应该看到：
   - 左侧菜单中有 **"GIFIA Living Scout - 24/7 全球自动侦察"** 工作流
   - 如果没有立即看到运行记录，这是正常的（因为还没有触发）

### 7.2 手动触发测试运行

1. 点击 **"GIFIA Living Scout - 24/7 全球自动侦察"** 工作流
2. 点击右侧的 **"Run workflow"** 按钮
3. 选择分支（通常是 `main`）
4. 点击 **"Run workflow"** 按钮

### 7.3 查看运行日志

1. 点击刚创建的运行记录
2. 点击 **"scout"** job
3. 查看执行日志，应该看到：
   - ✅ Checkout code
   - ✅ Set up Python
   - ✅ Install dependencies
   - ✅ Run Living Scout
   - ✅ Report results

---

## 步骤 8: 验证自动调度

### 8.1 检查调度配置

打开 `.github/workflows/living_scout.yml`，确认调度设置：

```yaml
schedule:
  - cron: '*/30 * * * *'  # 每30分钟执行一次
```

### 8.2 等待自动触发

- GitHub Actions 会在每小时的 **:00** 和 **:30** 自动触发
- 例如：10:00, 10:30, 11:00, 11:30...

### 8.3 查看运行历史

在 **"Actions"** 标签页，你可以看到：
- 所有运行记录（包括手动和自动）
- 运行状态（✅ 成功 / ❌ 失败）
- 执行时间

---

## 🔍 故障排除

### 问题 1: Actions 标签不可见

**原因**: 仓库可能禁用了 Actions

**解决**:
1. 进入仓库 **Settings**
2. 点击 **Actions** → **General**
3. 在 **"Actions permissions"** 中选择 **"Allow all actions and reusable workflows"**
4. 点击 **Save**

### 问题 2: Workflow 没有自动运行

**原因**: 
- 调度时间还没到
- 仓库是私有仓库，需要 GitHub Pro 或更高版本才能使用 Actions

**解决**:
- 等待下一个调度时间（:00 或 :30）
- 或手动触发测试
- 如果是私有仓库，考虑升级 GitHub 计划或使用 GitHub Actions 的免费额度

### 问题 3: Secrets 未找到

**错误信息**: `Error: Required secret TAVILY_API_KEY is not set`

**解决**:
1. 检查 Secrets 是否已正确添加
2. 检查 Secret 名称是否完全匹配（区分大小写）
3. 重新推送 workflow 文件

### 问题 4: Python 依赖安装失败

**错误信息**: `ModuleNotFoundError` 或 `pip install` 失败

**解决**:
1. 检查 `requirements.txt` 是否包含所有依赖
2. 确保依赖版本兼容
3. 查看完整错误日志定位问题

### 问题 5: API Key 验证失败

**错误信息**: `403` 或 `401` 错误

**解决**:
1. 检查 API Key 是否正确
2. 检查 API Key 是否过期
3. 检查 API Key 是否有足够的配额

---

## 📊 监控和维护

### 查看运行状态

1. 进入 **Actions** 标签
2. 查看工作流运行历史
3. 绿色 ✅ = 成功
4. 红色 ❌ = 失败（点击查看详细错误）

### 查看日志

1. 点击失败的运行记录
2. 点击 **"scout"** job
3. 展开各个步骤查看详细日志

### 修改调度频率

编辑 `.github/workflows/living_scout.yml`：

```yaml
schedule:
  - cron: '*/30 * * * *'  # 每30分钟
  # 或
  - cron: '0 * * * *'     # 每小时
  # 或
  - cron: '0 */6 * * *'  # 每6小时
```

然后推送更改：
```bash
git add .github/workflows/living_scout.yml
git commit -m "Update schedule frequency"
git push origin main
```

---

## ✅ 配置检查清单

完成以下检查清单，确保配置正确：

- [ ] Git 仓库已初始化
- [ ] 代码已推送到 GitHub
- [ ] GitHub 仓库已创建
- [ ] 5 个 Secrets 已全部添加
- [ ] `.github/workflows/living_scout.yml` 文件已推送
- [ ] Actions 标签可见
- [ ] 手动触发测试运行成功
- [ ] 查看日志确认无错误
- [ ] 等待自动调度触发（可选）

---

## 🎉 完成！

配置完成后，GitHub Actions 将：
- ✅ 每 30 分钟自动运行一次
- ✅ 执行 Living Scout 侦察任务
- ✅ 将结果保存到 Supabase 数据库
- ✅ 在 Actions 页面显示运行状态和日志

**系统现已实现 24/7 全球自动侦察！** 🚀

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 GitHub Actions 日志获取详细错误信息
2. 检查 Secrets 是否正确配置
3. 验证 API Keys 是否有效
4. 参考故障排除部分
