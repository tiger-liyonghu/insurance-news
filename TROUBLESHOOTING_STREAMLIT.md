# 🔧 Streamlit Cloud 部署故障排除

## 常见错误及解决方案

### 错误 1: ModuleNotFoundError

**错误信息**：
```
ModuleNotFoundError: No module named 'xxx'
```

**原因**：缺少依赖包

**解决**：
1. 检查 `requirements.txt` 是否包含所有依赖
2. 确保文件已推送到 GitHub
3. 在 Streamlit Cloud 设置中检查依赖安装日志

**修复**：更新 `requirements.txt`，确保包含：
```
streamlit>=1.31.0
supabase>=2.3.4
```

---

### 错误 2: 无法连接 Supabase

**错误信息**：
```
❌ 错误: 缺少 Supabase 配置
```
或
```
Connection error
```

**原因**：Secrets 未配置或配置错误

**解决**：
1. 进入应用 Settings → Secrets
2. 确认 Secrets 格式正确（TOML 格式）
3. 检查 URL 和 Key 是否正确
4. 保存后等待应用重新部署

**正确的 Secrets 格式**：
```toml
SUPABASE_URL = "https://wgprfrzbhdopznmkzwqu.supabase.co"
SUPABASE_KEY = "sb_publishable_8VNHdh-sybOa9KpWYMEpdg_k4yB1E8F"
```

---

### 错误 3: 文件未找到

**错误信息**：
```
FileNotFoundError: app_v5_redesigned.py
```

**原因**：Main file path 配置错误

**解决**：
1. 检查应用设置中的 "Main file path"
2. 确认应该是：`app_v5_redesigned.py`
3. 确认文件已推送到 GitHub

---

### 错误 4: 语法错误

**错误信息**：
```
SyntaxError: invalid syntax
```

**原因**：代码有语法错误

**解决**：
1. 在本地运行检查：
   ```bash
   python3 -m py_compile app_v5_redesigned.py
   ```
2. 修复错误后重新推送
3. Streamlit Cloud 会自动重新部署

---

### 错误 5: 数据库字段不存在

**错误信息**：
```
column "region_iso" does not exist
```

**原因**：数据库表未更新到 v5.0 结构

**解决**：
1. 在 Supabase SQL Editor 中执行 `migrate_to_v5.sql`
2. 验证迁移是否成功
3. 重新部署应用

---

## 🔍 如何查看错误日志

### 在 Streamlit Cloud 中：

1. 进入应用页面
2. 点击右上角 "⋮" (三个点)
3. 选择 "Settings"
4. 点击 "Logs" 标签
5. 查看详细错误信息

### 在本地测试：

```bash
# 运行应用查看错误
python3 -m streamlit run app_v5_redesigned.py

# 检查语法
python3 -m py_compile app_v5_redesigned.py
```

---

## 🛠️ 快速修复步骤

### 步骤 1: 检查代码

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"
python3 -m py_compile app_v5_redesigned.py
```

### 步骤 2: 检查依赖

```bash
# 查看 requirements.txt
cat requirements.txt
```

### 步骤 3: 本地测试

```bash
# 设置环境变量
export SUPABASE_URL="https://wgprfrzbhdopznmkzwqu.supabase.co"
export SUPABASE_KEY="sb_publishable_8VNHdh-sybOa9KpWYMEpdg_k4yB1E8F"

# 运行应用
python3 -m streamlit run app_v5_redesigned.py
```

### 步骤 4: 检查 GitHub

确认以下文件已推送：
- ✅ `app_v5_redesigned.py`
- ✅ `requirements.txt`

---

## 📋 请提供以下信息

为了更准确地帮你解决问题，请提供：

1. **错误信息**：完整的错误消息（从 Streamlit Cloud Logs 复制）
2. **错误位置**：在哪个步骤出错（部署时/运行时）
3. **应用 URL**：你的 Streamlit Cloud URL（如果有）

---

## 💡 常见问题快速检查

- [ ] `app_v5_redesigned.py` 文件是否存在？
- [ ] `requirements.txt` 是否包含所有依赖？
- [ ] Secrets 是否已正确配置？
- [ ] 数据库是否已迁移到 v5.0？
- [ ] 代码语法是否正确？

---

**请把具体的错误信息发给我，我会帮你快速解决！** 🔧
