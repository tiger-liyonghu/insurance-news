# v3.0 架构设置指南

## 架构说明

v3.0 采用**前后端分离**架构：
- **后台脚本** (`fetch_news.js`): 负责数据抓取和 AI 处理
- **GitHub Actions**: 自动运行后台脚本并更新数据
- **前端** (`index.html`): 仅负责展示，读取本地 `data.json`

## 设置步骤

### 1. 安装依赖

```bash
npm install
```

### 2. 配置 GitHub Secrets

⚠️ **重要**: API Keys 必须通过 GitHub Secrets 配置，绝对不能硬编码在代码中！

#### 步骤：

1. 访问你的 GitHub 仓库：`https://github.com/tiger-liyonghu/insurance-news`

2. 点击 **Settings** (设置)

3. 在左侧菜单中找到 **Secrets and variables** → **Actions**

4. 点击 **New repository secret** 添加以下 Secrets：

   - **Name**: `NEWS_API_KEY`
     - **Value**: 你的 NewsAPI Key
   
   - **Name**: `GEMINI_API_KEY`
     - **Value**: 你的 Google Gemini API Key
   
   - **Name**: `GEMINI_MODEL` (可选)
     - **Value**: `gemini-1.5-flash` (默认值)

5. 点击 **Add secret** 保存每个 Secret

### 3. 测试本地运行（可选）

如果你想在本地测试后台脚本：

```bash
# 设置环境变量（仅用于本地测试）
export NEWS_API_KEY="你的_NewsAPI_Key"
export GEMINI_API_KEY="你的_Gemini_API_Key"

# 运行脚本
npm run fetch
```

### 4. 启用 GitHub Actions

1. 确保 `.github/workflows/update.yml` 文件已提交到仓库

2. GitHub Actions 会自动：
   - 每小时运行一次（整点）
   - 代码推送时也会运行
   - 可以手动触发（在 Actions 页面）

3. 查看运行状态：
   - 访问：`https://github.com/tiger-liyonghu/insurance-news/actions`
   - 查看 "自动更新新闻数据" 工作流

### 5. 验证数据更新

- GitHub Actions 运行成功后，会自动提交 `data.json` 文件
- 前端页面会自动读取最新的 `data.json`
- 检查 `data.json` 文件是否包含最新数据

## 文件结构

```
insurance-news/
├── index.html          # 前端展示页面（v3.0）
├── fetch_news.js       # 后台数据抓取脚本
├── package.json        # Node.js 依赖配置
├── data.json           # 生成的数据文件（由 GitHub Actions 自动更新）
├── .github/
│   └── workflows/
│       └── update.yml  # GitHub Actions 工作流配置
└── SETUP.md           # 本设置文档
```

## 安全注意事项

✅ **正确做法**：
- API Keys 存储在 GitHub Secrets 中
- 代码中通过 `process.env` 读取环境变量
- Secrets 不会出现在代码、日志或提交历史中

❌ **错误做法**：
- 在代码中硬编码 API Keys
- 将 API Keys 提交到 Git 仓库
- 在公开场合分享 API Keys

## 故障排查

### GitHub Actions 运行失败

1. 检查 Secrets 是否已正确配置
2. 查看 Actions 日志：`https://github.com/tiger-liyonghu/insurance-news/actions`
3. 确认 `NEWS_API_KEY` 和 `GEMINI_API_KEY` 是否有效

### 前端无法加载数据

1. 检查 `data.json` 文件是否存在
2. 确认 GitHub Actions 已成功运行并提交了 `data.json`
3. 查看浏览器控制台是否有错误信息

### 数据未更新

1. GitHub Actions 每小时运行一次，请耐心等待
2. 可以手动触发：Actions → "自动更新新闻数据" → "Run workflow"

## 更新频率

- **自动更新**: 每小时一次（整点）
- **手动触发**: 随时可以在 Actions 页面手动运行
- **代码推送**: 当 `fetch_news.js` 或工作流文件更新时自动运行
