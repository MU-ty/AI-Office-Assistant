-- 办公助手Agent - PostgreSQL 数据库初始化脚本
-- 版本: v1.0
-- 数据库: PostgreSQL 15+
-- 执行方式: psql -U postgres -d office_assistant < init_schema.sql

-- ============================================================
-- 第一部分：扩展与基础设置
-- ============================================================

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建枚举类型
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');
CREATE TYPE user_role AS ENUM ('admin', 'user', 'guest');
CREATE TYPE session_device_type AS ENUM ('web', 'mobile', 'desktop');

CREATE TYPE meeting_type AS ENUM ('standup', 'regular', 'brainstorm', 'review', 'training', 'other');
CREATE TYPE meeting_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled', 'archived');
CREATE TYPE transcription_status AS ENUM ('pending', 'processing', 'completed', 'failed');
CREATE TYPE meeting_visibility AS ENUM ('private', 'team', 'organization', 'public');
CREATE TYPE participant_role AS ENUM ('organizer', 'presenter', 'attendee', 'observer');
CREATE TYPE participant_status AS ENUM ('invited', 'accepted', 'declined', 'tentative', 'no_response');
CREATE TYPE agenda_status AS ENUM ('pending', 'in_progress', 'completed', 'skipped');
CREATE TYPE decision_status AS ENUM ('proposed', 'approved', 'rejected', 'in_progress', 'completed', 'archived');
CREATE TYPE action_item_priority AS ENUM ('critical', 'high', 'medium', 'low');
CREATE TYPE action_item_status AS ENUM ('open', 'in_progress', 'completed', 'blocked', 'cancelled', 'overdue');
CREATE TYPE review_status AS ENUM ('pending', 'reviewing', 'approved', 'rejected');

CREATE TYPE document_source_type AS ENUM ('pdf', 'url', 'text', 'manual_upload', 'arxiv', 'pubmed');
CREATE TYPE document_research_level AS ENUM ('abstract', 'conference_paper', 'journal', 'review', 'thesis');
CREATE TYPE document_visibility AS ENUM ('private', 'shared', 'public');
CREATE TYPE document_processing_status AS ENUM ('pending', 'processing', 'completed', 'failed');
CREATE TYPE document_concept_type AS ENUM ('entity', 'method', 'result', 'concept', 'keyword', 'methodology');
CREATE TYPE citation_type AS ENUM ('direct', 'indirect', 'paraphrase', 'mentioned');
CREATE TYPE summary_level AS ENUM ('one_liner', 'paragraph', 'full', 'structured');

CREATE TYPE polish_level AS ENUM ('light', 'standard', 'deep', 'expert');
CREATE TYPE issue_type AS ENUM ('grammar', 'spelling', 'punctuation', 'style', 'clarity', 'vocabulary', 'coherence');
CREATE TYPE issue_severity AS ENUM ('error', 'warning', 'suggestion', 'info');
CREATE TYPE user_action AS ENUM ('accepted', 'rejected', 'skipped');

CREATE TYPE translation_style AS ENUM ('literal', 'free', 'academic');
CREATE TYPE translation_task_status AS ENUM ('pending', 'translating', 'reviewing', 'completed', 'failed');
CREATE TYPE terminology_source_type AS ENUM ('automatic', 'manual', 'expert_review', 'user_contributed');
CREATE TYPE terminology_approval AS ENUM ('pending', 'approved', 'rejected', 'archived');

CREATE TYPE ppt_project_status AS ENUM ('draft', 'generating', 'completed', 'failed', 'archived');
CREATE TYPE slide_type AS ENUM ('title', 'content', 'toc', 'section_header', 'visualization', 'conclusion', 'blank');
CREATE TYPE viz_type AS ENUM ('chart', 'graph', 'image', 'table', 'diagram', 'icon');

CREATE TYPE work_type AS ENUM ('development', 'testing', 'documentation', 'meeting', 'learning', 'communication', 'other');
CREATE TYPE blocker_status AS ENUM ('open', 'in_progress', 'resolved');
CREATE TYPE log_status AS ENUM ('draft', 'submitted', 'reviewed', 'approved');
CREATE TYPE report_review_status AS ENUM ('draft', 'submitted', 'reviewing', 'approved', 'rejected');

