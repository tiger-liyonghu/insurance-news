# 🔧 修复 Supabase API Key 问题

## 问题

诊断脚本显示：`❌ Supabase 初始化失败: Invalid API key`

## 解决方案

### 步骤 1: 获取正确的 Supabase API Key

1. 访问 Supabase Dashboard：https://supabase.com/dashboard
2. 选择你的项目（URL: `https://wgprfrzbhdopznmkzwqu.supabase.co`）
3. 点击左侧菜单 **Settings** → **API**
4. 在 **Project API keys** 部分，找到：
   - **anon public** key（这是你应该使用的）
   - 格式类似：`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` 或 `sb_publishable_...`

### 步骤 2: 更新 GitHub Secrets

1. 访问：https://github.com/tiger-liyonghu/insurance-news/settings/secrets/actions
2. 找到 **SUPABASE_KEY**
3. 点击右侧的 **编辑**（铅笔图标）
4. 粘贴正确的 **anon public** key
5. 点击 **Update secret**

### 步骤 3: 验证 SUPABASE_URL

同时检查 **SUPABASE_URL** 是否正确：
- 应该是：`https://wgprfrzbhdopznmkzwqu.supabase.co`
- 不要包含末尾的斜杠 `/`
- 不要包含路径

### 步骤 4: 重新运行

1. 进入 Actions 标签
2. 手动触发一次新的运行
3. 查看诊断输出，应该显示：
   - ✅ Supabase 客户端: 可以初始化并连接

---

## 常见错误

### 错误 1: 使用了 service_role key

**问题**: 使用了 `service_role` key 而不是 `anon public` key

**解决**: 使用 **anon public** key（更安全，有权限限制）

### 错误 2: Key 格式错误

**问题**: Key 不完整或包含额外字符

**解决**: 完整复制 key，不要添加空格或换行

### 错误 3: Key 已过期或被撤销

**问题**: Key 已被撤销或项目被删除

**解决**: 生成新的 API key

---

## 临时解决方案

如果暂时无法修复 Supabase API key，脚本仍会运行，只是：
- ⚠️ 无法保存数据到数据库
- ✅ 可以搜索和提取案例
- ✅ 可以显示结果（但不会持久化）

修复 API key 后，数据会自动保存。

---

## 验证 Key 是否正确

在 Supabase Dashboard 中：
1. Settings → API
2. 复制 **anon public** key
3. 确认格式正确（应该是长字符串，以 `eyJ` 或 `sb_` 开头）

---

**修复后，重新运行 GitHub Actions 即可！** ✅
