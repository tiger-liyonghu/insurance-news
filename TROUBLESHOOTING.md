# 故障排查指南：GitHub Actions 未运行

## 当前问题
看到 "等待数据更新" 提示，说明 GitHub Actions 尚未运行或配置未完成。

## 解决步骤

### 步骤 1：检查 GitHub Secrets 是否已配置 ⚠️ 最重要

1. **访问 Secrets 设置页面**：
   ```
   https://github.com/tiger-liyonghu/insurance-news/settings/secrets/actions
   ```

2. **检查是否已有以下 Secrets**：
   - ✅ `NEWS_API_KEY` - 你的 NewsAPI Key
   - ✅ `GEMINI_API_KEY` - 你的 Gemini API Key
   - ⚪ `GEMINI_MODEL` - 可选（默认为 `gemini-1.5-flash`）

3. **如果缺少，立即添加**：
   - 点击 "New repository secret"
   - 输入 Name 和 Value
   - 点击 "Add secret"

**⚠️ 没有 Secrets，GitHub Actions 无法运行！**

### 步骤 2：检查 GitHub Actions 工作流是否存在

1. **访问 Actions 页面**：
   ```
   https://github.com/tiger-liyonghu/insurance-news/actions
   ```

2. **检查是否有 "自动更新新闻数据" 工作流**

3. **如果没有，说明 workflow 文件未创建**：
   - 查看 [WORKFLOW_SETUP.md](./WORKFLOW_SETUP.md) 手动创建

### 步骤 3：手动触发 GitHub Actions

1. **访问 Actions 页面**：
   ```
   https://github.com/tiger-liyonghu/insurance-news/actions
   ```

2. **点击左侧的 "自动更新新闻数据" 工作流**

3. **点击右侧的 "Run workflow" 按钮**

4. **选择分支**：`main`

5. **点击绿色的 "Run workflow" 按钮**

6. **等待运行完成**（通常 1-2 分钟）

### 步骤 4：检查运行日志

1. **在 Actions 页面，点击最新的运行记录**

2. **查看每个步骤的状态**：
   - ✅ 绿色 = 成功
   - ❌ 红色 = 失败
   - ⏳ 黄色 = 运行中

3. **如果失败，点击失败的步骤查看错误信息**

### 常见错误及解决方案

#### 错误 1：Secrets 未配置
```
❌ 错误: NEWS_API_KEY 环境变量未设置
```

**解决**：
- 配置 GitHub Secrets（见步骤 1）

#### 错误 2：API Key 无效
```
NewsAPI 错误 (401): Invalid API key
```

**解决**：
- 检查 API Key 是否正确
- 确认 Key 是否有效（未过期）

#### 错误 3：权限不足
```
Permission denied
```

**解决**：
- 检查仓库是否为 Public（免费账户私有仓库不支持 Actions）
- 或升级到 GitHub Pro

#### 错误 4：Node.js 依赖安装失败
```
npm install failed
```

**解决**：
- 检查 `package.json` 是否正确
- 查看详细错误日志

### 步骤 5：验证数据更新

1. **等待 Actions 运行完成**

2. **检查 `data.json` 文件**：
   - 访问：https://github.com/tiger-liyonghu/insurance-news/blob/main/data.json
   - 查看文件内容是否已更新（应该包含 articles 数组）

3. **刷新网站页面**：
   - https://tiger-liyonghu.github.io/insurance-news/
   - 按 F5 或 Cmd+R 刷新

## 快速检查清单

- [ ] GitHub Secrets 已配置（NEWS_API_KEY, GEMINI_API_KEY）
- [ ] `.github/workflows/update.yml` 文件存在
- [ ] GitHub Actions 工作流已创建
- [ ] 已手动触发一次工作流
- [ ] 工作流运行成功（绿色 ✅）
- [ ] `data.json` 文件已更新
- [ ] 网站页面已刷新

## 如果仍然无法解决

1. **查看详细日志**：
   - Actions 页面 → 点击运行记录 → 查看每个步骤的日志

2. **检查 API Keys**：
   - 确认 NewsAPI Key 有效
   - 确认 Gemini API Key 有效

3. **检查仓库设置**：
   - Settings → Actions → General
   - 确保 "Allow all actions and reusable workflows" 已启用

4. **联系支持**：
   - 提供 Actions 运行日志
   - 提供错误信息截图

## 预期结果

成功运行后：
- ✅ Actions 显示绿色成功状态
- ✅ `data.json` 文件包含新闻数据
- ✅ 网站页面显示新闻列表
- ✅ 每小时自动更新一次
