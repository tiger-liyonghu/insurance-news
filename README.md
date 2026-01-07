# 全球保险欺诈监测情报系统 v2.0

Global Insurance Fraud Monitoring Intelligence System v2.0

## 功能特性

- 🔍 实时抓取全球保险欺诈案例
- 🤖 AI 智能分类和摘要生成
- 🌍 多语言支持（中文、英文、泰语、越南语）
- 📊 数据大屏可视化展示
- ⏰ 每小时自动更新

## 技术栈

- HTML5 + Tailwind CSS
- NewsAPI（新闻数据源）
- Google Gemini 1.5 Flash（AI 处理）
- Lucide Icons（图标库）

## 使用方法

1. 在 `index.html` 顶部配置您的 API Keys：
   - `NEWS_API_KEY`: NewsAPI 密钥
   - `GEMINI_API_KEY`: Google Gemini API 密钥

2. 直接在浏览器中打开 `index.html` 或使用本地服务器：
   ```bash
   python3 -m http.server 8000
   ```

3. 访问 http://localhost:8000

## 部署

推荐使用 Netlify、Vercel 或 GitHub Pages 进行部署。

## 版本历史

- **v2.0** (当前): 全球保险欺诈监测情报系统
  - 功能：AI 智能分类、多语言支持、数据大屏展示、模拟数据备选方案
  - 备份文件：`index-v2.0.html`
- **v1.0**: 保险新闻看板
  - 备份文件：`index-v1.0.html`