CREATE TYPE notification_type AS ENUM ('action_item', 'meeting_reminder', 'document_shared', 'report_review', 'system', 'other');
CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'urgent');

-- ============================================================
-- 第二部分：用户认证模块表
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(255),
    
    status user_status DEFAULT 'active',
    role user_role DEFAULT 'user',
    
    organization VARCHAR(100),
    position VARCHAR(100),
    phone VARCHAR(20),
    bio TEXT,
    
    is_email_verified BOOLEAN DEFAULT FALSE,
    is_phone_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP,
    phone_verified_at TIMESTAMP,
    
    language VARCHAR(10) DEFAULT 'zh-CN',
    timezone VARCHAR(50) DEFAULT 'UTC',
    theme VARCHAR(20) DEFAULT 'auto',
    notification_enabled BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    deleted_at TIMESTAMP,
    
    metadata JSONB DEFAULT '{}',
    
    CONSTRAINT email_verified_consistency CHECK (
        (is_email_verified = FALSE AND email_verified_at IS NULL) OR
        (is_email_verified = TRUE AND email_verified_at IS NOT NULL)
    )
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    birth_date DATE,
    gender VARCHAR(20),
    department VARCHAR(100),
    team VARCHAR(100),
    
    education_level VARCHAR(50),
    major_field VARCHAR(100),
    research_interests TEXT[],
    
    skills TEXT[],
    language_proficiency JSONB,
    
    preferred_summary_length VARCHAR(20),
    preferred_translation_style translation_style,
    
    privacy_level VARCHAR(20) DEFAULT 'private',
    allow_data_collection BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    access_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500),
    token_type VARCHAR(20) DEFAULT 'Bearer',
    
    device_type session_device_type,
    device_name VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    is_valid BOOLEAN DEFAULT TRUE,
    is_revoked BOOLEAN DEFAULT FALSE,
    
    CONSTRAINT valid_session CHECK (expires_at > created_at)
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_access_token ON user_sessions(access_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    key_name VARCHAR(100) NOT NULL,
    key_value VARCHAR(255) NOT NULL UNIQUE,
    key_prefix VARCHAR(20),
    
    scopes TEXT[] DEFAULT '{"read", "write"}',
    
    rate_limit INT,
    requests_count INT DEFAULT 0,
    last_used_at TIMESTAMP,
    
    is_active BOOLEAN DEFAULT TRUE,
    expired_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_value ON api_keys(key_value);

-- ============================================================
-- 第三部分：会议纪要模块表
-- ============================================================

CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    meeting_type meeting_type DEFAULT 'regular',
    
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    scheduled_duration_minutes INT,
    actual_duration_minutes INT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    location VARCHAR(255),
    is_virtual BOOLEAN DEFAULT FALSE,
    meeting_url VARCHAR(255),
    
    organizer_id UUID REFERENCES users(id),
    max_participants INT,
    
    status meeting_status DEFAULT 'scheduled',
    transcription_status transcription_status DEFAULT 'pending',
    minutes_status transcription_status DEFAULT 'pending',
    
    visibility meeting_visibility DEFAULT 'private',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    metadata JSONB DEFAULT '{}',
    
    CONSTRAINT meeting_time_logic CHECK (
        (status = 'scheduled' AND end_time IS NULL) OR
        (status IN ('completed', 'archived') AND end_time IS NOT NULL AND end_time > start_time) OR
        (status = 'cancelled' AND end_time IS NULL)
    )
);

CREATE INDEX idx_meetings_user_id ON meetings(user_id);
CREATE INDEX idx_meetings_organizer_id ON meetings(organizer_id);
CREATE INDEX idx_meetings_start_time ON meetings(start_time DESC);
CREATE INDEX idx_meetings_status ON meetings(status);
CREATE INDEX idx_meetings_created_at ON meetings(created_at DESC);

CREATE TABLE meeting_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    participant_name VARCHAR(255) NOT NULL,
    participant_email VARCHAR(100),
    role participant_role DEFAULT 'attendee',
    
    status participant_status DEFAULT 'invited',
    
    speaking_time_seconds INT DEFAULT 0,
    speaking_count INT DEFAULT 0,
    last_spoke_at TIMESTAMP,
    
    is_active BOOLEAN DEFAULT TRUE,
    attention_score FLOAT,
    
    joined_at TIMESTAMP,
    left_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_meeting_participants_meeting_id ON meeting_participants(meeting_id);
