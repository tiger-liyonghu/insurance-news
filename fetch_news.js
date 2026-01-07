#!/usr/bin/env node

/**
 * 全球保险欺诈监测情报系统 v3.0
 * 后台数据抓取脚本
 * 
 * 功能：
 * 1. 从 NewsAPI 抓取保险欺诈相关新闻
 * 2. 使用 Gemini API 进行分类、总结和多语言翻译
 * 3. 将处理后的数据保存为 data.json
 */

const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

// ========== 配置检查 ==========
const NEWS_API_KEY = process.env.NEWS_API_KEY;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-1.5-flash';

if (!NEWS_API_KEY) {
    console.error('❌ 错误: NEWS_API_KEY 环境变量未设置');
    console.error('请在 GitHub Repository Settings -> Secrets 中设置 NEWS_API_KEY');
    process.exit(1);
}

if (!GEMINI_API_KEY) {
    console.error('❌ 错误: GEMINI_API_KEY 环境变量未设置');
    console.error('请在 GitHub Repository Settings -> Secrets 中设置 GEMINI_API_KEY');
    process.exit(1);
}

console.log('✅ API Keys 检查通过');
console.log('📡 开始抓取新闻数据...\n');

// ========== 抓取新闻数据 ==========
async function fetchNews() {
    try {
        // 构建查询（保险欺诈相关）
        const query = 'insurance fraud';
        const newsApiUrl = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&language=en&sortBy=publishedAt&pageSize=10&apiKey=${NEWS_API_KEY}`;

        console.log('🔍 查询关键词:', query);
        const response = await fetch(newsApiUrl);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`NewsAPI 错误 (${response.status}): ${errorData.message || response.statusText}`);
        }

        const data = await response.json();

        if (data.status === 'error') {
            throw new Error(`NewsAPI 返回错误: ${data.message || '未知错误'}`);
        }

        if (data.status !== 'ok' || !data.articles || data.articles.length === 0) {
            console.warn('⚠️  未找到相关新闻，使用模拟数据');
            return getMockData();
        }

        console.log(`✅ 成功获取 ${data.articles.length} 条新闻`);
        return data.articles.slice(0, 10);

    } catch (error) {
        console.error('❌ 抓取新闻失败:', error.message);
        console.warn('⚠️  使用模拟数据作为备选方案');
        return getMockData();
    }
}

// ========== 使用 Gemini API 处理文章 ==========
async function processArticleWithGemini(article, index) {
    try {
        const prompt = `你是一个保险欺诈监测专家。请分析以下英文新闻，完成以下任务：

**原始新闻信息：**
标题: ${article.title || '无标题'}
摘要: ${article.description || '无摘要'}
来源: ${article.source?.name || '未知'}
发布时间: ${article.publishedAt || '未知'}

**任务要求：**
1. **分类任务**：判断这个案例属于以下哪一类？[寿险, 产险, 再保险, 大健康]
2. **摘要任务**：生成一个100字以内的中文精简摘要，包含：案件性质、涉及金额（如有）、主要嫌疑人、处理结果。
3. **翻译任务**：提供以下语言的标题翻译：
   - 中文
   - 英文（原文）
   - 泰语
   - 越南语

请以 JSON 格式返回，格式如下：
{
  "category": "寿险|产险|再保险|大健康",
  "summary_zh": "100字以内的中文精简摘要",
  "translations": {
    "zh": "中文标题",
    "en": "英文标题",
    "th": "泰语标题",
    "vi": "越南语标题"
  }
}`;

        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`;

        const response = await fetch(geminiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: prompt
                    }]
                }]
            })
        });

        if (!response.ok) {
            throw new Error(`Gemini API 错误: ${response.status}`);
        }

        const data = await response.json();

        if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
            throw new Error('Gemini API 返回格式错误');
        }

        const text = data.candidates[0].content.parts[0].text;

        // 提取 JSON
        let jsonText = text.trim();
        if (jsonText.includes('```json')) {
            jsonText = jsonText.split('```json')[1].split('```')[0].trim();
        } else if (jsonText.includes('```')) {
            jsonText = jsonText.split('```')[1].split('```')[0].trim();
        }

        const result = JSON.parse(jsonText);

        return {
            ...article,
            category: result.category || '产险',
            summary_zh: result.summary_zh || article.description || '暂无摘要',
            translations: result.translations || {
                zh: article.title,
                en: article.title,
                th: article.title,
                vi: article.title
            }
        };

    } catch (error) {
        console.error(`⚠️  处理文章 ${index + 1} 失败:`, error.message);
        // 如果失败，返回默认数据
        return {
            ...article,
            category: '产险',
            summary_zh: article.description || 'AI 处理失败，显示原文摘要',
            translations: {
                zh: article.title,
                en: article.title,
                th: article.title,
                vi: article.title
            }
        };
    }
}

