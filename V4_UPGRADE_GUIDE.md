# 🚀 GIFIA v4.0 升级指南 - 24/7 全球自动侦察与用户众包

## 概述

v4.0 版本实现了完整的 24/7 全球自动侦察系统和用户众包功能，包括递归扫描、热点抓取、专家准入闸门和自动脱敏。

---

## 🎯 核心功能

### 1. The Living Scout（递归扫描与热点抓取）

#### 递归扩散
- ✅ 自动提取已抓取文章中的外部引用链接
- ✅ 识别 `.org` 或 `.gov` 域名，自动加入监控白名单
- ✅ 对监控域名的链接进行深度抓取

#### 热点响应
- ✅ 接入 Tavily 的 `search_depth='news'` 模式
- ✅ 每 30 分钟进行一次关键词检索
- ✅ 发现突发的高关注度保险案例立即深度抓取

**文件**: `agent_v4_living_scout.py`

### 2. User Submission & Gatekeeper（用户上传模块）

#### 文件支持
- ✅ 支持 PDF/DOCX 上传
- ✅ 自动提取文本内容

#### 专家准入闸门
- ✅ 基于 LLM 检查上传内容是否符合"保险欺诈/逆选择/滥用"定义
- ✅ 判定险种类型：寿险、重疾、或医疗险
- ✅ 自动脱敏：识别并遮蔽 PII 信息，仅保留红旗指标和舞弊细节

#### 状态流转
- ✅ 通过验证的入库并标记为 `source='user_submission'`

**文件**: `user_submission_module.py` + `app.py`（新增提交页面）

### 3. 专业结构化摘要升级

所有新增案例（无论来自网络还是用户）必须提取以下五个维度：

1. **【风险画像】** - 投保背景、保额、异常出险间隔
2. **【舞弊手法(MO)】** - 具体欺诈手段
3. **【红旗指标(Red Flags)】** - 触发警报的异常指标
4. **【核查手段建议】** - 确证方式和调查方法
5. **【核保/风控启示】** - 预警价值和风控建议

### 4. 自动化调度

- ✅ GitHub Actions 配置文件
- ✅ 每 30 分钟自动执行一次
- ✅ 支持手动触发

**文件**: `.github/workflows/living_scout.yml`

---

## 📋 安装步骤

### 步骤1: 更新数据库

在 Supabase SQL Editor 中执行：

```sql
-- 执行 database_v4_updates.sql
```

这将添加 `source` 字段，用于标记案例来源。

### 步骤2: 安装新依赖

```bash
pip install PyPDF2 python-docx
```

### 步骤3: 配置 GitHub Actions Secrets

在 GitHub 仓库设置中添加以下 Secrets：

- `TAVILY_API_KEY`
- `GEMINI_API_KEY`
- `DEEPSEEK_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### 步骤4: 启用 GitHub Actions

1. 将 `.github/workflows/living_scout.yml` 推送到仓库
2. GitHub Actions 将自动启用
3. 工作流将每 30 分钟执行一次

---

## 🔄 工作流程

### Living Scout 自动侦察流程

```
每30分钟触发
    ↓
1. 热点搜索（News 模式）
   - 搜索系统性欺诈、大规模欺诈等热点关键词
   - 高关注度案例立即深度抓取
    ↓
2. 常规搜索（Advanced 模式）
   - 搜索全球保险欺诈案例
    ↓
3. 递归扫描
   - 从每个案例中提取外部引用链接
   - 识别 .org/.gov 域名
   - 加入监控白名单
   - 深度抓取监控域名的链接
    ↓
4. 结构化提取（5维度格式）
    ↓
5. 保存到数据库（标记来源）
```

### 用户上传流程

```
用户上传 PDF/DOCX
    ↓
1. 文件读取
   - 提取文本内容
    ↓
2. 专家准入闸门
   - LLM 验证是否符合定义
   - 判定险种类型
   - 检查是否为具体案例
    ↓
3. 自动脱敏
   - 识别 PII 信息
   - 遮蔽个人身份信息
   - 保留红旗指标和舞弊细节
    ↓
4. 结构化提取（5维度格式）
    ↓