CREATE INDEX idx_meeting_participants_user_id ON meeting_participants(user_id);
CREATE INDEX idx_meeting_participants_status ON meeting_participants(status);

CREATE TABLE meeting_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    
    content_type VARCHAR(50) NOT NULL,
    
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    mime_type VARCHAR(50),
    
    raw_text TEXT,
    processed_text TEXT,
    
    processing_status transcription_status DEFAULT 'pending',
    processing_error TEXT,
    
    audio_quality FLOAT,
    transcription_confidence FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    
    metadata JSONB
);

CREATE INDEX idx_meeting_content_meeting_id ON meeting_content(meeting_id);
CREATE INDEX idx_meeting_content_status ON meeting_content(processing_status);

CREATE TABLE meeting_agendas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    
    sequence INT NOT NULL,
    agenda_title VARCHAR(255) NOT NULL,
    agenda_description TEXT,
    
    planned_duration_minutes INT,
    actual_duration_minutes INT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    
    responsible_person_id UUID REFERENCES users(id),
    responsible_person_name VARCHAR(100),
    
    status agenda_status DEFAULT 'pending',
    
    related_documents TEXT[],
    tags TEXT[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_sequence CHECK (sequence >= 1)
);

CREATE INDEX idx_meeting_agendas_meeting_id ON meeting_agendas(meeting_id);
CREATE INDEX idx_meeting_agendas_sequence ON meeting_agendas(meeting_id, sequence);

