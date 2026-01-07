# 全球保险欺诈监测情报系统 v3.0

Global Insurance Fraud Monitoring Intelligence System v3.0

## 功能特性

- 🔍 实时抓取全球保险欺诈案例
- 🤖 AI 智能分类和摘要生成
- 🌍 多语言支持（中文、英文、泰语、越南语）
- 📊 数据大屏可视化展示
- ⏰ 每小时自动更新

## 技术栈

### v3.0 架构（前后端分离）
- **前端**: HTML5 + Tailwind CSS + Lucide Icons
- **后台**: Node.js + node-fetch
- **数据源**: NewsAPI（新闻数据源）
- **AI 处理**: Google Gemini 1.5 Flash
- **自动化**: GitHub Actions（每小时自动更新）

## 使用方法

### v3.0 设置（推荐）

1. **配置 GitHub Secrets**（必须）：
   - 访问仓库 Settings → Secrets and variables → Actions
   - 添加 `NEWS_API_KEY` 和 `GEMINI_API_KEY`
   - 详细步骤请查看 [SETUP.md](./SETUP.md)

2. **GitHub Actions 自动运行**：
   - 每小时自动抓取数据并更新 `data.json`
   - 无需手动操作

3. **访问网站**：
   - GitHub Pages: https://tiger-liyonghu.github.io/insurance-news/
   - 或本地运行：`python3 -m http.server 8000`

### 本地开发（可选）

```bash
# 安装依赖
npm install

# 设置环境变量
export NEWS_API_KEY="你的_NewsAPI_Key"
export GEMINI_API_KEY="你的_Gemini_API_Key"

# 运行数据抓取脚本
npm run fetch
```

## 部署

推荐使用 Netlify、Vercel 或 GitHub Pages 进行部署。

## 版本历史

- **v3.0** (当前): 前后端分离架构
  - 架构：后台自动抓取 + 前端静态展示
  - 自动化：GitHub Actions 每小时自动更新
  - 安全：API Keys 通过 GitHub Secrets 管理
  - 文件：Node.js 后台脚本 + GitHub Actions 工作流
  - 备份文件：`index-v3.0.html`
- **v2.0**: 全球保险欺诈监测情报系统
  - 功能：AI 智能分类、多语言支持、数据大屏展示、模拟数据备选方案
  - 备份文件：`index-v2.0.html`
- **v1.0**: 保险新闻看板
  - 备份文件：`index-v1.0.html`
