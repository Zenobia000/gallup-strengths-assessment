"""
Unified SQLAlchemy Database Engine
統一的 SQLAlchemy 資料庫引擎

完全替代舊的 utils/database.py SQLite 實現
支援完整的 V4 Thurstonian IRT 系統

設計原則：
- Linus 好品味：簡潔、可靠、專注
- Never break userspace：向後相容
- 統一 session 管理
- 完整的 V4 支援
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path

# 導入所有模型
from models.database import Base, create_indexes
from models.v4_models import V4_TABLE_NAMES, create_v4_indexes, update_consent_relationships
from core.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseEngine:
    """
    統一資料庫引擎

    管理 SQLAlchemy engine, session 和 schema 初始化
    支援 SQLite (開發) 和 PostgreSQL (生產)
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        初始化資料庫引擎

        Args:
            database_url: 資料庫連接URL，若為None則從設定讀取
        """
        self.settings = get_settings()
        self.database_url = database_url or self.settings.database_url

        # 建立引擎
        self.engine = self._create_engine()

        # 建立 session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # 初始化 schema
        self._initialize_schema()

        logger.info(f"Database engine initialized: {self._mask_db_url()}")

    def _create_engine(self):
        """建立 SQLAlchemy 引擎"""

        if self.database_url.startswith("sqlite"):
            # SQLite 配置
            db_path = self.database_url.replace("sqlite:///", "")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

            engine = create_engine(
                self.database_url,
                # SQLite 最佳化設定
                poolclass=StaticPool,
                pool_pre_ping=True,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                },
                echo=getattr(self.settings, 'debug', False)  # 開發時顯示 SQL
            )

            # SQLite 特殊設定
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                # 效能最佳化
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        else:
            # PostgreSQL 或其他資料庫
            engine = create_engine(
                self.database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=getattr(self.settings, 'debug', False)
            )

        return engine

    def _initialize_schema(self):
        """初始化資料庫 schema"""
        try:
            # 更新關聯 (V4 與原有模型的關聯)
            update_consent_relationships()

            # 建立所有資料表
            Base.metadata.create_all(bind=self.engine)

            # 建立索引 (在表格創建後)
            try:
                create_indexes(self.engine)
                create_v4_indexes(self.engine)
            except Exception as e:
                logger.warning(f"Index creation failed (will retry): {e}")
                # 索引失敗不影響基本功能

            # 初始化種子資料
            self._seed_initial_data()

            logger.info("Database schema initialized successfully")

        except Exception as e:
            logger.error(f"Database schema initialization failed: {e}")
            raise

    def _seed_initial_data(self):
        """初始化種子資料"""
        with self.get_session() as session:
            try:
                # 檢查是否已有資料
                from models.v4_models import V4Statement
                existing_statements = session.query(V4Statement).count()

                if existing_statements == 0:
                    # 載入 V4 語句資料
                    self._seed_v4_statements(session)
                    logger.info("V4 statements seeded successfully")

                # 可以在這裡添加其他種子資料
                session.commit()

            except Exception as e:
                session.rollback()
                logger.error(f"Seed data initialization failed: {e}")
                raise

    def _seed_v4_statements(self, session: Session):
        """載入 V4 語句庫"""
        from models.v4_models import V4Statement
        from data.v4_statements import STATEMENT_POOL

        statements_to_add = []

        for dimension, statements in STATEMENT_POOL.items():
            for stmt_data in statements:
                statement = V4Statement(
                    statement_id=stmt_data["statement_id"],
                    dimension=dimension,
                    text=stmt_data["text"],
                    social_desirability=stmt_data["social_desirability"],
                    context=stmt_data["context"],
                    factor_loading=stmt_data.get("factor_loading", 0.7)
                )
                statements_to_add.append(statement)

        session.add_all(statements_to_add)
        logger.info(f"Added {len(statements_to_add)} V4 statements")

    @contextmanager
    def get_session(self):
        """
        獲取資料庫 session 的 context manager

        自動處理 commit/rollback 和 session 清理
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_session_factory(self):
        """取得 session factory (用於 FastAPI Depends)"""
        return self.SessionLocal

    def _mask_db_url(self) -> str:
        """遮罩資料庫 URL 中的敏感資訊"""
        if "://" not in self.database_url:
            return self.database_url

        scheme, rest = self.database_url.split("://", 1)
        if "@" in rest:
            # 有認證資訊
            auth_part, host_part = rest.split("@", 1)
            return f"{scheme}://***@{host_part}"
        else:
            return self.database_url

    def health_check(self) -> Dict[str, Any]:
        """資料庫健康檢查"""
        try:
            with self.get_session() as session:
                # 執行簡單查詢測試連接
                result = session.execute(text("SELECT 1")).fetchone()

                # 檢查資料表
                from sqlalchemy import inspect
                inspector = inspect(self.engine)
                table_count = len(inspector.get_table_names())

                return {
                    "status": "healthy",
                    "database_url": self._mask_db_url(),
                    "table_count": table_count,
                    "connection_test": "passed"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database_url": self._mask_db_url(),
                "error": str(e),
                "connection_test": "failed"
            }

    def drop_all_tables(self):
        """刪除所有資料表 (慎用！)"""
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All tables dropped")

    def recreate_all_tables(self):
        """重建所有資料表"""
        logger.warning("Recreating all database tables...")
        self.drop_all_tables()
        self._initialize_schema()
        logger.info("All tables recreated successfully")


# 全域資料庫引擎實例
_db_engine: Optional[DatabaseEngine] = None


def get_database_engine() -> DatabaseEngine:
    """取得全域資料庫引擎單例"""
    global _db_engine
    if _db_engine is None:
        _db_engine = DatabaseEngine()
    return _db_engine


def get_db_session():
    """FastAPI dependency: 取得資料庫 session"""
    engine = get_database_engine()
    with engine.get_session() as session:
        yield session


@contextmanager
def get_session():
    """便利函式：取得資料庫 session"""
    engine = get_database_engine()
    with engine.get_session() as session:
        yield session


def init_database(force_recreate: bool = False):
    """
    初始化資料庫

    Args:
        force_recreate: 是否強制重建所有資料表
    """
    engine = get_database_engine()

    if force_recreate:
        engine.recreate_all_tables()

    return engine


# 向後相容：提供與舊 API 相同的介面
def get_database_manager():
    """向後相容：模擬舊的 DatabaseManager"""
    return get_database_engine()


def get_db_connection():
    """向後相容：提供類似舊 API 的連接管理"""
    return get_session()