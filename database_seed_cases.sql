-- GIFIA - 种子案例库数据库扩展
-- 为 fraud_cases 表添加种子案例相关字段

-- 添加新字段（如果不存在）
DO $$ 
BEGIN
    -- 险种字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='line_of_business') THEN
        ALTER TABLE fraud_cases ADD COLUMN line_of_business TEXT;
    END IF;
    
    -- 欺诈类型字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='fraud_type') THEN
        ALTER TABLE fraud_cases ADD COLUMN fraud_type TEXT;
    END IF;
    
    -- 舞弊手法字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='modus_operandi') THEN
        ALTER TABLE fraud_cases ADD COLUMN modus_operandi TEXT;
    END IF;
    
    -- 红旗指标字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='red_flags') THEN
        ALTER TABLE fraud_cases ADD COLUMN red_flags TEXT;
    END IF;
    
    -- 调查突破点字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='investigative_tips') THEN
        ALTER TABLE fraud_cases ADD COLUMN investigative_tips TEXT;
    END IF;
    
    -- 核保建议字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='underwriting_advice') THEN
        ALTER TABLE fraud_cases ADD COLUMN underwriting_advice TEXT;
    END IF;
    
    -- 种子案例标记
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='is_seed_case') THEN
        ALTER TABLE fraud_cases ADD COLUMN is_seed_case BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- 最后展示时间
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='fraud_cases' AND column_name='last_shown_at') THEN
        ALTER TABLE fraud_cases ADD COLUMN last_shown_at TIMESTAMPTZ;
    END IF;
END $$;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_fraud_cases_is_seed_case ON fraud_cases(is_seed_case);
CREATE INDEX IF NOT EXISTS idx_fraud_cases_line_of_business ON fraud_cases(line_of_business);
CREATE INDEX IF NOT EXISTS idx_fraud_cases_fraud_type ON fraud_cases(fraud_type);

-- 验证
SELECT 'fraud_cases 表扩展成功！' AS status;
