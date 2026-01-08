# 部署指南

## 方法 1: Netlify Drop（最简单，无需注册）

1. 访问 https://app.netlify.com/drop
2. 直接将 `index.html` 文件拖拽到页面
3. 立即获得公开网址（格式：`https://随机名称.netlify.app`）

## 方法 2: GitHub Pages（免费，需要 GitHub 账号）

1. 在 GitHub 创建新仓库
2. 上传 `index.html` 文件
3. 在仓库设置中启用 GitHub Pages
4. 选择 main 分支作为源
5. 访问：`https://你的用户名.github.io/仓库名/`

## 方法 3: Vercel（免费，推荐）

1. 访问 https://vercel.com
2. 使用 GitHub 账号登录
3. 点击 "New Project"
4. 导入包含 `index.html` 的文件夹
5. 立即部署，获得公开网址

## 方法 4: Cloudflare Pages（免费）

1. 访问 https://pages.cloudflare.com
2. 连接 GitHub 仓库或直接上传文件
3. 自动部署并获得公开网址

## 注意事项

⚠️ **重要**：部署前请确保 API Keys 的安全性
- 当前 API Keys 直接写在代码中，任何人都可以看到
- 建议使用环境变量或后端代理来保护 API Keys
