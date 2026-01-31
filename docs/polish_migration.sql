"""
数据库迁移脚本 - 为学术润色模块创建表结构
SQL脚本，可直接在数据库中执行
"""

-- =======================================================
-- SQLite 版本
-- =======================================================

CREATE TABLE IF NOT EXISTS polish_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    original_text TEXT NOT NULL,
    polished_text TEXT,
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/processing/completed/failed',
    polish_level VARCHAR(20) DEFAULT 'standard' COMMENT 'standard/academic/formal',
    terminology_issues JSON,
    tense_issues JSON,
    style_issues JSON,
    thesis_issues JSON,
    total_issues INTEGER DEFAULT 0,
    fixed_issues INTEGER DEFAULT 0,
    accuracy REAL DEFAULT 0.0,
    auto_fix_enabled VARCHAR(5) DEFAULT 'false',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS polish_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    issue_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    location JSON NOT NULL,
    original_content TEXT NOT NULL,
    suggested_content TEXT NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    rule_id VARCHAR(100),
    confidence REAL DEFAULT 0.0,
    accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES polish_tasks(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_polish_tasks_status ON polish_tasks(status);
CREATE INDEX IF NOT EXISTS idx_polish_tasks_created_at ON polish_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_polish_issues_task_id ON polish_issues(task_id);
CREATE INDEX IF NOT EXISTS idx_polish_issues_issue_type ON polish_issues(issue_type);

-- =======================================================
-- PostgreSQL 版本
-- =======================================================

/*
CREATE TABLE IF NOT EXISTS polish_tasks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER,
    original_text TEXT NOT NULL,
    polished_text TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    polish_level VARCHAR(20) DEFAULT 'standard',
    terminology_issues JSONB,
    tense_issues JSONB,
    style_issues JSONB,
    thesis_issues JSONB,
    total_issues INTEGER DEFAULT 0,
    fixed_issues INTEGER DEFAULT 0,
    accuracy REAL DEFAULT 0.0,
    auto_fix_enabled VARCHAR(5) DEFAULT 'false',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS polish_issues (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES polish_tasks(id) ON DELETE CASCADE,
    issue_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    location JSONB NOT NULL,
    original_content TEXT NOT NULL,
    suggested_content TEXT NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    rule_id VARCHAR(100),
    confidence REAL DEFAULT 0.0,
    accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_polish_tasks_status ON polish_tasks(status);
CREATE INDEX idx_polish_tasks_created_at ON polish_tasks(created_at);
CREATE INDEX idx_polish_issues_task_id ON polish_issues(task_id);
CREATE INDEX idx_polish_issues_issue_type ON polish_issues(issue_type);
*/

-- =======================================================
-- 示例数据 (可选)
-- =======================================================

-- 插入测试任务
INSERT INTO polish_tasks (
    original_text, 
    status, 
    polish_level, 
    total_issues, 
    fixed_issues, 
    accuracy
) VALUES (
    '我们的研究进行了详细分析。这样做很好。',
    'completed',
    'academic',
    2,
    0,
    0.0
);

-- 插入测试问题
INSERT INTO polish_issues (
    task_id,
    issue_type,
    severity,
    location,
    original_content,
    suggested_content,
    reason,
    rule_id,
    confidence
) VALUES (
    1,
    'terminology',
    'minor',
    '{"start": 0, "end": 3}',
    '我们的研究',
    '本研究',
    '将非正式术语替换为学术术语',
    'TERM_001',
    0.95
);

INSERT INTO polish_issues (
    task_id,
    issue_type,
    severity,
    location,
    original_content,
    suggested_content,
    reason,
    rule_id,
    confidence
) VALUES (
    1,
    'thesis',
    'medium',
    '{"start": 14, "end": 18}',
    '这样做很好',
    '结果良好',
    '学位论文规范检查：表述方式调整',
    'THESIS_001',
    0.85
);
