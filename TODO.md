# v3.0 待办清单

## ✅ 已完成

- [x] 创建 Node.js 后台脚本 `fetch_news.js`
- [x] 创建 `package.json` 管理依赖
- [x] 重构前端 `index.html`，移除 API 调用
- [x] 创建 `SETUP.md` 配置指南
- [x] 创建 `WORKFLOW_SETUP.md` workflow 设置说明
- [x] 更新 `README.md` 为 v3.0 版本
- [x] 创建初始 `data.json` 文件（避免前端报错）
- [x] 更新 `.gitignore` 排除 node_modules

## ⚠️ 需要手动完成（重要）

### 1. 配置 GitHub Secrets（必须）

**步骤：**
1. 访问：https://github.com/tiger-liyonghu/insurance-news/settings/secrets/actions
2. 点击 "New repository secret" 添加：
   - `NEWS_API_KEY` = 你的 NewsAPI Key
   - `GEMINI_API_KEY` = 你的 Gemini API Key
   - `GEMINI_MODEL` = `gemini-1.5-flash` (可选)

**为什么重要：**
- 没有 Secrets，GitHub Actions 无法运行
- API Keys 必须通过 Secrets 配置，不能硬编码

### 2. 手动创建 GitHub Actions Workflow 文件

**原因：** Personal Access Token 缺少 `workflow` 权限，无法直接推送 workflow 文件。

**步骤：**
1. 访问：https://github.com/tiger-liyonghu/insurance-news
2. 点击 "Add file" → "Create new file"
3. 文件路径：`.github/workflows/update.yml`
4. 复制 `WORKFLOW_SETUP.md` 中的 YAML 内容
5. 点击 "Commit new file"

**详细说明：** 查看 `WORKFLOW_SETUP.md`

### 3. 提交并推送代码

当前本地有未推送的提交，需要：
1. 解决 workflow 文件权限问题（见步骤2）
2. 或先推送其他文件，workflow 文件手动创建

## 🔍 验证清单

完成上述步骤后，验证以下内容：

- [ ] GitHub Secrets 已配置（3个）
- [ ] `.github/workflows/update.yml` 文件已创建
- [ ] 访问 https://github.com/tiger-liyonghu/insurance-news/actions 能看到 workflow
- [ ] 手动触发一次 workflow 运行
- [ ] workflow 运行成功后，`data.json` 文件被更新
- [ ] 前端页面能正常加载数据

## 📝 后续优化（可选）

- [ ] 添加错误通知（如 GitHub Actions 失败时发送邮件）
- [ ] 优化数据抓取逻辑（增加重试机制）
- [ ] 添加数据验证（确保 data.json 格式正确）
- [ ] 性能优化（减少 API 调用次数）

## 🐛 故障排查

如果遇到问题，检查：

1. **GitHub Actions 不运行**
   - 检查 workflow 文件是否存在
   - 检查 Secrets 是否配置
   - 查看 Actions 页面的错误日志

2. **data.json 未更新**
   - 检查 workflow 是否成功运行
   - 检查 API Keys 是否有效
   - 查看 workflow 日志

3. **前端无法加载数据**
   - 检查 `data.json` 文件是否存在
   - 检查文件格式是否正确
   - 查看浏览器控制台错误

## 📚 相关文档

- [SETUP.md](./SETUP.md) - 详细设置指南
- [WORKFLOW_SETUP.md](./WORKFLOW_SETUP.md) - Workflow 设置说明
- [README.md](./README.md) - 项目说明
