"""
SQLAlchemy Database Configuration and Utilities
為計分 API 提供 SQLAlchemy 支援

功能包含:
- SQLAlchemy 引擎配置
- 會話管理
- 依賴注入
- 資料庫初始化
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os
from pathlib import Path

from core.config import get_settings
from models.database import Base

# 全域變數
engine = None
SessionLocal = None


def get_database_url() -> str:
    """取得資料庫 URL"""
    settings = get_settings()
    return settings.database_url


def create_database_engine():
    """建立 SQLAlchemy 引擎"""
    database_url = get_database_url()

    # SQLite 特殊配置
    if database_url.startswith("sqlite"):
        # 確保資料庫目錄存在
        db_path = database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        return create_engine(
            database_url,
            connect_args={
                "check_same_thread": False,
                "timeout": 20
            },
            poolclass=StaticPool,
            echo=False  # 設為 True 可看到 SQL 語句
        )
    else:
        return create_engine(database_url)


def init_database():
    """初始化資料庫"""
    global engine, SessionLocal

    if engine is None:
        engine = create_database_engine()

    if SessionLocal is None:
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )

    # 建立所有資料表
    Base.metadata.create_all(bind=engine)

    # 建立索引
    from models.database import create_indexes
    create_indexes(engine)


def get_db() -> Generator[Session, None, None]:
    """
    取得資料庫會話 (FastAPI 依賴注入)

    用法:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            ...
    """
    if SessionLocal is None:
        init_database()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """取得新的資料庫會話 (手動管理)"""
    if SessionLocal is None:
        init_database()

    return SessionLocal()


# 在模組載入時初始化資料庫
init_database()


# 資料庫操作工具類
class DatabaseManager:
    """資料庫管理器"""

    @staticmethod
    def execute_raw_sql(sql: str, params: dict = None):
        """執行原生 SQL"""
        with get_db_session() as db:
            return db.execute(sql, params or {}).fetchall()

    @staticmethod
    def get_table_info(table_name: str):
        """取得資料表資訊"""
        sql = f"PRAGMA table_info({table_name})"
        return DatabaseManager.execute_raw_sql(sql)

    @staticmethod
    def backup_database(backup_path: str):
        """備份資料庫 (SQLite only)"""
        import shutil
        database_url = get_database_url()

        if not database_url.startswith("sqlite"):
            raise NotImplementedError("Backup only supported for SQLite")

        source_path = database_url.replace("sqlite:///", "")
        shutil.copy2(source_path, backup_path)

    @staticmethod
    def vacuum_database():
        """清理資料庫空間"""
        with get_db_session() as db:
            db.execute("VACUUM")
            db.commit()

    @staticmethod
    def get_database_stats() -> dict:
        """取得資料庫統計資訊"""
        stats = {}

        with get_db_session() as db:
            # 取得所有資料表
            tables_result = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()

            for (table_name,) in tables_result:
                # 計算每個資料表的記錄數
                count_result = db.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
                stats[table_name] = count_result[0] if count_result else 0

        return stats


# 測試函式
def test_database_connection() -> bool:
    """測試資料庫連接"""
    try:
        with get_db_session() as db:
            db.execute("SELECT 1").fetchone()
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False


if __name__ == "__main__":
    # 測試資料庫連接
    if test_database_connection():
        print("✅ Database connection successful")

        # 顯示資料庫統計
        stats = DatabaseManager.get_database_stats()
        print("📊 Database statistics:")
        for table, count in stats.items():
            print(f"  {table}: {count} records")
    else:
        print("❌ Database connection failed")