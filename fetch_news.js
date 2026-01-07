#!/usr/bin/env node

/**
 * 全球保险欺诈监测情报系统 v4.0 - 性能优化版
 * 后台数据抓取脚本（优化版）
 * 
 * 优化特性：
 * 1. 增量更新：仅处理新新闻，避免重复处理
 * 2. 并行调用：同时处理多个案例
 * 3. 批量处理：多个案例打包发送给 AI
 * 4. 超时控制：防止单个请求卡死整个流程
 * 5. 快速模型：使用 gemini-1.5-flash
 */

const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ========== 配置检查 ==========
const NEWS_API_KEY = process.env.NEWS_API_KEY;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = 'gemini-1.5-flash'; // 强制使用快速模型

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

// ========== 配置常量 ==========
const DATA_FILE = path.join(__dirname, 'data.json');
const MAX_ARTICLES = 50; // 保持最新 50 条记录
const BATCH_SIZE = 3; // 每批处理 3 个案例
const API_TIMEOUT = 30000; // 30 秒超时
const MAX_RETRIES = 2; // 最大重试次数

console.log('✅ API Keys 检查通过');
console.log('🚀 v4.0 性能优化模式启动\n');

// ========== 工具函数 ==========

/**
 * 生成新闻的唯一标识符（基于 URL 或标题）
 */
function generateArticleHash(article) {
    const uniqueString = article.url || article.title || '';
    return crypto.createHash('md5').update(uniqueString).digest('hex');
}

/**
 * 带超时的 fetch 请求
 */
async function fetchWithTimeout(url, options = {}, timeout = API_TIMEOUT) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error(`请求超时 (${timeout}ms)`);
        }
        throw error;
    }
}

/**
 * 读取现有的 data.json
 */
function loadExistingData() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const content = fs.readFileSync(DATA_FILE, 'utf8');
            const data = JSON.parse(content);
            return {
                articles: data.articles || [],
                existingHashes: new Set((data.articles || []).map(a => generateArticleHash(a)))
            };
        }
    } catch (error) {
        console.warn('⚠️  读取现有数据失败，将创建新数据:', error.message);
    }
    return { articles: [], existingHashes: new Set() };
}

/**
 * 保存数据到 data.json
 */
function saveData(articles) {
    const outputData = {
        version: '4.0',
        lastUpdated: new Date().toISOString(),
        total: articles.length,
        articles: articles.slice(0, MAX_ARTICLES) // 只保留最新 50 条
    };
    
    fs.writeFileSync(DATA_FILE, JSON.stringify(outputData, null, 2), 'utf8');
    console.log(`\n✅ 数据已保存: ${outputData.articles.length} 条记录`);
}

// ========== 抓取新闻数据 ==========
async function fetchNews() {
    try {
        const query = 'insurance fraud';
        const newsApiUrl = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&language=en&sortBy=publishedAt&pageSize=20&apiKey=${NEWS_API_KEY}`;

        console.log('🔍 查询关键词:', query);
        const response = await fetchWithTimeout(newsApiUrl);

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
        return data.articles;

    } catch (error) {
        console.error('❌ 抓取新闻失败:', error.message);
        console.warn('⚠️  使用模拟数据作为备选方案');
        return getMockData();
    }
}

// ========== 批量处理文章（优化版）==========
async function processArticlesBatch(articles) {
    if (articles.length === 0) return [];
    
    const prompt = `你是保险欺诈监测专家。请分析以下 ${articles.length} 条英文新闻，为每条新闻完成以下任务：

**任务要求（对每条新闻）：**
1. **分类**：判断属于 [寿险, 产险, 再保险, 大健康] 中的哪一类
2. **摘要**：生成100字以内的中文精简摘要（包含案件性质、涉及金额、主要嫌疑人、处理结果）
3. **翻译**：提供标题的4种语言翻译（中文、英文、泰语、越南语）

**新闻列表：**
${articles.map((article, index) => `
新闻 ${index + 1}:
标题: ${article.title || '无标题'}
摘要: ${article.description || '无摘要'}
来源: ${article.source?.name || '未知'}
发布时间: ${article.publishedAt || '未知'}
`).join('\n')}

请以 JSON 数组格式返回，每个元素对应一条新闻：
[
  {
    "category": "寿险|产险|再保险|大健康",
    "summary_zh": "100字以内的中文精简摘要",
    "translations": {
      "zh": "中文标题",
      "en": "英文标题",
      "th": "泰语标题",
      "vi": "越南语标题"
    }
  },
  ...
]`;

    try {
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`;

        const response = await fetchWithTimeout(geminiUrl, {
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
        }, API_TIMEOUT);

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

        const results = JSON.parse(jsonText);
        
        // 将处理结果合并到原始文章
        return articles.map((article, index) => {
            const result = results[index] || {};
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
        });

    } catch (error) {
        console.error(`⚠️  批量处理失败 (${articles.length} 条):`, error.message);
        // 如果批量处理失败，返回默认数据
        return articles.map(article => ({
            ...article,
            category: '产险',
            summary_zh: article.description || 'AI 处理失败，显示原文摘要',
            translations: {
                zh: article.title,
                en: article.title,
                th: article.title,
                vi: article.title
            }
        }));
    }
}

