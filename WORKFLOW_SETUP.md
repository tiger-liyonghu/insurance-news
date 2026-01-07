# GitHub Actions 工作流设置说明

## 问题

当前 Personal Access Token 缺少 `workflow` 权限，无法直接推送 workflow 文件。

## 解决方案

### 方法 1：更新 Personal Access Token（推荐）

1. 访问：https://github.com/settings/tokens
2. 找到你当前使用的 token，点击 **Edit** 或创建新 token
3. 在 **Select scopes** 中，勾选 **workflow** 权限
4. 更新 token 后，重新配置 Git 凭据

### 方法 2：在 GitHub 网页上手动创建（快速）

由于 workflow 文件无法通过当前 token 推送，请在 GitHub 网页上手动创建：

1. 访问：https://github.com/tiger-liyonghu/insurance-news
2. 点击 **Add file** → **Create new file**
3. 文件路径输入：`.github/workflows/update.yml`
4. 复制以下内容并粘贴：

```yaml
name: 自动更新新闻数据

on:
  # 每小时运行一次
  schedule:
    - cron: '0 * * * *'  # 每小时的整点运行
  # 代码推送时也运行（可选）
  push:
    branches:
      - main
    paths:
      - 'fetch_news.js'
      - '.github/workflows/update.yml'
  # 允许手动触发
  workflow_dispatch:

jobs:
  update-news:
    runs-on: ubuntu-latest
    
    steps:
      - name: 检出代码
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - name: 设置 Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: 安装依赖
        run: npm install

      - name: 运行数据抓取脚本
        env:
          NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GEMINI_MODEL: ${{ secrets.GEMINI_MODEL || 'gemini-1.5-flash' }}
        run: npm run fetch

      - name: 检查是否有变更
        id: check-changes
        run: |
          if [ -n "$(git status --porcelain data.json)" ]; then
            echo "has_changes=true" >> $GITHUB_OUTPUT
          else
            echo "has_changes=false" >> $GITHUB_OUTPUT
          fi

      - name: 提交并推送变更
        if: steps.check-changes.outputs.has_changes == 'true'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data.json
          git commit -m "🤖 自动更新: $(date +'%Y-%m-%d %H:%M:%S')" || exit 0
          git push

      - name: 完成
        if: steps.check-changes.outputs.has_changes == 'false'
        run: echo "✅ 数据无变更，跳过提交"
```

5. 点击 **Commit new file** 保存

## 重要提醒

⚠️ **在运行 workflow 之前，必须先配置 GitHub Secrets**：

1. 访问：https://github.com/tiger-liyonghu/insurance-news/settings/secrets/actions
2. 添加以下 Secrets：
   - `NEWS_API_KEY`
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL` (可选，默认为 `gemini-1.5-flash`)

详细步骤请查看 [SETUP.md](./SETUP.md)