CREATE TABLE meeting_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    
    decision_title VARCHAR(255) NOT NULL,
    decision_description TEXT,
    decision_rationale TEXT,
    
    decision_maker_id UUID REFERENCES users(id),
    approver_id UUID REFERENCES users(id),
    
    deadline DATE,
    implementation_plan TEXT,
    
    status decision_status DEFAULT 'proposed',
    
    estimated_impact VARCHAR(50),
    affected_teams TEXT[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_meeting_decisions_meeting_id ON meeting_decisions(meeting_id);
CREATE INDEX idx_meeting_decisions_status ON meeting_decisions(status);

CREATE TABLE action_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    
    task_description TEXT NOT NULL,
    detailed_requirements TEXT,
    
    assigned_to_id UUID REFERENCES users(id),
    assigned_to_name VARCHAR(100),
    assigned_by_id UUID REFERENCES users(id),
    
    priority action_item_priority DEFAULT 'medium',
    due_date DATE NOT NULL,
    estimated_hours FLOAT,
    
    status action_item_status DEFAULT 'open',
    
    completion_percentage INT DEFAULT 0,
    completion_date DATE,
    completion_notes TEXT,
    
    depends_on_items TEXT[],
    blocking_items TEXT[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_completion CHECK (completion_percentage >= 0 AND completion_percentage <= 100)
);

CREATE INDEX idx_action_items_meeting_id ON action_items(meeting_id);
CREATE INDEX idx_action_items_assigned_to ON action_items(assigned_to_id);
CREATE INDEX idx_action_items_status ON action_items(status);
CREATE INDEX idx_action_items_due_date ON action_items(due_date);

CREATE TABLE meeting_minutes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    
    title VARCHAR(255),
    generated_by_id UUID REFERENCES users(id),
    
    executive_summary TEXT,
    detailed_content TEXT,
    key_points TEXT[],
    
    format VARCHAR(50),
    
    exported_files JSONB DEFAULT '{}',
    
    completeness_score FLOAT,
    clarity_score FLOAT,
    
    review_status review_status DEFAULT 'pending',
    reviewed_by_id UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_comments TEXT,
    
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    visibility meeting_visibility DEFAULT 'private',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_meeting_minutes_meeting_id ON meeting_minutes(meeting_id);
CREATE INDEX idx_meeting_minutes_status ON meeting_minutes(review_status);

-- ============================================================
-- 第四部分：文献摘要模块表
-- ============================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    title VARCHAR(255) NOT NULL,
    authors TEXT[],
    description TEXT,
    
    publication_date DATE,
    publication_venue VARCHAR(255),
    volume VARCHAR(50),
    issue VARCHAR(50),
    page_range VARCHAR(50),
    
    doi VARCHAR(100) UNIQUE,
    isbn VARCHAR(20),
    issn VARCHAR(20),
    url VARCHAR(500),
    
    source_type document_source_type DEFAULT 'pdf',
    source_url VARCHAR(500),
    
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    
    original_language VARCHAR(10) DEFAULT 'en',
    word_count INT,
    page_count INT,
    
    processing_status document_processing_status DEFAULT 'pending',
    processing_error TEXT,
    
    category VARCHAR(100),
    field_of_study TEXT[],
    research_level document_research_level DEFAULT 'journal',
    
    visibility document_visibility DEFAULT 'private',
    shared_with_users UUID[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    metadata JSONB DEFAULT '{}',
    
    CONSTRAINT document_processing_logic CHECK (
        (processing_status = 'pending' AND processing_error IS NULL) OR
        (processing_status = 'failed' AND processing_error IS NOT NULL) OR
        (processing_status IN ('completed', 'processing') AND processing_error IS NULL)
    )
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_doi ON documents(doi);
CREATE INDEX idx_documents_status ON documents(processing_status);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

CREATE TABLE document_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    summary_level summary_level NOT NULL,
    
    language VARCHAR(10) DEFAULT 'en',
    translated_from VARCHAR(10),
    
    summary_text TEXT NOT NULL,
    
    model_used VARCHAR(100),
    model_version VARCHAR(50),
    
    quality_score FLOAT,
    completeness_score FLOAT,
    readability_score FLOAT,
    
    user_rating INT,
    user_feedback TEXT,
    
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_summaries_document_id ON document_summaries(document_id);
CREATE INDEX idx_document_summaries_level ON document_summaries(summary_level);

CREATE TABLE document_concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    concept_term VARCHAR(255) NOT NULL,
    concept_type document_concept_type DEFAULT 'keyword',
    
    frequency INT,
    importance_score FLOAT,
    
    first_occurrence_char INT,
    last_occurrence_char INT,
    occurrence_positions INT[],
    
    definition TEXT,
    context_snippet TEXT,
    
    related_concepts TEXT[],
    
    confidence FLOAT,
    
    identified_by VARCHAR(100),
    identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_concepts_document_id ON document_concepts(document_id);
CREATE INDEX idx_document_concepts_term ON document_concepts(concept_term);

CREATE TABLE document_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    cited_doc_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    
    citation_text TEXT,
    citation_context TEXT,
    citation_type citation_type DEFAULT 'direct',
    
    citation_page INT,
    citation_section VARCHAR(255),
    
    citation_count INT DEFAULT 1,
    
    is_supporting BOOLEAN,
    is_contradicting BOOLEAN,
    importance_level VARCHAR(20) DEFAULT 'medium',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_citations_source ON document_citations(source_doc_id);
CREATE INDEX idx_document_citations_cited ON document_citations(cited_doc_id);

CREATE TABLE document_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    vector_id VARCHAR(255) NOT NULL,
    embedding_model VARCHAR(100),
    embedding_dimension INT,
    
    chunk_index INT,
    chunk_text TEXT,
    chunk_token_count INT,
    
    vector_quality_score FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX idx_document_vectors_document_id ON document_vectors(document_id);
CREATE INDEX idx_document_vectors_vector_id ON document_vectors(vector_id);

CREATE TABLE document_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    tag_name VARCHAR(100) NOT NULL,
    tag_category VARCHAR(50),
    
    user_defined BOOLEAN DEFAULT FALSE,
    is_system_tag BOOLEAN DEFAULT FALSE,
    
    weight FLOAT DEFAULT 1.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, tag_name)
);

CREATE INDEX idx_document_tags_document_id ON document_tags(document_id);
CREATE INDEX idx_document_tags_name ON document_tags(tag_name);