5. 用户确认
    ↓
6. 保存到数据库（source='user_submission'）
```

---

## 📊 数据库字段

### 新增字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `source` | TEXT | 案例来源：`auto_scout` / `hotspot` / `recursive` / `user_submission` |

### Source 值说明

- `auto_scout`: 常规自动侦察
- `hotspot`: 热点案例（News 模式）
- `recursive`: 递归扫描的外部链接
- `user_submission`: 用户上传

---

## 🎮 使用方法

### 运行 Living Scout（本地测试）

```bash
python3 agent_v4_living_scout.py
```

### 使用用户上传功能

1. 启动 Streamlit 应用：
   ```bash
   python3 -m streamlit run app.py
   ```

2. 在侧边栏选择"📤 提交情报"

3. 上传 PDF 或 DOCX 文件

4. 系统将自动：
   - 验证内容
   - 脱敏处理
   - 提取案例
   - 等待确认后入库

---

## ⚙️ 配置选项

### 修改热点搜索频率

编辑 `.github/workflows/living_scout.yml`：

```yaml
schedule:
  - cron: '*/30 * * * *'  # 每30分钟（可修改）
```

### 修改监控域名规则

编辑 `agent_v4_living_scout.py`：

```python
# 当前规则：.org 或 .gov
if domain.endswith('.org') or domain.endswith('.gov'):
    # 可以添加更多规则
```

### 修改热点关键词

编辑 `agent_v4_living_scout.py`：

```python
hotspot_keywords = [
    "systemic insurance fraud",
    "massive insurance fraud scheme",
    # 添加更多关键词
]
```

---

## 🔍 监控与日志

### GitHub Actions 日志

1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 查看 "GIFIA Living Scout" 工作流执行日志

### 本地运行日志

运行 `agent_v4_living_scout.py` 时，终端会显示：
- 热点搜索进度
- 递归扫描发现的链接
- 监控域名列表
- 保存统计信息

---

## ⚠️ 注意事项

### API 限额

- **Gemini**: 免费版每日 20 次请求
- **Tavily**: 根据计划限制
- **DeepSeek**: 根据账户余额

系统已实现 Failover 机制，Gemini 限额时自动切换到 DeepSeek。

### 文件大小限制

- PDF/DOCX 文件建议不超过 10MB
- 文本内容限制在 15000 字符以内（AI 处理）

### 隐私保护

- 所有用户上传的内容都会自动脱敏
- PII 信息会被遮蔽
- 仅保留案件相关的红旗指标和舞弊细节

---

## 📚 相关文件

### 核心文件
- `agent_v4_living_scout.py` - Living Scout 主程序
- `user_submission_module.py` - 用户上传模块
- `app.py` - Web 应用（已扩展用户上传页面）

### 配置文件
- `.github/workflows/living_scout.yml` - GitHub Actions 配置
- `database_v4_updates.sql` - 数据库扩展脚本

### 文档
- `SIU_FORMAT.md` - 5维度结构化摘要格式说明
- `V4_UPGRADE_GUIDE.md` - 本文档

---

## ✅ 升级检查清单

- [ ] 执行数据库扩展 SQL
- [ ] 安装新依赖（PyPDF2, python-docx）
- [ ] 配置 GitHub Actions Secrets
- [ ] 推送 GitHub Actions 配置文件
- [ ] 测试本地运行 Living Scout
- [ ] 测试用户上传功能
- [ ] 验证 GitHub Actions 自动执行

---

## 🎉 新功能亮点

1. **24/7 自动侦察**: 无需人工干预，系统自动监控全球保险欺诈案例
2. **递归扩散**: 自动发现并监控权威机构的链接
3. **热点响应**: 及时发现突发的高关注度案例
4. **用户众包**: 允许用户上传案例，扩大数据来源
5. **专家准入**: AI 自动验证上传内容质量
6. **自动脱敏**: 保护隐私，仅保留案件关键信息
7. **统一格式**: 所有案例使用 5 维度结构化摘要

---

**v4.0 升级完成！系统现已实现 24/7 全球自动侦察与用户众包功能！** 🚀
