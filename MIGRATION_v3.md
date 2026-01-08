# 🚀 GIFIA v3.0 升级指南 - 深度协作模式

## 📋 从 v2.0 升级到 v3.0

v3.0 版本引入了**深度协作模式**，使用 Firecrawl 进行全文抓取，大幅提升了数据提取质量。

---

## 🎯 核心改进

### 1. 深度协作架构升级

| Agent | v2.0 | v3.0 | 改进点 |
|-------|------|------|--------|
| **Scout** | ✅ Tavily 搜索 | ✅ Tavily 高级搜索 | 保持不变 |
| **Researcher** | ⚠️ Jina Reader（可选） | ✅ **Firecrawl（必需）** | ✅ Markdown 格式全文<br>✅ 更高抓取质量 |
| **Analyst** | ✅ Gemini 分析 | ✅ **Gemini 1.5 Pro 深度分析** | ✅ 强调破绽细节<br>✅ 400+ 字详细描述 |
| **Validator** | ⚠️ GPT-4o-mini（可选） | ✅ **内置 Validator Agent** | ✅ 检查6个维度<br>✅ 质量评分<br>✅ 低质量重试 |

### 2. 主要变化

#### 文件变化
- ✅ 新增 `agent_v3.py` - 深度协作版本
- ✅ 保留 `agent_v2.py` - v2.0 版本（向后兼容）
- ✅ 更新 `requirements.txt` - 添加 firecrawl-py
- ✅ 更新 `config.example.py` - 新增 FIRECRAWL_API_KEY

#### API 变化
- ✅ **新增必需**: `FIRECRAWL_API_KEY` - Firecrawl API（必需）
- ❌ 不再需要: `JINA_API_KEY` - 被 Firecrawl 替代
- ❌ 不再需要: `OPENAI_API_KEY` - 被内置 Validator 替代

---

## 🔧 安装步骤

### 步骤 1: 安装新依赖

```bash
pip install -r requirements.txt
```

**新增依赖**:
- `firecrawl-py>=0.0.16` - Firecrawl API 客户端

### 步骤 2: 申请 Firecrawl API Key（必需）

1. **访问 Firecrawl**: https://firecrawl.dev/
2. **注册账号**（支持 GitHub/Google 登录）
3. **进入 Dashboard**，复制 API Key
4. **免费额度**: 请查看官网

### 步骤 3: 设置环境变量

#### 永久设置（推荐）

编辑 `~/.zshrc` 或 `~/.bashrc`：

```bash
# v2.0 已有的环境变量
export TAVILY_API_KEY="your_tavily_key"
export GEMINI_API_KEY="your_gemini_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"

# v3.0 新增的环境变量（必需）
export FIRECRAWL_API_KEY="your_firecrawl_key"
```

重新加载配置：
```bash
source ~/.zshrc
```

---

## 🎮 使用方法

### 运行 v3.0 版本（深度协作模式）

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"
python3 agent_v3.py
```

### 运行 v2.0 版本（向后兼容）

```bash
python3 agent_v2.py  # 仍然可以使用
```

---

## 📊 对比 v2.0

| 特性 | v2.0 | v3.0 |
|------|------|------|
| **全文抓取** | Jina Reader（可选） | ✅ Firecrawl（必需） |
| **抓取格式** | 纯文本 | ✅ Markdown 格式 |
| **抓取质量** | 依赖 Jina | ✅ 更高质量 |
| **质量检查** | GPT-4o-mini（可选） | ✅ 内置 Validator |
| **破绽细节** | 基础提取 | ✅ **深度挖掘** |
| **Process 字数** | 300+ 字 | ✅ **400+ 字** |
| **查重机制** | URL 去重 | ✅ URL + 标题相似度 |
| **低质量处理** | 直接跳过 | ✅ 标记并建议重试 |
| **日志输出** | 基础日志 | ✅ **详细实时日志** |

---

## 🔍 深度协作流程

### 完整流程

```
┌─────────────────────────────────────────────────────┐
│ Step 1: Scout Agent (搜索)                          │
│ - Tavily Advanced 搜索                              │
│ - 专业关键词增强                                    │
│ - 质量分数排序                                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: Researcher Agent (深度抓取)                │
│ - Firecrawl 抓取 Markdown 全文                      │
│ - 排除导航、页脚、页眉                              │
│ - 必须获取完整内容（严禁只看摘要）                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: Analyst Agent (深度分析)                   │
│ - Gemini 1.5 Pro 处理 Markdown 全文                 │
│ - 提取 6 个维度：时间、地区、人物、事件、经过、结果 │
│ - **特别挖掘：破绽细节 (The Red Flag)**             │
│ - Process 字段：400+ 字，破绽细节 150+ 字           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: Validator Agent (质量校验)                 │
│ - 检查 6 个维度的完整性                             │
│ - 特别检查 Process 字段质量                         │
│ - 质量评分（0-1）                                  │
│ - 低质量案例：标记并建议重试                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
          查重检查 + 保存到数据库
