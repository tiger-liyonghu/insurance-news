# Git 凭据重新配置指南

## 问题说明

当前 Personal Access Token 缺少 `workflow` 权限，导致无法推送 GitHub Actions workflow 文件。

## 解决方案

### 方法 1：更新现有 Token（推荐）

#### 步骤 1：创建新的 Personal Access Token（带 workflow 权限）

1. 访问 GitHub Token 设置页面：
   ```
   https://github.com/settings/tokens
   ```

2. 点击 **"Generate new token"** → **"Generate new token (classic)"**

3. 填写 Token 信息：
   - **Note**: `insurance-news-workflow` (或任意描述)
   - **Expiration**: 选择过期时间（建议 90 天或 No expiration）
   - **Select scopes**: 勾选以下权限：
     - ✅ `repo` (完整仓库访问权限)
     - ✅ `workflow` (更新 GitHub Action workflows) ⭐ **重要！**
     - ✅ `write:packages` (可选)

4. 点击 **"Generate token"**

5. **立即复制 Token**（只显示一次！）
   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

#### 步骤 2：更新 Git 凭据

**选项 A：使用 Git Credential Helper（推荐）**

```bash
# 清除旧的凭据
git credential-osxkeychain erase
host=github.com
protocol=https
# 按两次回车

# 或者使用以下命令清除
git config --global --unset credential.helper
```

**选项 B：直接在 URL 中使用新 Token**

```bash
cd /Users/tigerli/Desktop/insurance-news

# 更新远程仓库 URL，包含新 Token
git remote set-url origin https://你的新Token@github.com/tiger-liyonghu/insurance-news.git

# 例如：
# git remote set-url origin https://ghp_xxxxxxxxxxxx@github.com/tiger-liyonghu/insurance-news.git
```

**选项 C：使用 SSH（长期方案）**

```bash
# 1. 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 添加 SSH 密钥到 ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. 复制公钥
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容

# 4. 在 GitHub 添加 SSH 密钥
# 访问：https://github.com/settings/keys
# 点击 "New SSH key"，粘贴公钥

# 5. 更新远程仓库 URL 为 SSH
git remote set-url origin git@github.com:tiger-liyonghu/insurance-news.git
```

#### 步骤 3：测试推送

```bash
cd /Users/tigerli/Desktop/insurance-news

# 测试推送
git push origin main
```

### 方法 2：使用 GitHub CLI（最简单）

如果你安装了 GitHub CLI：

```bash
# 登录 GitHub
gh auth login

# 选择 GitHub.com
# 选择 HTTPS
# 选择使用浏览器登录或输入 Token

# 完成后，Git 会自动使用 gh 的凭据
```

## 验证配置

```bash
# 检查远程仓库 URL
git remote -v

# 测试推送（会提示输入凭据）
git push origin main
```

## 安全提示

⚠️ **重要安全建议**：

1. **不要将 Token 提交到代码仓库**
   - Token 只用于 Git 操作
   - 不要在代码中硬编码

2. **使用 Token 时注意**：
   - 如果使用 URL 方式，Token 会保存在 `.git/config` 中
   - 建议使用 SSH 或 Credential Helper

3. **定期轮换 Token**：
   - 定期更新 Token
   - 删除不再使用的 Token

## 故障排查

### 问题 1：仍然提示权限不足

**解决**：
- 确认 Token 已勾选 `workflow` 权限
- 重新生成 Token 并更新

### 问题 2：提示需要身份验证

**解决**：
```bash
# 清除缓存的凭据
git credential-osxkeychain erase
host=github.com
protocol=https
# 按两次回车

# 重新推送，会提示输入用户名和 Token
git push origin main
# Username: 输入你的 GitHub 用户名
# Password: 输入你的 Personal Access Token（不是密码！）
```

### 问题 3：Token 已过期

**解决**：
- 重新生成新 Token
- 更新 Git 配置

## 推荐方案

**最佳实践**：
1. 使用 **SSH 方式**（最安全，无需 Token）
2. 或使用 **GitHub CLI**（最简单）
3. 如果必须用 HTTPS，使用 Credential Helper 存储 Token

## 快速命令参考

```bash
# 查看当前远程 URL
git remote -v

# 更新为 HTTPS + Token
git remote set-url origin https://你的Token@github.com/tiger-liyonghu/insurance-news.git

# 更新为 SSH
git remote set-url origin git@github.com:tiger-liyonghu/insurance-news.git

# 清除凭据缓存
git credential-osxkeychain erase
```