CREATE TABLE document_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    collection_name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7),
    
    document_ids UUID[],
    document_count INT DEFAULT 0,
    
    display_order INT,
    
    is_public BOOLEAN DEFAULT FALSE,
    shared_with_users UUID[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_collections_user_id ON document_collections(user_id);

-- ============================================================
-- 第五部分：学术润色模块表
-- ============================================================

CREATE TABLE polish_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    input_type VARCHAR(50) DEFAULT 'text',
    input_text TEXT,
    input_file_path VARCHAR(255),
    input_language VARCHAR(10) DEFAULT 'en',
    
    polish_level polish_level DEFAULT 'standard',
    polish_focus TEXT[],
    
    status transcription_status DEFAULT 'pending',
    progress_percentage INT DEFAULT 0,
    
    output_text TEXT,
    issue_count INT,
    suggestion_count INT,
    
    grammar_score FLOAT,
    readability_score FLOAT,
    academic_score FLOAT,
    overall_quality_score FLOAT,
    
    user_rating INT,
    user_feedback TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_polish_tasks_user_id ON polish_tasks(user_id);
CREATE INDEX idx_polish_tasks_status ON polish_tasks(status);
CREATE INDEX idx_polish_tasks_created_at ON polish_tasks(created_at DESC);

CREATE TABLE polish_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    polish_task_id UUID NOT NULL REFERENCES polish_tasks(id) ON DELETE CASCADE,
    
    issue_type issue_type NOT NULL,
    issue_severity issue_severity DEFAULT 'warning',
    
    text_position INT,
    text_length INT,
    original_text VARCHAR(500),
    
    suggested_replacement VARCHAR(500),
    explanation TEXT,
    category VARCHAR(100),
    
    rule_id VARCHAR(100),
    rule_name VARCHAR(255),
    
    is_accepted BOOLEAN DEFAULT FALSE,
    user_action user_action DEFAULT 'skipped',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_polish_issues_polish_task_id ON polish_issues(polish_task_id);
CREATE INDEX idx_polish_issues_type ON polish_issues(issue_type);

CREATE TABLE polish_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    polish_task_id UUID NOT NULL REFERENCES polish_tasks(id) ON DELETE CASCADE,
    
    version_number INT NOT NULL,
    version_name VARCHAR(100),
    
    full_text TEXT,
    text_length INT,
    word_count INT,
    
    changes_made INT,
    issues_fixed INT,
    
    quality_score_before FLOAT,
    quality_score_after FLOAT,
    quality_improvement FLOAT,
    
    created_by_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_version CHECK (version_number >= 1)
);

CREATE INDEX idx_polish_versions_polish_task_id ON polish_versions(polish_task_id);
CREATE INDEX idx_polish_versions_version_number ON polish_versions(polish_task_id, version_number DESC);

-- ============================================================
-- 第六部分：多语言处理模块表
-- ============================================================

CREATE TABLE translation_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    translation_style translation_style DEFAULT 'academic',
    domain VARCHAR(100),
    
    input_type VARCHAR(50) DEFAULT 'text',
    input_text TEXT,
    input_file_path VARCHAR(255),
    input_length_chars INT,
    
    status translation_task_status DEFAULT 'pending',
    progress_percentage INT DEFAULT 0,
    
    output_text TEXT,
    output_length_chars INT,
    
    quality_score FLOAT,
    fluency_score FLOAT,
    accuracy_score FLOAT,
    consistency_score FLOAT,
    
    user_rating INT,
    user_feedback TEXT,
    is_satisfied BOOLEAN,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_translation_tasks_user_id ON translation_tasks(user_id);
CREATE INDEX idx_translation_tasks_status ON translation_tasks(status);
CREATE INDEX idx_translation_tasks_lang_pair ON translation_tasks(source_language, target_language);

CREATE TABLE terminology_database (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    original_term VARCHAR(255) NOT NULL,
    source_language VARCHAR(10) NOT NULL,
    domain VARCHAR(100),
    
    zh_translation VARCHAR(255),
    en_translation VARCHAR(255),
    ja_translation VARCHAR(255),
    ko_translation VARCHAR(255),
    fr_translation VARCHAR(255),
    de_translation VARCHAR(255),
    es_translation VARCHAR(255),
    ru_translation VARCHAR(255),
    
    definition TEXT,
    usage_example TEXT,
    context_notes TEXT,
    synonyms VARCHAR(255)[],
    antonyms VARCHAR(255)[],
    
    source_type terminology_source_type DEFAULT 'automatic',
    confidence_score FLOAT,
    
    approval_status terminology_approval DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    
    usage_count INT DEFAULT 0,
    contributor_id UUID REFERENCES users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(original_term, source_language, domain)
);

