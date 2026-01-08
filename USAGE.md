# 🚀 GIFIA 系统使用指南

## 📋 当前配置状态

✅ **所有 API 已配置成功！**
- Tavily API: ✅ 正常
- Gemini API: ✅ 正常（使用 models/gemini-2.5-flash）
- Supabase: ✅ 正常（表已创建）

---

## 🎯 快速开始（3 步）

### 第一步：设置环境变量（每次打开新终端时都需要）

**方法 1：临时设置（当前终端会话有效）**

打开终端，执行以下命令：

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

export TAVILY_API_KEY=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
export GEMINI_API_KEY=AIzaSyBKx8I5FMyr3GKKMi7mnZt2HTSW1mr6EUo
export SUPABASE_URL=https://wgprfrzbhdopznmkzwqu.supabase.co
export SUPABASE_KEY=sb_publishable_8VNHdh-sybOa9KpWYMEpdg_k4yB1E8F
```

**方法 2：永久设置（推荐）**

将环境变量添加到你的 shell 配置文件中：

```bash
# 编辑配置文件
nano ~/.zshrc

# 在文件末尾添加以下内容：
export TAVILY_API_KEY=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
export GEMINI_API_KEY=AIzaSyBKx8I5FMyr3GKKMi7mnZt2HTSW1mr6EUo
export SUPABASE_URL=https://wgprfrzbhdopznmkzwqu.supabase.co
export SUPABASE_KEY=sb_publishable_8VNHdh-sybOa9KpWYMEpdg_k4yB1E8F

# 保存文件（按 Ctrl+X，然后 Y，然后 Enter）
# 重新加载配置
source ~/.zshrc
```

---

### 第二步：运行抓取脚本（收集案例数据）

```bash
# 确保在项目目录中
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

# 确保环境变量已设置（如果没永久设置的话）
export TAVILY_API_KEY=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
export GEMINI_API_KEY=AIzaSyBKx8I5FMyr3GKKMi7mnZt2HTSW1mr6EUo
export SUPABASE_URL=https://wgprfrzbhdopznmkzwqu.supabase.co
export SUPABASE_KEY=sb_publishable_8VNHdh-sybOa9KpWYMEpdg_k4yB1E8F

# 运行抓取脚本
python3 agent.py
```

**预期输出：**
```
============================================================
🚀 GIFIA - 全球保险欺诈情报抓取开始
⏰ 执行时间: 2026-01-08 XX:XX:XX
============================================================

📡 步骤1: 搜索全球保险欺诈案例...
✅ 搜索到 10 个结果

🔍 步骤2: 开始提取案例信息（共 10 个）...
✅ 使用 Gemini 模型: models/gemini-2.5-flash
✅ 成功提取案例: [案例名称]
✅ 成功保存到数据库: [案例名称]
...

============================================================
📊 抓取完成统计
============================================================
✅ 成功保存: X 个案例
⏭️  跳过（重复）: X 个案例
❌ 失败: X 个案例
📈 总计处理: 10 个搜索结果
============================================================
```

**执行时间：** 约 2-5 分钟（取决于网络和 API 响应速度）

---

### 第三步：启动 Web 展示页面（查看案例）

**在新终端窗口中运行：**

```bash
# 进入项目目录
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"

# 确保环境变量已设置（如果没永久设置的话）
export SUPABASE_URL=https://wgprfrzbhdopznmkzwqu.supabase.co
export SUPABASE_KEY=sb_publishable_8VNHdh-sybOa9KpWYMEpdg_k4yB1E8F