```

### 详细日志输出

v3.0 增加了详细的实时日志：

```
🔍 [Scout] 正在执行高级搜索...
📥 [Researcher] 正在深度扫描: [URL]...
   🔄 调用 Firecrawl 提取 Markdown 全文...
🧠 [Analyst] Gemini 正在分析卷宗...
   📄 分析内容: XXXX 字符 Markdown 全文
   💡 特别关注：破绽细节 (The Red Flag) 挖掘...
🔍 [Validator] 正在校验提取结果质量...
```

---

## ⚙️ 配置选项

### 修改处理数量

编辑 `agent_v3.py`：

```python
# 在 main() 函数中
search_results = scout.search(max_results=15)  # 修改搜索数量

# 在 deep_research_flow() 函数中
results = deep_research_flow(search_results, max_cases=3)  # 修改处理数量
```

### 修改质量阈值

编辑 `agent_v3.py` 的 `ValidatorAgent.validate()` 方法：

```python
# 总体质量分数阈值
is_valid = overall_score >= 0.7  # 修改阈值（0-1）

# Process 字段质量阈值
process_score >= 0.6  # 修改阈值（0-1）
```

### 修改等待时间

```python
# 在 deep_research_flow() 函数中
wait_time = 15  # 修改等待时间（秒）
```

---

## ⚠️ 注意事项

### 1. API 成本

v3.0 版本使用了 Firecrawl API：
- **Firecrawl**: 每次全文抓取
- **Gemini 1.5 Pro**: 处理更长文本（Markdown 全文）

建议：
- 监控 Firecrawl API 使用量
- 根据需要调整处理数量
- 确保 API 配额充足

### 2. 执行时间

v3.0 版本处理时间更长（因为增加了深度抓取）：
- **v2.0**: 约 5-10 分钟（3 个案例）
- **v3.0**: 约 8-15 分钟（3 个案例）

### 3. 向后兼容

- ✅ `agent_v2.py` (v2.0) 仍然可用
- ✅ 数据库结构不变
- ✅ `app.py` Web 展示页面兼容
- ✅ 可以同时运行 v2.0 和 v3.0

---

## 🐛 故障排除

### 问题 1: Firecrawl API 失败

**症状**: 看到 "❌ [Researcher] Firecrawl API Key 未设置" 或 "❌ [Researcher] 深度扫描失败"

**解决**:
- 检查 `FIRECRAWL_API_KEY` 是否正确设置
- 确认 Firecrawl API 配额是否充足
- 验证 API Key 是否有效

### 问题 2: 导入错误

**症状**: `ImportError: cannot import name 'FirecrawlApp'`

**解决**:
```bash
pip install --upgrade firecrawl-py
```

### 问题 3: 质量验证失败

**症状**: 看到 "⚠️ [Validator] 验证未通过"

**解决**:
- 检查 Gemini API 提取质量
- 可能需要调整质量阈值
- 检查源网页内容是否完整

---

## 📚 相关文档

- **完整功能文档**: `VERSION_1.0.md`
- **v2.0 升级指南**: `MIGRATION_v2.md`
- **快速开始指南**: `QUICKSTART.md`
- **使用指南**: `USAGE.md`

---

## ✅ 迁移检查清单

- [ ] 安装新依赖: `pip install -r requirements.txt`
- [ ] 申请 Firecrawl API Key（必需）
- [ ] 设置环境变量 `FIRECRAWL_API_KEY`
- [ ] 测试运行: `python3 agent_v3.py`
- [ ] 验证数据质量（检查数据库中保存的案例）
- [ ] 查看日志输出（确认深度协作流程正常）

---

## 🎉 新功能亮点

### 1. Firecrawl 深度抓取
- ✅ Markdown 格式全文
- ✅ 自动排除导航、页脚、页眉
- ✅ 更高抓取质量

### 2. 破绽细节深度挖掘
- ✅ 专门强调破绽细节 (The Red Flag)
- ✅ Process 字段 400+ 字详细描述
- ✅ 破绽细节部分 150+ 字

### 3. 智能质量校验
- ✅ 检查 6 个维度完整性
- ✅ 质量评分系统（0-1）
- ✅ 低质量案例标记和重试建议

### 4. 增强查重机制
- ✅ URL 完全匹配
- ✅ 标题相似度检查（85% 阈值）
- ✅ 避免重复抓取

### 5. 详细日志输出
- ✅ 实时进度提示
- ✅ 每个 Agent 的状态信息
- ✅ 质量评分和问题提示

---

**升级完成！现在可以使用 v3.0 的深度协作模式了！** 🎉