CREATE INDEX idx_terminology_original_term ON terminology_database(original_term);
CREATE INDEX idx_terminology_domain ON terminology_database(domain);
CREATE INDEX idx_terminology_approval ON terminology_database(approval_status);

CREATE TABLE translation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    translation_task_id UUID REFERENCES translation_tasks(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    
    original_text TEXT,
    translated_text TEXT,
    source_language VARCHAR(10),
    target_language VARCHAR(10),
    
    quality_score FLOAT,
    
    user_rating INT,
    feedback TEXT,
    improvement_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_translation_history_user_id ON translation_history(user_id);
CREATE INDEX idx_translation_history_created_at ON translation_history(created_at DESC);

-- ============================================================
-- 第七部分：PPT生成模块表
-- ============================================================

CREATE TABLE ppt_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    project_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    template_id VARCHAR(100),
    template_name VARCHAR(255),
    color_scheme_id VARCHAR(100),
    
    source_type VARCHAR(50) DEFAULT 'text',
    source_content TEXT,
    source_document_id UUID REFERENCES documents(id),
    
    slide_count INT,
    max_points_per_slide INT DEFAULT 5,
    include_visuals BOOLEAN DEFAULT TRUE,
    auto_generate_speaker_notes BOOLEAN DEFAULT FALSE,
    
    pptx_file_path VARCHAR(255),
    file_size_bytes BIGINT,
    
    status ppt_project_status DEFAULT 'draft',
    progress_percentage INT DEFAULT 0,
    
    version_number INT DEFAULT 1,
    last_edited_by UUID REFERENCES users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exported_at TIMESTAMP
);

CREATE INDEX idx_ppt_projects_user_id ON ppt_projects(user_id);
CREATE INDEX idx_ppt_projects_status ON ppt_projects(status);
CREATE INDEX idx_ppt_projects_created_at ON ppt_projects(created_at DESC);

CREATE TABLE ppt_slides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ppt_project_id UUID NOT NULL REFERENCES ppt_projects(id) ON DELETE CASCADE,
    
    slide_number INT NOT NULL,
    slide_title VARCHAR(255),
    slide_type slide_type DEFAULT 'content',
    
    content_text TEXT,
    bullet_points TEXT[],
    notes_for_speaker TEXT,
    
    background_color VARCHAR(7),
    background_image_path VARCHAR(255),
    has_visualization BOOLEAN DEFAULT FALSE,
    visualization_type VARCHAR(50),
    
    layout_template VARCHAR(100),
    font_family VARCHAR(50),
    font_size INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_slide_number CHECK (slide_number >= 1)
);

CREATE INDEX idx_ppt_slides_project_id ON ppt_slides(ppt_project_id);
CREATE INDEX idx_ppt_slides_number ON ppt_slides(ppt_project_id, slide_number);

CREATE TABLE ppt_visualizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ppt_slide_id UUID NOT NULL REFERENCES ppt_slides(id) ON DELETE CASCADE,
    
    viz_type viz_type NOT NULL,
    viz_subtype VARCHAR(50),
    
    data_source VARCHAR(50),
    data_json JSONB,
    
    image_path VARCHAR(255),
    image_alt_text TEXT,
    
    position_left INT,
    position_top INT,
    width INT,
    height INT,
    
    color_scheme VARCHAR(100),
    title VARCHAR(255),
    description TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ppt_visualizations_slide_id ON ppt_visualizations(ppt_slide_id);

-- ============================================================
-- 第八部分：周报生成模块表
-- ============================================================

CREATE TABLE work_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    log_date DATE NOT NULL,
    work_type work_type DEFAULT 'development',
    
    task_description TEXT NOT NULL,
    detailed_notes TEXT,
    
    hours_spent FLOAT,
    start_time TIME,
    end_time TIME,
    
    project_id VARCHAR(100),
    project_name VARCHAR(255),
    task_category VARCHAR(100),
    tags TEXT[],
    
    achievements TEXT,
    deliverables TEXT,
    
    challenges TEXT,
    blockers TEXT,
    blocker_resolution_status blocker_status,
    
    learning_points TEXT,
    skills_improved TEXT[],
    
    attachments JSONB,
    
    status log_status DEFAULT 'draft',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_work_logs_user_id ON work_logs(user_id);
