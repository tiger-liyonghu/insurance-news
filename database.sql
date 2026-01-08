-- GIFIA - 全球反保险欺诈联盟数据库表结构
-- 请将此 SQL 复制到 Supabase SQL Editor 中执行

-- 创建保险欺诈案例表
CREATE TABLE IF NOT EXISTS fraud_cases (
    id BIGSERIAL PRIMARY KEY,
    time TEXT NOT NULL,
    region TEXT NOT NULL,
    characters TEXT NOT NULL,
    event TEXT NOT NULL,
    process TEXT NOT NULL,
    result TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,  -- 唯一约束，用于去重
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引以提高查询速度
CREATE INDEX IF NOT EXISTS idx_fraud_cases_created_at ON fraud_cases(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fraud_cases_source_url ON fraud_cases(source_url);
CREATE INDEX IF NOT EXISTS idx_fraud_cases_region ON fraud_cases(region);

-- 添加更新时间的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器（自动更新 updated_at）
CREATE TRIGGER update_fraud_cases_updated_at 
    BEFORE UPDATE ON fraud_cases 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 验证表是否创建成功
SELECT 'fraud_cases 表创建成功！' AS status;
