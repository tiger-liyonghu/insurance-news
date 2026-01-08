# 版本历史记录

## v3.0 - 前后端分离架构（当前版本）

**发布日期**: 2024-01-07

### 核心特性

- ✅ **前后端分离架构**
  - 后台脚本 (`fetch_news.js`) 负责数据抓取和 AI 处理
  - 前端 (`index.html`) 仅负责展示，读取本地 `data.json`
  
- ✅ **自动化数据更新**
  - GitHub Actions 每小时自动运行
  - 自动抓取新闻 → AI 处理 → 更新 `data.json`
  
- ✅ **安全性提升**
  - API Keys 通过 GitHub Secrets 管理
  - 代码中无硬编码密钥
  
- ✅ **用户体验优化**
  - 友好的空数据提示
  - 详细的错误信息和解决指南
  - 多语言支持（中文、英文、泰语、越南语）

### 技术栈

- **前端**: HTML5 + Tailwind CSS + Lucide Icons
- **后台**: Node.js + node-fetch
- **数据源**: NewsAPI
- **AI 处理**: Google Gemini 1.5 Flash
- **自动化**: GitHub Actions

### 文件结构

```
v3.0/
├── index.html              # 前端展示页面
├── fetch_news.js           # 后台数据抓取脚本
├── package.json            # Node.js 依赖
├── data.json               # 生成的数据文件
├── .github/workflows/
│   └── update.yml          # GitHub Actions 工作流
├── SETUP.md                # 设置指南
├── TROUBLESHOOTING.md      # 故障排查指南
└── index-v3.0.html         # v3.0 备份文件
```

### 主要改进

1. **架构升级**: 从单文件架构升级为前后端分离
2. **自动化**: 无需手动操作，每小时自动更新
3. **安全性**: API Keys 不再暴露在代码中
4. **可维护性**: 代码结构更清晰，易于维护

---

## v2.0 - 全球保险欺诈监测情报系统

**发布日期**: 2024-01-07

### 核心特性

- AI 智能分类（寿险、产险、再保险、大健康）
- 多语言支持（中文、英文、泰语、越南语）
- 数据大屏可视化展示
- 模拟数据备选方案（处理 NewsAPI 403 错误）

### 技术栈

- HTML5 + Tailwind CSS
- NewsAPI（新闻数据源）
- Google Gemini 1.5 Flash（AI 处理）
- Lucide Icons（图标库）

### 备份文件

- `index-v2.0.html`

---

## v1.0 - 保险新闻看板

**发布日期**: 2024-01-07

### 核心特性

- 基础新闻展示
- 120 秒自动刷新
- Gemini AI 翻译和点评

### 备份文件

- `index-v1.0.html`

---

## 版本升级路径

```
v1.0 (基础看板)
  ↓
v2.0 (AI 增强 + 数据大屏)
  ↓
v3.0 (前后端分离 + 自动化)
  ↓
v4.0 (待开发...)
```

## 备份说明

每个版本都有对应的备份文件：
- `index-v1.0.html` - v1.0 完整备份
- `index-v2.0.html` - v2.0 完整备份
- `index-v3.0.html` - v3.0 完整备份

如需回退到某个版本，直接使用对应的备份文件即可。
