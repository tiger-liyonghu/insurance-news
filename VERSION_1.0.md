# 🛡️ GIFIA - 全球反保险欺诈联盟 云端情报站

## 📦 Version 1.0 版本文档

**版本号**: v1.0  
**发布日期**: 2026年1月8日  
**开发状态**: ✅ 稳定运行  
**文档类型**: 完整功能文档 & 存档

---

## 📋 目录

1. [项目概述](#项目概述)
2. [功能清单](#功能清单)
3. [技术架构](#技术架构)
4. [核心功能详解](#核心功能详解)
5. [数据模型](#数据模型)
6. [API 配置](#api-配置)
7. [部署说明](#部署说明)
8. [使用指南](#使用指南)
9. [已知问题与限制](#已知问题与限制)
10. [项目结构](#项目结构)
11. [性能指标](#性能指标)
12. [未来规划参考（2.0版本）](#未来规划参考20版本)

---

## 项目概述

### 项目名称
Global Insurance Fraud Intelligence Agent (GIFIA) - 全球反保险欺诈联盟云端情报站

### 项目目标
建立一个自动化系统，利用 AI Agent 全球搜集保险理赔欺诈案例，每小时更新一次，展示全球最新的深度欺诈案例分析。

### 核心价值
通过对"作案经过"和"破绽分析"的沉淀，建立行业 IP 和反欺诈案例库。

### 开发者
Yonghu LI - 资深保险专家

---

## 功能清单

### ✅ 已实现功能

#### 1. 自动化数据抓取
- ✅ 使用 Tavily API 全球搜索保险欺诈案例
- ✅ 支持自定义搜索关键词
- ✅ 可配置搜索数量（默认 5 个，避免 API 限流）
- ✅ 自动去重（基于 URL）

#### 2. AI 智能提取
- ✅ 使用 Google Gemini 2.5 Flash 模型提取结构化信息
- ✅ 自动翻译为中文
- ✅ 提取 6 个核心字段（详见数据模型）
- ✅ JSON 格式输出

#### 3. 数据存储
- ✅ Supabase 云端数据库持久化存储
- ✅ 自动去重机制（URL 唯一约束）
- ✅ 时间戳自动记录
- ✅ 支持按时间倒序查询

#### 4. Web 展示门户
- ✅ Streamlit 构建的极简 Web 界面
- ✅ 展示最新 6 个案例（可配置）
- ✅ 卡片式展示，支持展开查看详情
- ✅ 重点展示"作案经过"字段
- ✅ 显示数据统计和地区分布
- ✅ 响应式设计，支持移动端访问

#### 5. 自动化部署（可选）
- ✅ GitHub Actions 配置文件（每小时执行）
- ✅ 支持手动触发
- ✅ 自动化依赖安装和环境配置

#### 6. 工具和辅助功能
- ✅ 配置测试脚本（test_config.py）
- ✅ 数据库初始化 SQL 脚本
- ✅ 环境变量配置示例
- ✅ 完整的文档系统

### ❌ 未实现功能（计划在 2.0 版本）

- ⏳ 用户认证系统
- ⏳ 案例搜索和筛选功能
- ⏳ 数据导出功能（Excel/PDF）
- ⏳ 多语言支持切换
- ⏳ 邮件通知功能
- ⏳ 案例分类标签系统
- ⏳ 数据可视化图表
- ⏳ API 接口提供
- ⏳ 案例评论和讨论功能
- ⏳ 移动端原生应用

---

## 技术架构

### 技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **编程语言** | Python | 3.9+ | 核心开发语言 |
| **搜索引擎** | Tavily AI | API | 全球案例搜索 |
| **AI 提取** | Google Gemini | 2.5 Flash | 结构化信息提取 |
| **数据库** | Supabase (PostgreSQL) | Cloud | 数据持久化存储 |
| **Web 框架** | Streamlit | 1.50.0 | 前端展示页面 |
| **自动化** | GitHub Actions | - | CI/CD 定时任务 |
| **依赖管理** | pip | - | Python 包管理 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions                        │
│              (每小时自动触发一次)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    agent.py                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Tavily API  │→ │ Gemini API   │→ │  Supabase    │  │
│  │   (搜索)     │  │  (提取)      │  │  (存储)      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Supabase Database                           │
│          (fraud_cases 表)                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    app.py                                │
│              (Streamlit Web App)                         │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   用户浏览器                             │
│              http://localhost:8501                       │
└─────────────────────────────────────────────────────────┘
```

### 数据流

1. **搜索阶段**：Tavily API 搜索全球保险欺诈案例（约 5-10 个结果）
2. **提取阶段**：Gemini API 从每个搜索结果中提取结构化信息
3. **存储阶段**：Supabase 数据库存储，自动去重
4. **展示阶段**：Streamlit 从数据库读取并展示给用户

---

## 核心功能详解

### 1. agent.py - 数据抓取脚本

**文件路径**: `agent.py`

**主要功能**:
- 调用 Tavily API 搜索保险欺诈案例
- 使用 Gemini API 提取结构化信息
- 连接 Supabase 数据库存储数据
- 自动去重（基于 URL）

**核心函数**:

| 函数名 | 功能 | 参数 | 返回值 |
|--------|------|------|--------|
| `search_fraud_cases()` | 搜索案例 | query, max_results | 搜索结果列表 |
| `extract_case_info_with_gemini()` | 提取案例信息 | url, title, content | 结构化字典 |
| `check_duplicate()` | 检查重复 | url | True/False |
| `save_to_supabase()` | 保存到数据库 | case_data | True/False |
| `get_gemini_model()` | 获取可用模型 | - | Gemini 模型对象 |
| `main()` | 主函数 | - | - |

**关键配置**:
```python
# 搜索数量（避免 API 限流）
max_results = 5

# 案例处理间隔（秒）
sleep_time = 15

# 搜索关键词
query = "Global insurance fraud case 2025 2026"
```

**API 限流处理**:
- Gemini 免费版：每分钟 5 次请求
- 每个案例间隔 15 秒
- 默认只搜索 5 个案例

### 2. app.py - Web 展示页面

**文件路径**: `app.py`

**主要功能**:
- 从 Supabase 读取数据
- 展示最新 6 个案例（可配置）
- 卡片式布局，支持展开/收起
- 显示统计信息

**页面结构**:
- **标题区域**：项目名称和简介
- **侧边栏**：
  - 数据统计（总案例数）
  - 地区分布（Top 5）
  - 更新时间提示
- **主内容区**：
  - 案例卡片列表
  - 每个卡片包含：事件、地区、时间、涉案方、作案经过、判决结果

**核心函数**:

| 函数名 | 功能 | 参数 | 返回值 |
|--------|------|------|--------|
| `init_supabase()` | 初始化数据库连接 | - | Supabase 客户端 |
| `fetch_latest_cases()` | 获取最新案例 | limit | 案例列表 |
| `fetch_all_cases()` | 获取所有案例 | - | 案例列表 |
| `format_datetime()` | 格式化日期时间 | dt_str | 格式化字符串 |

### 3. test_config.py - 配置测试脚本

**文件路径**: `test_config.py`

**功能**:
- 测试所有 API Key 是否正确配置
- 验证 Supabase 数据库连接
- 检查数据库表是否存在

**使用方法**:
```bash
python3 test_config.py
```

### 4. database.sql - 数据库初始化脚本

**文件路径**: `database.sql`

**功能**:
- 创建 `fraud_cases` 表
- 创建索引优化查询
- 创建触发器自动更新时间戳

**表结构**:
```sql
CREATE TABLE fraud_cases (
    id BIGSERIAL PRIMARY KEY,
    time TEXT NOT NULL,
    region TEXT NOT NULL,
    characters TEXT NOT NULL,
    event TEXT NOT NULL,
    process TEXT NOT NULL,
    result TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 数据模型

### fraud_cases 表字段说明

| 字段名 | 类型 | 说明 | 必填 | 唯一 |
|--------|------|------|------|------|
| `id` | BIGSERIAL | 主键，自增 | ✅ | ✅ |
| `time` | TEXT | 事件发生或判决时间 | ✅ | ❌ |
| `region` | TEXT | 国家及城市 | ✅ | ❌ |
| `characters` | TEXT | 涉案人身份、保险公司、中介或医疗机构 | ✅ | ❌ |
| `event` | TEXT | 欺诈类型概括 | ✅ | ❌ |
| `process` | TEXT | 详细的作案手法、逃避初审的过程、以及被发现的破绽细节（重点字段） | ✅ | ❌ |
| `result` | TEXT | 判决结果、罚金或法律制裁 | ✅ | ❌ |
| `source_url` | TEXT | 原始链接 | ✅ | ✅ |
| `created_at` | TIMESTAMPTZ | 数据入库时间 | ✅ | ❌ |
| `updated_at` | TIMESTAMPTZ | 数据更新时间（自动） | ✅ | ❌ |

### 数据示例

```json
{
    "id": 1,
    "time": "2025-01-15",
    "region": "美国纽约",
    "characters": "John Smith, ABC保险公司, XYZ医疗中心",
    "event": "医疗保险欺诈",
    "process": "详细描述作案经过：他们如何实施欺诈，如何通过初审，最终如何被发现...",
    "result": "被判有期徒刑5年，罚款50万美元",
    "source_url": "https://example.com/case-1",
    "created_at": "2026-01-08T08:14:31+00:00",
    "updated_at": "2026-01-08T08:14:31+00:00"
}
```

---

## API 配置

### 必需的 API Key

#### 1. Tavily API Key
- **申请地址**: https://tavily.com/
- **免费额度**: 每月 1000 次搜索
- **用途**: 全球案例搜索
- **环境变量**: `TAVILY_API_KEY`

#### 2. Google Gemini API Key
- **申请地址**: https://makersuite.google.com/app/apikey
- **免费额度**: 每分钟 15 次请求（实际限制为 5 次/分钟/模型）
- **使用的模型**: `models/gemini-2.5-flash`
- **用途**: 结构化信息提取和翻译
- **环境变量**: `GEMINI_API_KEY`

#### 3. Supabase 配置
- **申请地址**: https://supabase.com/
- **免费额度**: 500MB 数据库，无限 API 请求
- **用途**: 数据存储
- **环境变量**: 
  - `SUPABASE_URL` - 项目 URL
  - `SUPABASE_KEY` - anon public key

### 环境变量配置

**永久设置（推荐）**:
```bash
# 编辑 ~/.zshrc 或 ~/.bashrc
export TAVILY_API_KEY="your_key"
export GEMINI_API_KEY="your_key"
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
```

**临时设置**:
```bash
export TAVILY_API_KEY="your_key"
export GEMINI_API_KEY="your_key"
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
```

---

## 部署说明

### 本地部署

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量
（参考上面的 API 配置部分）

#### 3. 初始化数据库
- 访问 Supabase Dashboard
- 在 SQL Editor 中执行 `database.sql`

#### 4. 测试配置
```bash
python3 test_config.py
```

#### 5. 运行系统
```bash
# 抓取数据
python3 agent.py

# 启动 Web 页面（新终端）
python3 -m streamlit run app.py
```

### GitHub Actions 自动化部署

**配置文件**: `.github/workflows/auto_scraper.yml`

**触发条件**:
- 每小时自动执行（Cron: `0 * * * *`）
- 支持手动触发

**设置步骤**:
1. 将代码推送到 GitHub
2. 在仓库 Settings > Secrets 中添加 4 个 API Key
3. 在 Actions 标签页手动触发一次

### Streamlit Cloud 部署

**步骤**:
1. 访问 https://share.streamlit.io/
2. 使用 GitHub 登录
3. 选择仓库和分支
4. 设置 Main file path: `app.py`
5. 在 Secrets 中添加 `SUPABASE_URL` 和 `SUPABASE_KEY`
6. 点击 Deploy

---

## 使用指南

### 快速开始

#### 步骤 1: 设置环境变量
```bash
# 永久设置（推荐）
nano ~/.zshrc
# 添加 4 个 export 语句
source ~/.zshrc
```

#### 步骤 2: 运行抓取脚本
```bash
cd "/Users/tigerli/Desktop/全球反保险欺诈联盟"
python3 agent.py
```

#### 步骤 3: 启动 Web 页面
```bash
# 在新终端
python3 -m streamlit run app.py
```

#### 步骤 4: 访问 Web 页面
打开浏览器访问: `http://localhost:8501`

### 常用操作

#### 手动抓取数据
```bash
python3 agent.py
```

#### 查看配置状态
```bash
python3 test_config.py
```

#### 停止 Streamlit
```bash
pkill -f streamlit
```

#### 查看数据库数据
- 访问 Supabase Dashboard
- 进入 Table Editor > fraud_cases

### 自定义配置

#### 修改搜索关键词
编辑 `agent.py`:
```python
search_results = search_fraud_cases(
    query="你的搜索关键词",  # 修改这里
    max_results=5
)
```

#### 修改展示案例数量
编辑 `app.py`:
```python
cases = fetch_latest_cases(limit=10)  # 修改数量
```

#### 修改抓取频率（GitHub Actions）
编辑 `.github/workflows/auto_scraper.yml`:
```yaml
schedule:
  - cron: '0 */2 * * *'  # 每 2 小时执行一次
```

---

## 已知问题与限制

### 当前版本限制

#### 1. API 限流问题
- **问题**: Gemini API 免费版限制每分钟 5 次请求
- **影响**: 每次只能处理约 5 个案例
- **解决方案**: 
  - 已增加延迟时间（15 秒/案例）
  - 已减少搜索数量为 5 个
  - 建议升级到付费版或使用多个 API Key 轮询

#### 2. Python 版本兼容性
- **问题**: 代码在 Python 3.9.6 上有兼容性警告
- **影响**: 不影响功能，但有警告信息
- **解决方案**: 建议升级到 Python 3.10+

#### 3. JSON 解析错误
- **问题**: 某些案例的 Gemini 返回格式不规范，导致解析失败
- **影响**: 极少数案例会提取失败
- **解决方案**: 已添加错误处理，失败的案例会被跳过

#### 4. 数据完整性
- **问题**: 部分案例的某些字段可能为"未知"或"待补充"
- **影响**: 数据质量取决于源网页内容质量
- **解决方案**: 可以手动补充数据或优化提取 prompt

### 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 每次抓取案例数 | 5 个 | 受 API 限流限制 |
| 抓取执行时间 | 2-5 分钟 | 取决于网络和 API 响应 |
| 单次抓取 API 调用 | ~5 次 Gemini | 避免限流 |
| 数据库查询响应 | < 1 秒 | Supabase 性能 |
| Web 页面加载时间 | < 2 秒 | Streamlit 渲染 |

---

## 项目结构

```
全球反保险欺诈联盟/
├── agent.py                    # 核心抓取脚本
├── app.py                      # Streamlit Web 展示页面
├── test_config.py              # 配置测试脚本
├── requirements.txt            # Python 依赖包
├── config.example.py           # 配置文件示例
├── database.sql                # 数据库初始化脚本
├── .gitignore                  # Git 忽略文件
├── .github/
│   └── workflows/
│       └── auto_scraper.yml    # GitHub Actions 配置
├── README.md                   # 项目说明文档
├── QUICKSTART.md              # 快速开始指南
├── USAGE.md                    # 使用指南
└── VERSION_1.0.md             # 本文件（版本文档）
```

### 文件说明

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `agent.py` | 核心抓取逻辑 | ⭐⭐⭐⭐⭐ |
| `app.py` | Web 展示页面 | ⭐⭐⭐⭐⭐ |
| `test_config.py` | 配置验证工具 | ⭐⭐⭐ |
| `database.sql` | 数据库表结构 | ⭐⭐⭐⭐ |
| `.github/workflows/auto_scraper.yml` | 自动化配置 | ⭐⭐⭐ |
| `requirements.txt` | 依赖管理 | ⭐⭐⭐⭐ |
| `README.md` | 项目文档 | ⭐⭐⭐ |
| `QUICKSTART.md` | 快速入门 | ⭐⭐⭐⭐ |
| `USAGE.md` | 使用指南 | ⭐⭐⭐⭐ |
| `VERSION_1.0.md` | 版本文档 | ⭐⭐⭐⭐⭐ |

---

## 技术债务

### 代码改进建议

1. **错误处理增强**
   - 添加重试机制（API 失败时）
   - 改进 JSON 解析错误处理
   - 添加日志记录系统

2. **性能优化**
   - 使用异步请求提高并发性能
   - 添加缓存机制减少 API 调用
   - 优化数据库查询

3. **代码质量**
   - 添加单元测试
   - 添加类型注解
   - 代码格式化（black, flake8）

4. **安全性**
   - API Key 加密存储
   - 添加访问日志
   - 防止 SQL 注入（虽然使用 ORM，但可以加强）

---

## 版本历史

### Version 1.0 (2026-01-08)

**初始发布**
- ✅ 实现基础抓取功能（Tavily + Gemini + Supabase）
- ✅ 实现 Web 展示页面（Streamlit）
- ✅ 实现自动化部署配置（GitHub Actions）
- ✅ 完整的文档系统
- ✅ 配置测试工具
- ✅ 数据库初始化脚本

**已知问题**:
- Gemini API 限流（每分钟 5 次）
- 部分案例提取失败（JSON 解析问题）
- Python 3.9 兼容性警告

---

## 未来规划参考（2.0版本）

### 功能增强

#### 1. 用户体验改进
- [ ] 添加用户登录/注册系统
- [ ] 个人收藏和订阅功能
- [ ] 案例评分和评论系统
- [ ] 搜索和筛选功能（按地区、类型、时间）
- [ ] 数据导出功能（Excel, PDF, CSV）
- [ ] 邮件通知（新案例提醒）

#### 2. 数据功能增强
- [ ] 案例分类标签系统
- [ ] 数据可视化（图表、趋势分析）
- [ ] 相似案例推荐
- [ ] 案例关联分析
- [ ] 多语言支持（英文、中文切换）
- [ ] 数据质量评分机制

#### 3. 技术架构升级
- [ ] 后端 API 服务（FastAPI/Django）
- [ ] 前端框架重构（React/Vue）
- [ ] 移动端原生应用（iOS/Android）
- [ ] 实时数据更新（WebSocket）
- [ ] 多数据源支持（不仅限于 Tavily）
- [ ] 分布式抓取（多个 Worker）

#### 4. 分析和智能功能
- [ ] 欺诈模式识别（AI 分析）
- [ ] 风险评分系统
- [ ] 趋势预测
- [ ] 自动生成报告
- [ ] 案例相似度匹配
- [ ] 智能分类和标签

#### 5. 企业功能
- [ ] 多租户支持
- [ ] 角色权限管理
- [ ] API 接口提供
- [ ] 数据白名单/黑名单
- [ ] 审计日志
- [ ] 数据备份和恢复

#### 6. 性能优化
- [ ] 异步处理（Celery/Redis）
- [ ] 缓存系统（Redis）
- [ ] CDN 加速
- [ ] 数据库读写分离
- [ ] 负载均衡

### 技术栈升级建议

- **后端**: FastAPI + PostgreSQL + Redis
- **前端**: React + TypeScript + Tailwind CSS
- **移动端**: React Native 或 Flutter
- **部署**: Docker + Kubernetes 或 Serverless
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack (Elasticsearch + Logstash + Kibana)

### 2.0 版本优先级建议

**高优先级（核心功能）**:
1. 搜索和筛选功能
2. 用户认证系统
3. 数据导出功能
4. 后端 API 服务

**中优先级（体验优化）**:
1. 数据可视化
2. 案例分类标签
3. 邮件通知
4. 多语言支持

**低优先级（高级功能）**:
1. 移动端应用
2. AI 分析功能
3. 企业功能
4. 分布式系统

---

## 联系与支持

### 开发者
**Yonghu LI** - 资深保险专家

### 文档版本
- **文档版本**: 1.0
- **最后更新**: 2026-01-08
- **维护状态**: ✅ 活跃维护

### 获取帮助
- 查看 `README.md` 了解项目概况
- 查看 `QUICKSTART.md` 快速开始
- 查看 `USAGE.md` 详细使用指南
- 运行 `python3 test_config.py` 检查配置

---

## 附录

### A. 依赖包列表

详见 `requirements.txt`:

```
supabase==2.3.4
google-generativeai==0.3.2
tavily-python==0.3.0
streamlit==1.31.0
requests==2.31.0
python-dateutil==2.8.2
```

### B. 环境变量清单

```bash
TAVILY_API_KEY       # Tavily 搜索 API Key
GEMINI_API_KEY       # Google Gemini API Key
SUPABASE_URL         # Supabase 项目 URL
SUPABASE_KEY         # Supabase anon public key
```

### C. 数据库索引

```sql
CREATE INDEX idx_fraud_cases_created_at ON fraud_cases(created_at DESC);
CREATE INDEX idx_fraud_cases_source_url ON fraud_cases(source_url);
CREATE INDEX idx_fraud_cases_region ON fraud_cases(region);
```

---

**文档结束**

---
*此文档为 Version 1.0 完整功能文档，用于存档和 2.0 版本开发参考。*
*最后更新: 2026-01-08*
