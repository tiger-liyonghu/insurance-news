# 📤 推送代码到 GitHub - 快速指南

## 当前状态

✅ Git 仓库已初始化
✅ 代码已提交
✅ workflow 文件已存在
⏳ 需要推送到 GitHub

---

## 步骤 1: 添加远程仓库

在终端运行以下命令（替换为你的实际 GitHub 仓库 URL）：

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

# 添加远程仓库（替换为你的实际 URL）
git remote add origin https://github.com/你的用户名/仓库名.git

# 验证
git remote -v
```

**示例**：
```bash
git remote add origin https://github.com/tigerli/gifia.git
```

---

## 步骤 2: 推送代码

```bash
# 添加所有文件（包括新创建的文档）
git add .

# 提交更改
git commit -m "Add GitHub Actions workflow and documentation"

# 推送到 GitHub
git push -u origin main
```

**注意**：如果 GitHub 仓库默认分支是 `master` 而不是 `main`，使用：
```bash
git push -u origin master
```

---

## 步骤 3: 验证推送成功

1. 打开你的 GitHub 仓库页面
2. 确认可以看到所有文件
3. 确认 `.github/workflows/living_scout.yml` 文件存在

---

## 步骤 4: 验证 GitHub Actions

1. 点击 **Actions** 标签
2. 应该看到 **"GIFIA Living Scout - 24/7 全球自动侦察"** 工作流
3. 点击 **"Run workflow"** 手动触发测试

---

## 如果遇到错误

### 错误：remote origin already exists

```bash
# 删除现有远程仓库
git remote remove origin

# 重新添加
git remote add origin https://github.com/你的用户名/仓库名.git
```

### 错误：failed to push

- 检查 GitHub 仓库 URL 是否正确
- 确认你有推送权限
- 检查网络连接

---

## 完成后的检查清单

- [ ] 代码已推送到 GitHub
- [ ] 可以看到所有文件
- [ ] `.github/workflows/living_scout.yml` 存在
- [ ] Actions 标签可见
- [ ] 5 个 Secrets 已添加
- [ ] 手动触发测试运行成功
