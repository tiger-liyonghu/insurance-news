# ✅ GitHub Actions 验证步骤

## 下一步：验证配置

### 步骤 1: 检查 Actions 是否可见

1. 在 GitHub 仓库页面，点击 **"Actions"** 标签（在顶部导航栏）
2. 你应该看到左侧菜单中有：
   - **"GIFIA Living Scout - 24/7 全球自动侦察"** 工作流

如果看不到 Actions 标签或工作流：
- 检查是否已推送 `.github/workflows/living_scout.yml` 文件
- 确认仓库已启用 Actions（Settings → Actions → General → Allow all actions）

---

### 步骤 2: 手动触发测试运行

1. 点击 **"GIFIA Living Scout - 24/7 全球自动侦察"** 工作流
2. 点击右侧的 **"Run workflow"** 按钮（绿色按钮）
3. 选择分支（通常是 `main` 或 `master`）
4. 点击 **"Run workflow"** 按钮

---

### 步骤 3: 查看运行日志

1. 点击刚创建的运行记录（会显示 "Queued" 或 "In progress"）
2. 等待几秒钟，状态会变为 "Running"
3. 点击 **"scout"** job（左侧）
4. 展开各个步骤查看详细日志：

   - ✅ **Checkout code** - 应该成功
   - ✅ **Set up Python** - 应该成功
   - ✅ **Install dependencies** - 应该成功
   - ✅ **Run Living Scout** - 查看执行日志
   - ✅ **Report results** - 应该显示完成时间

---

### 步骤 4: 检查执行结果

在 **"Run Living Scout"** 步骤的日志中，你应该看到：

```
======================================================================
🌐 GIFIA v4.0 - The Living Scout (24/7 全球自动侦察)
⏰ 执行时间: ...
======================================================================
🔥 步骤1: 热点案例搜索（News 模式）
...
📡 步骤2: 常规案例搜索
...
📊 侦察完成统计
✅ 成功保存: X 个案例
...
```

---

### 步骤 5: 验证自动调度

1. 在 Actions 页面，查看工作流列表
2. 确认调度配置显示：**"Scheduled: */30 * * * *"**（每30分钟）
3. 等待下一个调度时间（:00 或 :30），系统会自动运行

---

## 🎉 完成！

如果所有步骤都成功，你的系统现在：
- ✅ 每 30 分钟自动运行一次
- ✅ 自动搜索热点案例
- ✅ 自动保存到 Supabase 数据库
- ✅ 24/7 不间断运行

---

## 🔍 故障排除

### 问题：Actions 标签不可见

**解决**：
1. Settings → Actions → General
2. Actions permissions → 选择 "Allow all actions"
3. 点击 Save

### 问题：运行失败

**检查**：
1. 查看错误日志
2. 确认所有 Secrets 已正确添加
3. 验证 API Keys 是否有效

### 问题：没有自动运行

**原因**：
- 调度时间还没到（每小时的 :00 和 :30）
- 私有仓库可能需要 GitHub Pro（免费账户每月有 2000 分钟免费额度）

**解决**：
- 等待下一个调度时间
- 或手动触发运行

---

## 📊 监控运行状态

定期检查：
- Actions 标签 → 查看运行历史
- 绿色 ✅ = 成功
- 红色 ❌ = 失败（点击查看错误）
