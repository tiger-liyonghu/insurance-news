# 🌱 种子案例库构建指南

## 概述

本指南说明如何从深度研究报告中提取案例，构建50个核心种子案例库。

---

## 📋 准备工作

### 1. 更新数据库表结构

首先需要在 Supabase 中执行数据库扩展脚本：

```sql
-- 在 Supabase SQL Editor 中执行
-- 文件：database_seed_cases.sql
```

这将添加以下字段：
- `line_of_business`: 险种
- `fraud_type`: 欺诈定性（Fraud/Abuse/Waste）
- `modus_operandi`: 舞弊手法
- `red_flags`: 红旗指标
- `investigative_tips`: 调查突破点
- `underwriting_advice`: 核保建议
- `is_seed_case`: 种子案例标记
- `last_shown_at`: 最后展示时间

### 2. 安装依赖

```bash
pip install python-docx
```

---

## 🔄 工作流程

### 步骤1: 从报告中提取案例

运行提取器脚本：

```bash
python3 seed_cases_extractor.py
```

**功能**：
- 读取4个Word研究报告
- 使用AI提取具体案例
- 转换为结构化格式
- 生成预览清单 `seed_cases_preview.json`

**注意事项**：
- 如果 Gemini API 达到限额，会自动切换到 DeepSeek
- 如果提取的案例不足50个，会启动外部搜索补充

### 步骤2: 检查预览清单

查看生成的 `seed_cases_preview.json` 文件，确认：
- ✅ 案例数量是否达到50个
- ✅ 案例信息是否完整
- ✅ 格式是否符合要求

**示例格式**：
```json
{
  "Time": "2024-01-15",
  "Region": "美国",
  "Characters": "DMERx公司, 多家保险公司",
  "Event": "DMERx 10亿美元医疗保险欺诈案",
  "Process": "【风险画像】\n...\n【舞弊手法(MO)】\n...",
  "Result": "被起诉，涉及10亿美元欺诈金额",
  "line_of_business": "医疗险",
  "fraud_type": "Fraud",
  "modus_operandi": "Upcoding和Unbundling",
  "red_flags": "理赔金额异常偏高",
  "investigative_tips": "医保大数据比对",
  "underwriting_advice": "建立医疗编码异常预警机制",
  "is_seed_case": true
}
```

### 步骤3: 导入到数据库

确认预览清单无误后，执行导入：

```bash
python3 seed_cases_extractor.py --import
```

**功能**：
- 从预览文件读取案例
- 转换为标准格式
- 批量保存到 Supabase 数据库
- 标记为种子案例（`is_seed_case = True`）

---

## 📊 案例字段说明

### 基础字段（与现有格式一致）
- `Time`: 时间
- `Region`: 地区
- `Characters`: 人物/实体
- `Event`: 事件名称
- `Process`: 经过（SIU格式，5个维度）
- `Result`: 结果

### 新增专业字段
- `line_of_business`: 险种（医疗险/重疾险/定期寿险等）
- `fraud_type`: 欺诈定性（Fraud/Abuse/Waste）
- `modus_operandi`: 舞弊手法（MO）
- `red_flags`: 红旗指标
- `investigative_tips`: 调查突破点
- `underwriting_advice`: 核保/风控建议

### 种子案例标记
- `is_seed_case`: 布尔值，标记为种子案例
- `last_shown_at`: 最后展示时间（用于轮播）

---

## 🎯 Process 字段格式

Process 字段必须严格按照以下5个标题：

```
【风险画像】
投保时间：...
保额：...
出险间隔：...

【舞弊手法(MO)】
具体欺诈手段...

【红旗指标(Red Flags)】
触发警报的异常指标...

【核查手段建议】
确证方式和调查方法...

【核保/风控启示】
预警价值和风控建议...
```

---

## 📝 示例案例

参考文件：`seed_cases_preview_example.json`

包含3个示例案例：
1. DMERx 10亿美元医疗保险欺诈案
2. 无锡虹桥医院挂床住院欺诈案
3. 台湾干冰截肢案

---

## ⚠️ 注意事项

1. **API 限额**：
   - Gemini 免费版每日限额20次
   - 如果达到限额，会自动切换到 DeepSeek
   - 建议在配额充足时运行

2. **外部补充**：
   - 如果报告中案例不足50个，会启动外部搜索
   - 外部搜索的案例需要进一步深度分析（调用 deep_research_flow）

3. **数据质量**：
   - 严禁录入碎片化的新闻简报
   - 所有案例必须符合专家级字段标准
   - 信息缺失的字段必须明确标注

4. **去重机制**：
   - 基于 `source_url` 进行去重
   - 种子案例使用内部URL格式：`internal_report_[案例名]`

---

## 🔍 验证

导入完成后，可以在 Supabase 中验证：

```sql
-- 查看种子案例数量
SELECT COUNT(*) FROM fraud_cases WHERE is_seed_case = TRUE;

-- 查看种子案例列表
SELECT event, region, line_of_business, fraud_type 
FROM fraud_cases 
WHERE is_seed_case = TRUE 
ORDER BY created_at DESC;
```

---

## 📚 相关文件

- `seed_cases_extractor.py` - 提取器脚本
- `database_seed_cases.sql` - 数据库扩展脚本
- `seed_cases_preview.json` - 预览清单（生成后）
- `seed_cases_preview_example.json` - 示例格式

---

**完成以上步骤后，50个核心种子案例库将构建完成！** 🌱
