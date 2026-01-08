# 🚀 GIFIA v2.0 升级指南

## 📋 从 v1.0 升级到 v2.0

v2.0 版本采用了**多 Agent 协作模式**，大幅提升了数据提取质量。

---

## 🎯 核心改进

### 1. 多 Agent 协作架构

| Agent | 功能 | 技术栈 | 改进点 |
|-------|------|--------|--------|
| **The Scout** | 搜索高质量案例 | Tavily API | ✅ 添加专业关键词<br>✅ advanced 搜索模式<br>✅ 按质量分数排序 |
| **The Scraper** | 抓取全文内容 | Jina Reader | ✅ 获取完整网页内容<br>✅ 备用抓取方案<br>✅ 前3个高质量链接优先 |
| **The Analyst** | 深度分析提取 | Gemini 1.5 Pro | ✅ 强调破绽细节<br>✅ 明确信息缺失标注<br>✅ 300+ 字详细描述 |
| **The Critic** | 质量检查验证 | GPT-4o-mini | ✅ 虚构内容检测<br>✅ 准确率验证<br>✅ 置信度评分 |

### 2. 主要变化

#### 文件变化
- ✅ 新增 `agent_v2.py` - 多 Agent 协作版本
- ✅ 保留 `agent.py` - v1.0 版本（向后兼容）
- ✅ 更新 `requirements.txt` - 添加新依赖
- ✅ 更新 `config.example.py` - 新增 API Key 说明

#### API 变化
- ✅ 新增 `JINA_API_KEY` - Jina Reader API（可选）
- ✅ 新增 `OPENAI_API_KEY` - OpenAI API（可选，用于质检）
- ✅ 现有 API Key 保持不变

---

## 🔧 安装步骤

### 步骤 1: 安装新依赖

```bash
pip install -r requirements.txt
```

**新增依赖**:
- `openai>=1.0.0` - OpenAI API 客户端

### 步骤 2: 申请新的 API Key（可选但推荐）

#### Jina Reader API Key
- **申请地址**: https://jina.ai/
- **用途**: The Scraper - 全文内容抓取
- **免费额度**: 请查看官网
- **环境变量**: `JINA_API_KEY`

#### OpenAI API Key
- **申请地址**: https://platform.openai.com/api-keys
- **用途**: The Critic - 质量检查验证
- **免费额度**: 请查看官网（GPT-4o-mini 价格较低）
- **环境变量**: `OPENAI_API_KEY`

**注意**: 
- 这两个 API Key 是**可选的**
- 如果没有 Jina API Key，系统会使用备用抓取方法
- 如果没有 OpenAI API Key，系统会跳过质量检查

### 步骤 3: 设置环境变量

#### 永久设置（推荐）

编辑 `~/.zshrc` 或 `~/.bashrc`：

```bash
# v1.0 已有的环境变量
export TAVILY_API_KEY="your_tavily_key"
export GEMINI_API_KEY="your_gemini_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"

# v2.0 新增的环境变量（可选）
export JINA_API_KEY="your_jina_key"      # 可选
export OPENAI_API_KEY="your_openai_key"  # 可选
```

重新加载配置：
```bash
source ~/.zshrc
```

---

## 🎮 使用方法

### 运行 v2.0 版本

```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"
python3 agent_v2.py
```

### 运行 v1.0 版本（向后兼容）

```bash
python3 agent.py  # 仍然可以使用
```

---

## 📊 对比 v1.0

| 特性 | v1.0 | v2.0 |
|------|------|------|
| **搜索深度** | 基础搜索 | ✅ Advanced 搜索 + 专业关键词 |
| **内容来源** | 搜索摘要 | ✅ 全文内容（Jina Reader） |
| **提取质量** | 基础提取 | ✅ 深度分析（强调破绽） |
| **质量检查** | ❌ 无 | ✅ GPT-4o-mini 质检 |
| **处理数量** | 5-10 个 | 3 个高质量（深度处理） |
| **信息完整性** | 基础字段 | ✅ 明确信息缺失标注 |
| **破绽分析** | 简单描述 | ✅ 详细的三方面分析 |

---

## ⚙️ 配置选项

### 修改处理数量

