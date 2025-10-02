"""
Migration 004: Career Archetypes and Job Recommendations Tables

基於凱爾西氣質理論的職業原型表格系統：
- career_archetypes: 4種職業原型定義
- job_roles: 具體職位角色
- archetype_talents: 原型與才幹的關聯表
- user_archetype_results: 用戶職業原型分析結果
- job_recommendations: 職位推薦結果
"""

import json
from typing import Any, Dict


def apply_migration(conn: Any) -> None:
    """Apply migration 004: Career Archetypes system"""

    # 1. 職業原型主表 - 基於凱爾西氣質理論的4種原型
    conn.execute("""
        CREATE TABLE IF NOT EXISTS career_archetypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archetype_id TEXT UNIQUE NOT NULL,
            archetype_name TEXT NOT NULL,
            archetype_name_en TEXT NOT NULL,
            keirsey_temperament TEXT NOT NULL,
            mbti_correlates TEXT NOT NULL,  -- JSON array of MBTI types
            description TEXT NOT NULL,
            core_characteristics TEXT NOT NULL,  -- JSON array of characteristics
            work_environment_preferences TEXT NOT NULL,  -- JSON object
            leadership_style TEXT,
            decision_making_style TEXT,
            communication_style TEXT,
            stress_indicators TEXT,  -- JSON array
            development_areas TEXT,  -- JSON array
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT valid_archetype_id CHECK (length(archetype_id) > 0),
            CONSTRAINT valid_archetype_name CHECK (length(archetype_name) > 0)
        )
    """)

    # 2. 才幹維度主表 - 12個核心才幹維度
    conn.execute("""
        CREATE TABLE IF NOT EXISTS talent_dimensions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dimension_id TEXT UNIQUE NOT NULL,
            dimension_name TEXT NOT NULL,
            dimension_name_en TEXT NOT NULL,
            category TEXT NOT NULL,  -- 'executing', 'influencing', 'relationship', 'strategic'
            description TEXT NOT NULL,
            behavioral_indicators TEXT,  -- JSON array
            development_strategies TEXT,  -- JSON array
            assessment_questions TEXT,  -- JSON array of related questions
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT valid_dimension_id CHECK (dimension_id LIKE 'T%'),
            CONSTRAINT valid_category CHECK (category IN ('executing', 'influencing', 'relationship', 'strategic'))
        )
    """)

    # 3. 原型與才幹關聯表 - 多對多關係，包含權重
    conn.execute("""
        CREATE TABLE IF NOT EXISTS archetype_talents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archetype_id TEXT NOT NULL,
            dimension_id TEXT NOT NULL,
            talent_type TEXT NOT NULL,  -- 'primary', 'secondary', 'neutral', 'avoid'
            weight REAL NOT NULL DEFAULT 1.0,
            importance_level INTEGER NOT NULL DEFAULT 3,  -- 1-5 scale
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (archetype_id) REFERENCES career_archetypes(archetype_id),
            FOREIGN KEY (dimension_id) REFERENCES talent_dimensions(dimension_id),
            CONSTRAINT valid_talent_type CHECK (talent_type IN ('primary', 'secondary', 'neutral', 'avoid')),
            CONSTRAINT valid_weight CHECK (weight >= 0 AND weight <= 5.0),
            CONSTRAINT valid_importance CHECK (importance_level >= 1 AND importance_level <= 5),
            CONSTRAINT unique_archetype_dimension UNIQUE (archetype_id, dimension_id)
        )
    """)

    # 4. 職位角色表 - 具體職位定義
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id TEXT UNIQUE NOT NULL,
            role_name TEXT NOT NULL,
            role_name_en TEXT,
            industry_sector TEXT NOT NULL,
            job_family TEXT NOT NULL,
            seniority_level TEXT NOT NULL,  -- 'entry', 'mid', 'senior', 'executive'
            description TEXT NOT NULL,
            key_responsibilities TEXT NOT NULL,  -- JSON array
            required_skills TEXT NOT NULL,  -- JSON array
            preferred_skills TEXT,  -- JSON array
            required_talents TEXT NOT NULL,  -- JSON array of dimension_ids with weights
            beneficial_talents TEXT,  -- JSON array of dimension_ids with weights
            education_requirements TEXT,
            experience_requirements TEXT,
            salary_range_min INTEGER,
            salary_range_max INTEGER,
            currency TEXT DEFAULT 'TWD',
            work_arrangement TEXT,  -- 'remote', 'hybrid', 'onsite'
            career_growth_path TEXT,  -- JSON array of next role possibilities
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT valid_role_id CHECK (length(role_id) > 0),
            CONSTRAINT valid_seniority CHECK (seniority_level IN ('entry', 'mid', 'senior', 'executive')),
            CONSTRAINT valid_salary_range CHECK (salary_range_max >= salary_range_min)
        )
    """)

    # 5. 原型與職位關聯表 - 原型適合的職位推薦
    conn.execute("""
        CREATE TABLE IF NOT EXISTS archetype_job_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archetype_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            match_score REAL NOT NULL,  -- 0.0-1.0 compatibility score
            match_reasoning TEXT,  -- JSON object with detailed reasoning
            confidence_level REAL NOT NULL DEFAULT 0.8,
            priority_rank INTEGER,  -- 1-N ranking within archetype
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (archetype_id) REFERENCES career_archetypes(archetype_id),
            FOREIGN KEY (role_id) REFERENCES job_roles(role_id),
            CONSTRAINT valid_match_score CHECK (match_score >= 0.0 AND match_score <= 1.0),
            CONSTRAINT valid_confidence CHECK (confidence_level >= 0.0 AND confidence_level <= 1.0),
            CONSTRAINT unique_archetype_role UNIQUE (archetype_id, role_id)
        )
    """)

    # 6. 用戶職業原型分析結果表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_archetype_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            primary_archetype_id TEXT NOT NULL,
            secondary_archetype_id TEXT,
            archetype_scores TEXT NOT NULL,  -- JSON object with all 4 archetype scores
            dominant_talents TEXT NOT NULL,  -- JSON array of top talents with scores
            supporting_talents TEXT NOT NULL,  -- JSON array of supporting talents
            lesser_talents TEXT NOT NULL,  -- JSON array of weaker talents
            confidence_score REAL NOT NULL,
            analysis_metadata TEXT,  -- JSON object with analysis details
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (primary_archetype_id) REFERENCES career_archetypes(archetype_id),
            FOREIGN KEY (secondary_archetype_id) REFERENCES career_archetypes(archetype_id),
            CONSTRAINT valid_confidence CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
            CONSTRAINT unique_session_result UNIQUE (session_id)
        )
    """)

    # 7. 職位推薦結果表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            recommendation_type TEXT NOT NULL,  -- 'primary', 'stretch', 'development'
            match_score REAL NOT NULL,
            strength_alignment TEXT NOT NULL,  -- JSON object
            development_gaps TEXT,  -- JSON array of skills/talents to develop
            recommendation_reasoning TEXT NOT NULL,  -- JSON object with detailed explanation
            priority_rank INTEGER NOT NULL,
            confidence_level REAL NOT NULL,
            is_featured BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            FOREIGN KEY (role_id) REFERENCES job_roles(role_id),
            CONSTRAINT valid_recommendation_type CHECK (recommendation_type IN ('primary', 'stretch', 'development')),
            CONSTRAINT valid_match_score CHECK (match_score >= 0.0 AND match_score <= 1.0),
            CONSTRAINT valid_confidence CHECK (confidence_level >= 0.0 AND confidence_level <= 1.0),
            CONSTRAINT unique_session_role UNIQUE (session_id, role_id)
        )
    """)

    # 建立效能索引
    create_indexes(conn)

    # 載入種子資料
    seed_career_archetypes(conn)
    seed_talent_dimensions(conn)
    seed_archetype_talents(conn)
    seed_job_roles(conn)

    # 記錄遷移完成
    conn.execute("""
        INSERT INTO migrations (version, description)
        VALUES ('004', 'Career Archetypes and Job Recommendations System')
    """)


def create_indexes(conn: Any) -> None:
    """建立效能最佳化索引"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_archetype_talents_archetype ON archetype_talents(archetype_id)",
        "CREATE INDEX IF NOT EXISTS idx_archetype_talents_dimension ON archetype_talents(dimension_id)",
        "CREATE INDEX IF NOT EXISTS idx_job_roles_industry ON job_roles(industry_sector)",
        "CREATE INDEX IF NOT EXISTS idx_job_roles_seniority ON job_roles(seniority_level)",
        "CREATE INDEX IF NOT EXISTS idx_job_roles_active ON job_roles(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_archetype_matches_archetype ON archetype_job_matches(archetype_id)",
        "CREATE INDEX IF NOT EXISTS idx_archetype_matches_score ON archetype_job_matches(match_score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_user_results_session ON user_archetype_results(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_job_recommendations_session ON job_recommendations(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_job_recommendations_score ON job_recommendations(match_score DESC)"
    ]

    for index_sql in indexes:
        conn.execute(index_sql)