// ========== 单个文章处理（备用方案）==========
async function processArticleSingle(article, retryCount = 0) {
    const prompt = `你是保险欺诈监测专家。请分析以下英文新闻：

标题: ${article.title || '无标题'}
摘要: ${article.description || '无摘要'}

请完成：
1. 分类：[寿险, 产险, 再保险, 大健康]
2. 生成100字以内的中文精简摘要
3. 提供4种语言的标题翻译（中文、英文、泰语、越南语）

返回 JSON：
{
  "category": "寿险|产险|再保险|大健康",
  "summary_zh": "中文摘要",
  "translations": {
    "zh": "中文标题",
    "en": "英文标题",
    "th": "泰语标题",
    "vi": "越南语标题"
  }
}`;

    try {
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`;

        const response = await fetchWithTimeout(geminiUrl, {
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
        }, API_TIMEOUT);

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
        if (retryCount < MAX_RETRIES) {
            console.warn(`⚠️  处理失败，重试中 (${retryCount + 1}/${MAX_RETRIES}):`, error.message);
            await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
            return processArticleSingle(article, retryCount + 1);
        }
        
        console.error(`❌ 处理文章失败 (已重试 ${MAX_RETRIES} 次):`, error.message);
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
            description: 'Authorities have arrested five individuals in connection with a massive life insurance fraud scheme.',
            source: { name: 'Insurance Journal' },
            publishedAt: new Date().toISOString(),
            url: '#',
            urlToImage: null
        },
        {
            title: 'Auto Insurance Fraud Investigation Leads to 12 Arrests',
            description: 'A year-long investigation into staged auto accidents has resulted in the arrest of 12 suspects.',
            source: { name: 'Reuters' },
            publishedAt: new Date(Date.now() - 86400000).toISOString(),
            url: '#',
            urlToImage: null
        },
        {
            title: 'Medical Insurance Fraud: Doctor Charged with $5M Billing Scheme',
            description: 'A prominent physician has been charged with defrauding health insurance companies of $5 million.',
            source: { name: 'Healthcare News' },
            publishedAt: new Date(Date.now() - 172800000).toISOString(),
            url: '#',
            urlToImage: null
        }
    ];
}

// ========== 主函数（优化版）==========
async function main() {
    const startTime = Date.now();
    
    try {
        // 1. 加载现有数据
        console.log('📂 加载现有数据...');
        const { articles: existingArticles, existingHashes } = loadExistingData();
        console.log(`   现有记录: ${existingArticles.length} 条\n`);

        // 2. 抓取最新新闻
        console.log('📡 抓取最新新闻...');
        const fetchedArticles = await fetchNews();
        console.log(`   获取到 ${fetchedArticles.length} 条新闻\n`);

        // 3. 筛选新文章（增量更新）
        const newArticles = fetchedArticles.filter(article => {
            const hash = generateArticleHash(article);
            return !existingHashes.has(hash);
        });

        console.log(`🔍 增量更新检查:`);
        console.log(`   新文章: ${newArticles.length} 条`);
        console.log(`   已存在: ${fetchedArticles.length - newArticles.length} 条\n`);

        if (newArticles.length === 0) {
            console.log('✅ 没有新文章需要处理，数据已是最新');
            saveData(existingArticles);
            return;
        }

        // 4. 批量处理新文章
        console.log(`🤖 开始 AI 处理 (批量模式，每批 ${BATCH_SIZE} 条)...\n`);
        const processedArticles = [];
        
        // 将新文章分批处理
        for (let i = 0; i < newArticles.length; i += BATCH_SIZE) {
            const batch = newArticles.slice(i, i + BATCH_SIZE);
            const batchNumber = Math.floor(i / BATCH_SIZE) + 1;
            const totalBatches = Math.ceil(newArticles.length / BATCH_SIZE);
            
            console.log(`📦 处理批次 ${batchNumber}/${totalBatches} (${batch.length} 条)...`);
            
            try {
                const batchResults = await processArticlesBatch(batch);
                processedArticles.push(...batchResults);
                console.log(`   ✅ 批次 ${batchNumber} 完成\n`);
            } catch (error) {
                console.error(`   ❌ 批次 ${batchNumber} 失败，使用单条处理模式:`, error.message);
                // 如果批量失败，回退到单条处理
                const singleResults = await Promise.all(
                    batch.map(article => processArticleSingle(article))
                );
                processedArticles.push(...singleResults);
                console.log(`   ✅ 批次 ${batchNumber} 完成（单条模式）\n`);
            }
            
            // 批次间短暂延迟，避免 API 限流
            if (i + BATCH_SIZE < newArticles.length) {
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }

        // 5. 合并数据（新文章在前，保持时间顺序）
        const allArticles = [...processedArticles, ...existingArticles];
        
        // 按发布时间排序（最新的在前）
        allArticles.sort((a, b) => {
            const timeA = new Date(a.publishedAt || 0).getTime();
            const timeB = new Date(b.publishedAt || 0).getTime();
            return timeB - timeA;
        });

        // 6. 保存数据
        saveData(allArticles);

        // 7. 输出统计信息
        const categoryCount = {};
        processedArticles.forEach(article => {
            categoryCount[article.category] = (categoryCount[article.category] || 0) + 1;
        });

        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log('\n📊 处理统计:');
        console.log(`   新增文章: ${processedArticles.length} 条`);
        console.log(`   总记录数: ${allArticles.slice(0, MAX_ARTICLES).length} 条`);
        console.log(`   处理耗时: ${duration} 秒`);
        console.log(`   平均速度: ${(processedArticles.length / parseFloat(duration)).toFixed(2)} 条/秒\n`);
        
        if (Object.keys(categoryCount).length > 0) {
            console.log('📈 分类统计:');
            Object.entries(categoryCount).forEach(([category, count]) => {
                console.log(`   ${category}: ${count} 条`);
            });
        }

    } catch (error) {
        console.error('❌ 执行失败:', error);
        process.exit(1);
    }
}

// 运行主函数
main();