编辑 `agent_v2.py`：

```python
# 修改搜索数量
search_results = scout.search(
    base_query="Global insurance fraud case 2025 2026",
    max_results=10  # 修改这里
)

# 修改处理的案例数量
top_links = search_results[:3]  # 修改数字，例如改为 [:5]
```

### 修改等待时间

```python
# 在 main() 函数中
wait_time = 15  # 修改等待时间（秒）
```

### 禁用某个 Agent

```python
# 禁用 Jina Reader（使用备用方法）
JINA_API_KEY = None

# 禁用质量检查
OPENAI_API_KEY = None
```

---

## 🔍 工作流程对比

### v1.0 工作流程

```
搜索 (Tavily) → 提取 (Gemini) → 存储 (Supabase)
```

### v2.0 工作流程

```
┌─────────────────────────────────────────────────────┐
│ Step 1: The Scout (搜索)                            │
│ - Tavily Advanced 搜索                              │
│ - 专业关键词增强                                    │
│ - 质量分数排序                                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: The Scraper (抓取)                         │
│ - 选择前3个高质量链接                               │
│ - Jina Reader 全文抓取                              │
│ - 备用方法（如果 Jina 失败）                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: The Analyst (分析)                         │
│ - Gemini 1.5 Pro 深度分析                           │
│ - 强调破绽细节                                      │
│ - 明确信息缺失标注                                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: The Critic (质检)                          │
│ - GPT-4o-mini 验证                                  │
│ - 虚构内容检测                                      │
│ - 置信度评分                                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
          存储到 Supabase 数据库
```

---

## ⚠️ 注意事项

### 1. API 成本

v2.0 版本使用了更多的 API 调用：
- **Jina Reader**: 每次全文抓取
- **OpenAI GPT-4o-mini**: 每次质量检查
- **Gemini 1.5 Pro**: 处理更长的全文内容

建议：
- 监控 API 使用量
- 根据需要调整处理数量
- 考虑使用备用方法（如果不设置 Jina/OpenAI Key）

### 2. 执行时间

v2.0 版本处理时间更长（因为增加了多个步骤）：
- **v1.0**: 约 2-5 分钟（5 个案例）
- **v2.0**: 约 5-10 分钟（3 个高质量案例）

### 3. 向后兼容

- ✅ `agent.py` (v1.0) 仍然可用
- ✅ 数据库结构不变
- ✅ `app.py` Web 展示页面兼容
- ✅ 可以同时运行 v1.0 和 v2.0

---

## 🐛 故障排除

### 问题 1: Jina Reader API 失败

**症状**: 看到 "⚠️ [Scraper] Jina API Key 未设置" 或 "❌ [Scraper] 抓取失败"

**解决**:
- 检查 `JINA_API_KEY` 是否正确设置
- 如果没有设置，系统会自动使用备用方法
- 确认 Jina Reader API 配额是否充足

### 问题 2: OpenAI API 失败

**症状**: 看到 "⚠️ [Critic] OpenAI API Key 未设置，跳过质检"

**解决**:
- 检查 `OPENAI_API_KEY` 是否正确设置
- 如果没有设置，系统会跳过质量检查（不影响流程）
- 确认 OpenAI API 配额是否充足

### 问题 3: Gemini API 限流

**症状**: 看到 "429 Quota exceeded"

**解决**:
- 增加等待时间（修改 `wait_time`）
- 减少处理数量（修改 `top_links[:3]`）
- 考虑升级 Gemini API 配额

---

## 📚 相关文档

- **完整功能文档**: `VERSION_1.0.md`
- **快速开始指南**: `QUICKSTART.md`
- **使用指南**: `USAGE.md`

---

## ✅ 迁移检查清单

- [ ] 安装新依赖: `pip install -r requirements.txt`
- [ ] 申请 Jina Reader API Key（可选）
- [ ] 申请 OpenAI API Key（可选）
- [ ] 设置环境变量（包括新的可选变量）
- [ ] 测试运行: `python3 agent_v2.py`
- [ ] 验证数据质量（检查数据库中保存的案例）

---

**升级完成！现在可以使用 v2.0 的多 Agent 协作模式了！** 🎉