def seed_career_archetypes(conn: Any) -> None:
    """載入4種凱爾西氣質理論職業原型"""
    archetypes = [
        {
            "archetype_id": "ARCHITECT",
            "archetype_name": "系統建構者",
            "archetype_name_en": "System Architect",
            "keirsey_temperament": "理性者 (Rational)",
            "mbti_correlates": json.dumps(["INTJ", "INTP", "ENTJ", "ENTP"]),
            "description": "天生的系統思考者與建構者，擅長將複雜的資訊轉化為清晰的藍圖與高效的流程。注重邏輯、效率與長期規劃。",
            "core_characteristics": json.dumps([
                "系統性思維", "邏輯分析能力", "長期規劃", "效率導向",
                "創新思考", "問題解決", "理性決策", "獨立工作"
            ]),
            "work_environment_preferences": json.dumps({
                "structure": "high",
                "autonomy": "high",
                "collaboration": "medium",
                "routine": "low",
                "innovation": "high"
            }),
            "leadership_style": "策略型領導，注重長期願景和系統優化",
            "decision_making_style": "基於數據和邏輯分析的理性決策",
            "communication_style": "直接、簡潔、事實導向",
            "stress_indicators": json.dumps([
                "被迫做重複性工作", "缺乏自主權", "過度社交要求", "不合理的時間壓力"
            ]),
            "development_areas": json.dumps([
                "人際關係建立", "情感表達", "團隊協作", "耐心培養"
            ])
        },
        {
            "archetype_id": "GUARDIAN",
            "archetype_name": "組織守護者",
            "archetype_name_en": "Organization Guardian",
            "keirsey_temperament": "守護者 (Guardian)",
            "mbti_correlates": json.dumps(["ISTJ", "ISFJ", "ESTJ", "ESFJ"]),
            "description": "可靠的執行者與維護者，擅長建立和維護穩定的系統，並確保任務按時、按質完成。注重責任、紀律與品質。",
            "core_characteristics": json.dumps([
                "責任感", "紀律性", "品質導向", "可靠性",
                "組織能力", "細節關注", "傳統價值", "服務精神"
            ]),
            "work_environment_preferences": json.dumps({
                "structure": "high",
                "autonomy": "medium",
                "collaboration": "high",
                "routine": "high",
                "innovation": "medium"
            }),
            "leadership_style": "服務型領導，注重團隊穩定和流程優化",
            "decision_making_style": "基於經驗和既定程序的穩健決策",
            "communication_style": "詳細、準確、支持性",
            "stress_indicators": json.dumps([
                "過度變化", "模糊的期望", "缺乏資源", "衝突環境"
            ]),
            "development_areas": json.dumps([
                "創新思維", "變化適應", "策略思考", "風險承擔"
            ])
        },
        {
            "archetype_id": "IDEALIST",
            "archetype_name": "人文關懷家",
            "archetype_name_en": "Humanistic Idealist",
            "keirsey_temperament": "理想主義者 (Idealist)",
            "mbti_correlates": json.dumps(["INFJ", "INFP", "ENFJ", "ENFP"]),
            "description": "以人為本的溝通者與賦能者，擅長理解他人、建立關係並激勵團隊。注重和諧、成長與共同價值。",
            "core_characteristics": json.dumps([
                "同理心", "人際敏感度", "價值導向", "成長導向",
                "激勵他人", "創意思考", "和諧建立", "意義追求"
            ]),
            "work_environment_preferences": json.dumps({
                "structure": "medium",
                "autonomy": "high",
                "collaboration": "high",
                "routine": "low",
                "innovation": "high"
            }),
            "leadership_style": "啟發型領導，注重人員發展和團隊凝聚力",
            "decision_making_style": "基於價值觀和人員影響的全面考量",
            "communication_style": "溫暖、啟發性、個人化",
            "stress_indicators": json.dumps([
                "價值觀衝突", "人際關係緊張", "過度批評", "缺乏意義感"
            ]),
            "development_areas": json.dumps([
                "邏輯分析", "衝突處理", "決斷力", "自我照顧"
            ])
        },
        {
            "archetype_id": "ARTISAN",
            "archetype_name": "推廣實踐家",
            "archetype_name_en": "Promotion Practitioner",
            "keirsey_temperament": "工匠 (Artisan)",
            "mbti_correlates": json.dumps(["ESTP", "ESFP", "ISTP", "ISFP"]),
            "description": "充滿活力的行動派與連結者，擅長將想法付諸實踐，並在與人互動中獲得能量。注重結果、效率與人際關係。",
            "core_characteristics": json.dumps([
                "行動導向", "適應靈活", "人際影響力", "實務導向",
                "壓力管理", "即時反應", "機會把握", "結果導向"
            ]),
            "work_environment_preferences": json.dumps({
                "structure": "low",
                "autonomy": "high",
                "collaboration": "high",
                "routine": "low",
                "innovation": "medium"
            }),
            "leadership_style": "魅力型領導，注重激勵和即時問題解決",
            "decision_making_style": "基於直覺和實際情況的快速決策",
            "communication_style": "生動、有感染力、互動性強",
            "stress_indicators": json.dumps([
                "過度規則限制", "長期規劃壓力", "缺乏人際互動", "單調重複工作"
            ]),
            "development_areas": json.dumps([
                "長期規劃", "系統思考", "細節關注", "耐心培養"
            ])
        }
    ]

    for archetype in archetypes:
        conn.execute("""
            INSERT OR REPLACE INTO career_archetypes
            (archetype_id, archetype_name, archetype_name_en, keirsey_temperament,
             mbti_correlates, description, core_characteristics, work_environment_preferences,
             leadership_style, decision_making_style, communication_style,
             stress_indicators, development_areas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            archetype["archetype_id"], archetype["archetype_name"], archetype["archetype_name_en"],
            archetype["keirsey_temperament"], archetype["mbti_correlates"], archetype["description"],
            archetype["core_characteristics"], archetype["work_environment_preferences"],
            archetype["leadership_style"], archetype["decision_making_style"],
            archetype["communication_style"], archetype["stress_indicators"], archetype["development_areas"]
        ))


def seed_talent_dimensions(conn: Any) -> None:
    """載入12個才幹維度定義"""
    dimensions = [
        ("T1", "結構化執行", "Structured Execution", "executing", "建立系統化的工作流程和執行框架"),
        ("T2", "品質與完備", "Quality & Completeness", "executing", "追求高品質標準和完善的成果"),
        ("T3", "探索與創新", "Exploration & Innovation", "strategic", "主動探索新可能性和創新解決方案"),
        ("T4", "分析與洞察", "Analysis & Insight", "strategic", "深入分析複雜問題並產生洞察"),
        ("T5", "影響與倡議", "Influence & Advocacy", "influencing", "影響他人並推動倡議的能力"),
        ("T6", "協作與共好", "Collaboration & Synergy", "relationship", "建立協作關係並追求共同利益"),
        ("T7", "客戶導向", "Customer Orientation", "relationship", "以客戶需求為中心的服務意識"),
        ("T8", "學習與成長", "Learning & Growth", "strategic", "持續學習和個人成長的驅動力"),
        ("T9", "紀律與信任", "Discipline & Trust", "executing", "維持紀律性和建立信任關係"),
        ("T10", "壓力調節", "Stress Regulation", "relationship", "在壓力下保持穩定和調節能力"),
        ("T11", "衝突整合", "Conflict Integration", "relationship", "處理衝突並找到整合解決方案"),
        ("T12", "責任與當責", "Responsibility & Accountability", "executing", "承擔責任並對結果負責")
    ]

    for dim_id, name_zh, name_en, category, description in dimensions:
        conn.execute("""
            INSERT OR REPLACE INTO talent_dimensions
            (dimension_id, dimension_name, dimension_name_en, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (dim_id, name_zh, name_en, category, description))


def seed_archetype_talents(conn: Any) -> None:
    """載入原型與才幹的關聯關係"""
    # 基於原有的 archetype_mapper.py 定義
    mappings = [
        # ARCHITECT (系統建構者)
        ("ARCHITECT", "T4", "primary", 3.0, 5),    # 分析與洞察
        ("ARCHITECT", "T1", "primary", 3.0, 5),    # 結構化執行
        ("ARCHITECT", "T3", "secondary", 2.0, 4),  # 探索與創新
        ("ARCHITECT", "T8", "secondary", 2.0, 4),  # 學習與成長
        ("ARCHITECT", "T12", "secondary", 2.0, 4), # 責任與當責

        # GUARDIAN (組織守護者)
        ("GUARDIAN", "T12", "primary", 3.0, 5),    # 責任與當責
        ("GUARDIAN", "T9", "primary", 3.0, 5),     # 紀律與信任
        ("GUARDIAN", "T2", "secondary", 2.0, 4),   # 品質與完備
        ("GUARDIAN", "T1", "secondary", 2.0, 4),   # 結構化執行
        ("GUARDIAN", "T6", "secondary", 2.0, 4),   # 協作與共好

        # IDEALIST (人文關懷家)
        ("IDEALIST", "T6", "primary", 3.0, 5),     # 協作與共好
        ("IDEALIST", "T8", "primary", 3.0, 5),     # 學習與成長
        ("IDEALIST", "T5", "secondary", 2.0, 4),   # 影響與倡議
        ("IDEALIST", "T11", "secondary", 2.0, 4),  # 衝突整合
        ("IDEALIST", "T7", "secondary", 2.0, 4),   # 客戶導向

        # ARTISAN (推廣實踐家)
        ("ARTISAN", "T5", "primary", 3.0, 5),      # 影響與倡議
        ("ARTISAN", "T10", "primary", 3.0, 5),     # 壓力調節
        ("ARTISAN", "T3", "secondary", 2.0, 4),    # 探索與創新
        ("ARTISAN", "T7", "secondary", 2.0, 4),    # 客戶導向
        ("ARTISAN", "T11", "secondary", 2.0, 4),   # 衝突整合
    ]

    for archetype_id, dimension_id, talent_type, weight, importance in mappings:
        conn.execute("""
            INSERT OR REPLACE INTO archetype_talents
            (archetype_id, dimension_id, talent_type, weight, importance_level)
            VALUES (?, ?, ?, ?, ?)
        """, (archetype_id, dimension_id, talent_type, weight, importance))


def seed_job_roles(conn: Any) -> None:
    """載入基礎職位角色資料"""
    # 基於原有的 career_matcher.py 和 archetype_mapper.py 的職位建議
    job_roles = [
        # ARCHITECT 相關職位
        {
            "role_id": "ARCH_001",
            "role_name": "軟體架構師",
            "industry_sector": "Technology",
            "job_family": "Engineering",
            "seniority_level": "senior",
            "description": "設計和維護大型軟體系統的整體架構",
            "key_responsibilities": json.dumps([
                "系統架構設計", "技術決策制定", "代碼審查", "團隊技術指導"
            ]),
            "required_skills": json.dumps([
                "系統設計", "程式語言精通", "架構模式", "性能優化"
            ]),
            "required_talents": json.dumps([
                {"dimension_id": "T4", "weight": 3.0},
                {"dimension_id": "T1", "weight": 3.0}
            ])
        },
        {
            "role_id": "ARCH_002",
            "role_name": "策略顧問",
            "industry_sector": "Consulting",
            "job_family": "Strategy",
            "seniority_level": "mid",
            "description": "為企業提供策略規劃和業務轉型建議",
            "key_responsibilities": json.dumps([
                "策略分析", "市場研究", "客戶諮詢", "方案設計"
            ]),
            "required_skills": json.dumps([
                "策略思維", "分析能力", "簡報技巧", "專案管理"
            ]),
            "required_talents": json.dumps([
                {"dimension_id": "T4", "weight": 3.0},
                {"dimension_id": "T3", "weight": 2.5}
            ])
        },

        # GUARDIAN 相關職位
        {
            "role_id": "GUARD_001",
            "role_name": "專案經理",
            "industry_sector": "Various",
            "job_family": "Management",
            "seniority_level": "mid",
            "description": "負責專案規劃、執行和交付管理",
            "key_responsibilities": json.dumps([
                "專案規劃", "進度管控", "風險管理", "團隊協調"
            ]),
            "required_skills": json.dumps([
                "專案管理", "溝通協調", "風險控制", "時程管理"
            ]),
            "required_talents": json.dumps([
                {"dimension_id": "T12", "weight": 3.0},
                {"dimension_id": "T9", "weight": 3.0}
            ])
        },

        # IDEALIST 相關職位
        {
            "role_id": "IDEAL_001",
            "role_name": "人力資源經理",
            "industry_sector": "Various",
            "job_family": "Human Resources",
            "seniority_level": "mid",
            "description": "負責人才發展、組織文化和員工關係管理",
            "key_responsibilities": json.dumps([
                "人才招募", "績效管理", "組織發展", "員工關係"
            ]),
            "required_skills": json.dumps([
                "人際溝通", "衝突處理", "組織心理學", "法規知識"
            ]),
            "required_talents": json.dumps([
                {"dimension_id": "T6", "weight": 3.0},
                {"dimension_id": "T8", "weight": 2.5}
            ])
        },

        # ARTISAN 相關職位
        {
            "role_id": "ART_001",
            "role_name": "市場行銷專家",
            "industry_sector": "Marketing",
            "job_family": "Marketing",
            "seniority_level": "mid",
            "description": "負責品牌推廣、市場策略和客戶關係管理",
            "key_responsibilities": json.dumps([
                "市場分析", "品牌推廣", "活動企劃", "客戶管理"
            ]),
            "required_skills": json.dumps([
                "市場分析", "創意企劃", "數位行銷", "客戶關係管理"
            ]),
            "required_talents": json.dumps([
                {"dimension_id": "T5", "weight": 3.0},
                {"dimension_id": "T10", "weight": 2.5}
            ])
        }
    ]

    for role in job_roles:
        conn.execute("""
            INSERT OR REPLACE INTO job_roles
            (role_id, role_name, industry_sector, job_family, seniority_level,
             description, key_responsibilities, required_skills, required_talents)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            role["role_id"], role["role_name"], role["industry_sector"],
            role["job_family"], role["seniority_level"], role["description"],
            role["key_responsibilities"], role["required_skills"], role["required_talents"]
        ))