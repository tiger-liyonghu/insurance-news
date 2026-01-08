-- GIFIA v4.0 - 数据库扩展
-- 添加 source 字段支持用户上传和不同来源标记

-- 添加 source 字段（如果不存在）
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='source') THEN
        ALTER TABLE fraud_cases ADD COLUMN source TEXT DEFAULT 'auto_scout';
    END IF;
END $$;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_fraud_cases_source ON fraud_cases(source);

-- 验证
SELECT 'fraud_cases 表 v4.0 扩展成功！' AS status;
