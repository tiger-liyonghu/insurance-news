# 🔧 GitHub Actions 故障排除指南

## 常见错误及解决方案

### 错误 1: Process completed with exit code 1

**可能原因**：
1. 缺少必要的 API Keys
2. API Keys 无效或过期
3. 依赖安装失败
4. 脚本执行错误

**解决步骤**：

#### 步骤 1: 检查 Secrets 是否已添加

1. 进入 GitHub 仓库
2. Settings → Secrets and variables → Actions
3. 确认以下 5 个 Secrets 都存在：
   - ✅ `TAVILY_API_KEY`
   - ✅ `GEMINI_API_KEY`
   - ✅ `DEEPSEEK_API_KEY`（可选，但推荐）
   - ✅ `SUPABASE_URL`
   - ✅ `SUPABASE_KEY`

#### 步骤 2: 查看详细错误日志

1. 进入 Actions 标签
2. 点击失败的运行记录
3. 点击 "scout" job
4. 展开各个步骤查看详细错误：

   **"Verify environment variables"** 步骤：
   - 如果显示 "⚠️ XXX is not set"，说明该 Secret 未添加或为空
   - 如果显示 "✅ All required environment variables are set"，说明 Secrets 配置正确

   **"Install dependencies"** 步骤：
   - 如果失败，可能是 requirements.txt 中的包版本问题
   - 查看具体错误信息

   **"Run Living Scout"** 步骤：
   - 查看完整的错误输出
   - 常见错误：
     - `❌ 错误: 缺少必要的 API Key` → 检查 Secrets
     - `ModuleNotFoundError` → 依赖安装失败
     - `403` 或 `401` → API Key 无效
     - `429` → API 限额

#### 步骤 3: 验证 API Keys

**Tavily API Key**:
- 访问 https://tavily.com/
- 检查 API Key 是否有效
- 检查配额是否充足

**Gemini API Key**:
- 访问 https://makersuite.google.com/app/apikey
- 检查 API Key 是否有效
- 检查是否达到每日限额（免费版 20 次/天）

**Supabase**:
- 访问 https://supabase.com/dashboard
- 检查项目是否正常
- 检查 API Key 是否正确

---

### 错误 2: ModuleNotFoundError

**原因**: 依赖包未正确安装

**解决**:
1. 检查 `requirements.txt` 是否包含所有依赖
2. 查看 "Install dependencies" 步骤的日志
3. 如果某个包安装失败，可能需要更新版本号

---

### 错误 3: API 限额错误 (429)

**原因**: API 调用次数超过限制

**解决**:
- **Gemini**: 等待配额重置（通常每天重置）或升级计划
- **Tavily**: 检查配额或升级计划
- 系统会自动切换到 DeepSeek 备份引擎（如果配置了）

---

### 错误 4: 数据库连接失败

**错误信息**: `❌ Supabase 未初始化` 或连接错误

**解决**:
1. 检查 `SUPABASE_URL` 是否正确（格式：`https://xxx.supabase.co`）
2. 检查 `SUPABASE_KEY` 是否正确
3. 确认 Supabase 项目是否正常运行
4. 检查数据库表是否已创建

---

## 调试技巧

### 1. 查看完整日志

在 Actions 页面：
1. 点击失败的运行
2. 点击 "scout" job
3. 展开 "Run Living Scout" 步骤
4. 查看完整的输出日志

### 2. 本地测试

在本地运行脚本，模拟 GitHub Actions 环境：

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

# 设置环境变量（使用你的实际值）
export TAVILY_API_KEY="your_key"
export GEMINI_API_KEY="your_key"
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"

# 运行脚本
python3 agent_v4_living_scout.py
```

### 3. 检查依赖版本

```bash
# 查看已安装的包版本
pip list | grep -E "(tavily|supabase|google-generativeai|openai)"
```

---

## 最新修复

已修复的问题：
- ✅ 改进了错误处理，脚本在错误时会正确退出
- ✅ 添加了环境变量验证步骤
- ✅ 添加了依赖安装验证
- ✅ 改进了日志输出

---

## 如果问题仍然存在

1. **查看最新运行日志**：进入 Actions → 最新的运行记录 → 查看详细错误
2. **检查 Secrets**：确认所有 Secrets 都已正确添加
3. **验证 API Keys**：确认 API Keys 有效且未过期
4. **本地测试**：在本地运行脚本，查看具体错误

---

## 成功运行的标志

如果运行成功，你应该看到：

```
======================================================================
🌐 GIFIA v4.0 - The Living Scout (24/7 全球自动侦察)
⏰ 执行时间: ...
======================================================================
📋 已加载 X 个监控域名
🔥 步骤1: 热点案例搜索（News 模式）
...
📡 步骤2: 常规案例搜索
...
📊 侦察完成统计
✅ 成功保存: X 个案例
⏭️  跳过（重复）: X 个案例
❌ 失败: X 个案例
======================================================================
```

---

**如果仍有问题，请提供具体的错误日志，我会帮你进一步诊断！**