CREATE INDEX idx_work_logs_date ON work_logs(log_date DESC);
CREATE INDEX idx_work_logs_type ON work_logs(work_type);

CREATE TABLE weekly_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    report_year INT,
    report_week INT,
    
    title VARCHAR(255),
    executive_summary TEXT,
    detailed_summary TEXT,
    
    total_hours_worked FLOAT,
    tasks_completed INT,
    tasks_in_progress INT,
    
    work_breakdown JSONB,
    projects_involved TEXT[],
    
    key_achievements TEXT[],
    challenges_faced TEXT[],
    blockers TEXT[],
    solutions_implemented TEXT[],
    
    learning_points TEXT[],
    skills_improved TEXT[],
    
    next_week_plan TEXT,
    next_week_focus_areas TEXT[],
    
    completeness_score FLOAT,
    professionalism_score FLOAT,
    actionability_score FLOAT,
    
    review_status report_review_status DEFAULT 'draft',
    reviewed_by UUID REFERENCES users(id),
    review_feedback TEXT,
    reviewed_at TIMESTAMP,
    
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    visibility meeting_visibility DEFAULT 'private',
    
    exported_formats JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT report_date_logic CHECK (week_end_date > week_start_date)
);

CREATE INDEX idx_weekly_reports_user_id ON weekly_reports(user_id);
CREATE INDEX idx_weekly_reports_week ON weekly_reports(week_start_date DESC);
CREATE INDEX idx_weekly_reports_status ON weekly_reports(review_status);

CREATE TABLE report_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    weekly_report_id UUID NOT NULL REFERENCES weekly_reports(id) ON DELETE CASCADE,
    
    metric_name VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50),
    metric_value FLOAT,
    metric_unit VARCHAR(20),
    
    previous_week_value FLOAT,
    target_value FLOAT,
    variance FLOAT,
    variance_percentage FLOAT,
    
    status VARCHAR(20) DEFAULT 'on_track',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_report_metrics_report_id ON report_metrics(weekly_report_id);

-- ============================================================
-- 第九部分：通用模块表
-- ============================================================

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    file_name VARCHAR(255) NOT NULL,
    file_extension VARCHAR(10),
    mime_type VARCHAR(100),
    
    storage_path VARCHAR(500),
    storage_url VARCHAR(500),
    file_size_bytes BIGINT,
    
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    
    metadata JSONB,
    
    visibility document_visibility DEFAULT 'private',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_related ON files(related_entity_type, related_entity_id);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    notification_type notification_type NOT NULL,
    title VARCHAR(255),
    message TEXT,
    
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    
    is_read BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    
    priority notification_priority DEFAULT 'normal',
    
    action_url VARCHAR(255),
    action_buttons JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, is_read);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    
    action_type VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id UUID,
    
    old_value JSONB,
    new_value JSONB,
    change_summary TEXT,
    
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- ============================================================
-- 第十部分：缓存表
-- ============================================================

CREATE TABLE cache_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    CONSTRAINT cache_not_expired CHECK (expires_at > created_at)
);

CREATE INDEX idx_cache_expires_at ON cache_entries(expires_at);

-- ============================================================
-- 创建视图
-- ============================================================

-- 活跃用户视图
CREATE OR REPLACE VIEW active_users AS
SELECT id, username, email, full_name, organization, position, last_login_at, created_at
FROM users
WHERE status = 'active' AND deleted_at IS NULL;

-- 待处理的会议纪要视图
CREATE OR REPLACE VIEW pending_minutes AS
SELECT m.id, m.title, m.start_time, m.end_time, u.full_name as organizer, mm.review_status
FROM meetings m
LEFT JOIN users u ON m.organizer_id = u.id
LEFT JOIN meeting_minutes mm ON m.id = mm.meeting_id
WHERE mm.review_status IN ('pending', 'reviewing');

-- 逾期的Action Items视图
CREATE OR REPLACE VIEW overdue_actions AS
SELECT ai.id, ai.task_description, ai.due_date, u.full_name as assigned_to, ai.priority
FROM action_items ai
LEFT JOIN users u ON ai.assigned_to_id = u.id
WHERE ai.status != 'completed' AND ai.due_date < CURRENT_DATE;

-- ============================================================
-- 完成
-- ============================================================

COMMIT;
VACUUM ANALYZE;

-- 执行完成，系统已准备好！
