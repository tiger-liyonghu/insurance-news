# 快速配置指南

## 当前问题
你的 Git 使用的 Token 缺少 `workflow` 权限，无法推送 workflow 文件。

## 快速解决（3 步）

### 第 1 步：创建新 Token

1. 访问：https://github.com/settings/tokens
2. 点击 **"Generate new token"** → **"Generate new token (classic)"**
3. 填写：
   - Note: `insurance-news-workflow`
   - 勾选权限：
     - ✅ `repo` (完整权限)
     - ✅ `workflow` ⭐ **必须勾选！**
4. 点击 **"Generate token"**
5. **立即复制 Token**（类似：`ghp_xxxxxxxxxxxxxxxxxxxx`）

### 第 2 步：更新 Git 配置

在终端执行：

```bash
cd /Users/tigerli/Desktop/insurance-news

# 替换 YOUR_NEW_TOKEN 为你在第 1 步复制的 Token
git remote set-url origin https://YOUR_NEW_TOKEN@github.com/tiger-liyonghu/insurance-news.git
```

**示例**（不要直接复制，替换为你的 Token）：
```bash
git remote set-url origin https://ghp_xxxxxxxxxxxxxxxxxxxx@github.com/tiger-liyonghu/insurance-news.git
```

### 第 3 步：测试推送

```bash
git push origin main
```

如果成功，说明配置完成！

## 验证

```bash
# 查看当前配置
git remote -v
# 应该显示新的 URL（包含新 Token）
```

## 注意事项

⚠️ **Token 安全**：
- Token 会保存在 `.git/config` 文件中
- 不要将 `.git/config` 提交到仓库
- 不要分享你的 Token

## 如果还有问题

查看详细文档：[GIT_CREDENTIALS_SETUP.md](./GIT_CREDENTIALS_SETUP.md)