# 启动 Streamlit Web 应用
python3 -m streamlit run app.py
```

**预期输出：**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

浏览器会自动打开，如果没有，手动访问：**http://localhost:8501**

---

## 📖 使用场景

### 场景 1：手动抓取（每日或每周）

1. **打开终端**
2. **设置环境变量**（如果没永久设置）
3. **运行抓取脚本**：`python3 agent.py`
4. **等待完成**（约 2-5 分钟）
5. **启动 Web 页面**：`python3 -m streamlit run app.py`
6. **查看最新案例**

### 场景 2：持续运行（展示页面保持开启）

1. **启动 Streamlit**（让它一直运行）
   ```bash
   python3 -m streamlit run app.py
   ```
2. **定期运行抓取脚本**（每次运行时，页面会自动显示最新数据）
   ```bash
   python3 agent.py
   ```

---

## ⚙️ 高级配置

### 自定义搜索关键词

编辑 `agent.py` 文件，找到 `search_fraud_cases()` 调用：

```python
# 修改搜索关键词（第 245 行左右）
search_results = search_fraud_cases(
    query="Global insurance fraud case 2025 2026",  # 修改这里
    max_results=10  # 修改搜索数量（建议 5-15）
)
```

### 修改抓取数量

在 `agent.py` 的 `main()` 函数中：

```python
search_results = search_fraud_cases(
    query="Global insurance fraud case 2025 2026",
    max_results=15  # 增加或减少搜索数量
)
```

### 修改展示案例数量

编辑 `app.py` 文件，找到 `fetch_latest_cases()` 调用：

```python
# 修改展示的案例数量（第 42 行左右）
cases = fetch_latest_cases(limit=10)  # 修改为 10 个
```

---

## 🔄 自动化部署（可选）

### 使用 GitHub Actions 自动抓取（每小时）

1. **将代码推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin [你的GitHub仓库URL]
   git push -u origin main
   ```

2. **设置 GitHub Secrets**
   - 进入 GitHub 仓库
   - 点击 **Settings** > **Secrets and variables** > **Actions**
   - 点击 **New repository secret**
   - 添加以下 4 个 Secrets：
     - `TAVILY_API_KEY`: `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`
     - `GEMINI_API_KEY`: `AIzaSyBKx8I5FMyr3GKKMi7mnZt2HTSW1mr6EUo`
     - `SUPABASE_URL`: `https://wgprfrzbhdopznmkzwqu.supabase.co`
     - `SUPABASE_KEY`: `sb_publishable_8VNHdh-sybOa9KpWYMEpdg_k4yB1E8F`

3. **启用 GitHub Actions**
   - 进入 **Actions** 标签页
   - 首次需要手动点击 **"Run workflow"** 触发

### 使用 Streamlit Cloud 部署展示页面

1. **访问 Streamlit Cloud**: https://share.streamlit.io/
2. **使用 GitHub 登录**
3. **点击 "New app"**
4. **配置应用**:
   - Repository: 选择你的仓库
   - Branch: `main`
   - Main file path: `app.py`
5. **添加 Secrets**:
   - 点击 **Advanced settings**
   - 添加以下 2 个 Secrets（只需要 Supabase 的）:
     - `SUPABASE_URL`: `https://wgprfrzbhdopznmkzwqu.supabase.co`
     - `SUPABASE_KEY`: `sb_publishable_8VNHdh-sybOa9KpWYMEpdg_k4yB1E8F`
6. **点击 Deploy**

---

## ❓ 常见问题

### Q1: 运行 `python3 agent.py` 报错 "No module named 'xxx'"

**解决**：
```bash
pip3 install -r requirements.txt
```

### Q2: 运行 `streamlit run app.py` 报错

**解决**：
```bash
python3 -m streamlit run app.py
```

### Q3: 抓取时提示 "API Key 未设置"

**解决**：
- 检查环境变量是否已设置：`echo $GEMINI_API_KEY`
- 如果为空，重新设置环境变量（参考第一步）

### Q4: Web 页面显示空白或没有案例

**解决**：
1. 确认已经运行过 `python3 agent.py` 抓取数据
2. 检查 Supabase 数据库中是否有数据
3. 查看 Streamlit 控制台的错误信息

### Q5: 想修改抓取频率

**解决**：
- 编辑 `.github/workflows/auto_scraper.yml`
- 修改 Cron 表达式（例如：每天运行一次：`0 0 * * *`）

---

## 📊 监控和维护

### 查看数据库中的数据

1. 访问 Supabase Dashboard: https://supabase.com/dashboard
2. 选择你的项目
3. 点击 **Table Editor** > **fraud_cases**
4. 查看所有已保存的案例

### 检查 API 使用量

- **Tavily**: https://tavily.com/dashboard（查看剩余配额）
- **Gemini**: https://makersuite.google.com/app/apikey（查看使用量）
- **Supabase**: Dashboard > Settings > Usage（查看数据库使用情况）

---

## 🎉 完成！

现在你可以开始使用系统了。建议的首次使用流程：

1. ✅ 设置环境变量（永久设置，只需一次）
2. ✅ 运行 `python3 agent.py` 抓取第一批案例
3. ✅ 运行 `python3 -m streamlit run app.py` 查看案例
4. ✅ 根据需要设置自动化（GitHub Actions + Streamlit Cloud）

如有问题，请查看 `README.md` 或 `QUICKSTART.md` 获取更多帮助！
