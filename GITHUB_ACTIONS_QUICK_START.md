# ⚡ GitHub Actions 快速开始指南

## 🎯 5 分钟快速配置

### 方法 1: 使用自动化脚本（推荐）

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"
./setup_github_repo.sh
```

脚本会自动：
1. ✅ 初始化 Git 仓库（如果还没有）
2. ✅ 创建 .gitignore
3. ✅ 添加远程仓库
4. ✅ 推送代码到 GitHub

### 方法 2: 手动配置

#### 步骤 1: 初始化并推送代码

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

# 如果还没有 Git 仓库
git init
git add .
git commit -m "Initial commit: GIFIA v4.0"

# 添加远程仓库（替换为你的 GitHub 仓库 URL）
git remote add origin https://github.com/你的用户名/gifia.git

# 推送到 GitHub
git push -u origin main
```

#### 步骤 2: 在 GitHub 上添加 Secrets

1. 打开你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，添加以下 5 个：

| Secret 名称 | 说明 |
|------------|------|
| `TAVILY_API_KEY` | Tavily API Key |
| `GEMINI_API_KEY` | Gemini API Key |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `SUPABASE_URL` | Supabase 项目 URL |
| `SUPABASE_KEY` | Supabase API Key |

#### 步骤 3: 验证配置

1. 点击 **Actions** 标签
2. 点击 **"GIFIA Living Scout - 24/7 全球自动侦察"**
3. 点击 **"Run workflow"** 手动触发测试
4. 查看运行日志确认成功

---

## 📋 详细步骤

需要更详细的说明？查看完整指南：

👉 **[GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md)**

---

## ✅ 配置检查清单

- [ ] Git 仓库已初始化
- [ ] 代码已推送到 GitHub
- [ ] 5 个 Secrets 已添加
- [ ] Actions 工作流已可见
- [ ] 手动测试运行成功

---

## 🎉 完成！

配置完成后，系统将每 30 分钟自动运行一次！