// ========== 模拟数据（备选方案）==========
function getMockData() {
    return [
        {
            title: 'Insurance Fraud Ring Busted: $2M Life Insurance Scam Uncovered',
            description: 'Authorities have arrested five individuals in connection with a massive life insurance fraud scheme that defrauded insurers of over $2 million through fake death certificates and identity theft.',
            source: { name: 'Insurance Journal' },
            publishedAt: new Date().toISOString(),
            url: '#',
            urlToImage: null,
            category: '寿险',
            summary_zh: '执法部门破获一起大型寿险欺诈案，逮捕5名嫌疑人。该团伙通过伪造死亡证明和身份盗用，骗取保险公司超过200万美元。案件涉及多个州，目前正在进一步调查中。',
            translations: {
                zh: '保险欺诈团伙被破获：200万美元寿险诈骗案曝光',
                en: 'Insurance Fraud Ring Busted: $2M Life Insurance Scam Uncovered',
                th: 'เครือข่ายการฉ้อโกงประกันภัยถูกจับกุม: เปิดโปงการฉ้อโกงประกันชีวิตมูลค่า 2 ล้านดอลลาร์',
                vi: 'Vỡ lưới gian lận bảo hiểm: Phát hiện vụ lừa đảo bảo hiểm nhân thọ 2 triệu USD'
            }
        },
        {
            title: 'Auto Insurance Fraud Investigation Leads to 12 Arrests',
            description: 'A year-long investigation into staged auto accidents has resulted in the arrest of 12 suspects who allegedly orchestrated fake collisions to collect insurance payouts.',
            source: { name: 'Reuters' },
            publishedAt: new Date(Date.now() - 86400000).toISOString(),
            url: '#',
            urlToImage: null,
            category: '产险',
            summary_zh: '经过一年的调查，执法部门破获一起故意制造车祸的保险欺诈案，逮捕12名嫌疑人。该团伙通过策划虚假碰撞事故骗取保险赔偿，涉案金额巨大。',
            translations: {
                zh: '车险欺诈调查导致12人被捕',
                en: 'Auto Insurance Fraud Investigation Leads to 12 Arrests',
                th: 'การสอบสวนการฉ้อโกงประกันภัยรถยนต์นำไปสู่การจับกุม 12 คน',
                vi: 'Điều tra gian lận bảo hiểm ô tô dẫn đến 12 người bị bắt'
            }
        },
        {
            title: 'Medical Insurance Fraud: Doctor Charged with $5M Billing Scheme',
            description: 'A prominent physician has been charged with defrauding health insurance companies of $5 million through fraudulent billing practices and unnecessary medical procedures.',
            source: { name: 'Healthcare News' },
            publishedAt: new Date(Date.now() - 172800000).toISOString(),
            url: '#',
            urlToImage: null,
            category: '大健康',
            summary_zh: '一名知名医生被指控通过欺诈性账单和不必要的医疗程序，骗取健康保险公司500万美元。案件涉及数百名患者，目前正在法庭审理中。',
            translations: {
                zh: '医疗保险欺诈：医生被控500万美元账单诈骗',
                en: 'Medical Insurance Fraud: Doctor Charged with $5M Billing Scheme',
                th: 'การฉ้อโกงประกันสุขภาพ: แพทย์ถูกตั้งข้อหาแผนการเรียกเก็บเงิน 5 ล้านดอลลาร์',
                vi: 'Gian lận bảo hiểm y tế: Bác sĩ bị buộc tội kế hoạch thanh toán 5 triệu USD'
            }
        },
        {
            title: 'Critical Illness Insurance Fraud: Fake Cancer Diagnosis Exposed',
            description: 'Insurance investigators have uncovered a scheme where individuals faked critical illness diagnoses, particularly cancer, to claim large insurance payouts from critical illness policies.',
            source: { name: 'Insurance Times' },
            publishedAt: new Date(Date.now() - 259200000).toISOString(),
            url: '#',
            urlToImage: null,
            category: '寿险',
            summary_zh: '保险调查人员发现一起伪造重疾诊断的欺诈案，嫌疑人通过伪造癌症等重疾诊断骗取重大疾病保险赔付。案件涉及多名医生和患者，目前正在深入调查。',
            translations: {
                zh: '重疾保险欺诈：伪造癌症诊断被曝光',
                en: 'Critical Illness Insurance Fraud: Fake Cancer Diagnosis Exposed',
                th: 'การฉ้อโกงประกันโรคร้ายแรง: เปิดโปงการวินิจฉัยมะเร็งปลอม',
                vi: 'Gian lận bảo hiểm bệnh hiểm nghèo: Phát hiện chẩn đoán ung thư giả'
            }
        },
        {
            title: 'Reinsurance Fraud Case: International Investigation Underway',
            description: 'Regulators from multiple countries are investigating a complex reinsurance fraud scheme that spans across borders, involving fake reinsurance contracts and manipulated claims data.',
            source: { name: 'Financial Times' },
            publishedAt: new Date(Date.now() - 345600000).toISOString(),
            url: '#',
            urlToImage: null,
            category: '再保险',
            summary_zh: '多国监管机构正在调查一起复杂的跨境再保险欺诈案，涉及伪造再保险合同和操纵理赔数据。案件涉及多个国家的保险公司，调查仍在进行中。',
            translations: {
                zh: '再保险欺诈案：国际调查正在进行',
                en: 'Reinsurance Fraud Case: International Investigation Underway',
                th: 'คดีการฉ้อโกงประกันภัยต่อ: กำลังดำเนินการสอบสวนระหว่างประเทศ',
                vi: 'Vụ gian lận tái bảo hiểm: Điều tra quốc tế đang diễn ra'
            }
        }
    ];
}

// ========== 主函数 ==========
async function main() {
    try {
        // 1. 抓取新闻
        const articles = await fetchNews();

        // 2. 使用 Gemini 处理每条新闻
        console.log('🤖 开始使用 AI 处理新闻...\n');
        const processedArticles = [];
        
        for (let i = 0; i < articles.length; i++) {
            console.log(`处理中 ${i + 1}/${articles.length}: ${articles[i].title?.substring(0, 50)}...`);
            const processed = await processArticleWithGemini(articles[i], i);
            processedArticles.push(processed);
            
            // 延迟以避免 API 限流
            if (i < articles.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }

        // 3. 构建最终数据
        const outputData = {
            version: '3.0',
            lastUpdated: new Date().toISOString(),
            total: processedArticles.length,
            articles: processedArticles
        };

        // 4. 保存为 data.json
        const outputPath = path.join(__dirname, 'data.json');
        fs.writeFileSync(outputPath, JSON.stringify(outputData, null, 2), 'utf8');

        console.log('\n✅ 数据抓取和处理完成！');
        console.log(`📄 数据已保存到: ${outputPath}`);
        console.log(`📊 共处理 ${processedArticles.length} 条新闻\n`);

        // 5. 输出统计信息
        const categoryCount = {};
        processedArticles.forEach(article => {
            categoryCount[article.category] = (categoryCount[article.category] || 0) + 1;
        });
        
        console.log('📈 分类统计:');
        Object.entries(categoryCount).forEach(([category, count]) => {
            console.log(`   ${category}: ${count} 条`);
        });

    } catch (error) {
        console.error('❌ 执行失败:', error);
        process.exit(1);
    }
}

// 运行主函数
main();
