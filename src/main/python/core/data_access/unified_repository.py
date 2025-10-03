"""
Unified Repository Pattern

統一的資料存取層，解決多重資料庫管理問題：
- 抽象資料存取介面
- 支援 SQLite 和 SQLAlchemy
- 事務管理統一化
- 查詢最佳化

遵循 Repository Pattern 和 Linus 簡潔原則
"""

from typing import Dict, List, Any, Optional, Protocol, TypeVar, Generic
from abc import ABC, abstractmethod
from contextlib import contextmanager
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Repository(Protocol, Generic[T]):
    """資料儲存庫協議"""

    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """根據 ID 查找實體"""
        ...

    @abstractmethod
    def find_all(self, filters: Dict[str, Any] = None) -> List[T]:
        """查找所有符合條件的實體"""
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        """儲存實體"""
        ...

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """刪除實體"""
        ...


class DatabaseAdapter(ABC):
    """資料庫適配器抽象基類"""

    @abstractmethod
    @contextmanager
    def get_connection(self):
        """獲取資料庫連接"""
        ...

    @abstractmethod
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """執行查詢"""
        ...

    @abstractmethod
    def execute_command(self, command: str, params: tuple = ()) -> int:
        """執行命令（INSERT/UPDATE/DELETE）"""
        ...


class SQLiteAdapter(DatabaseAdapter):
    """SQLite 資料庫適配器"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """獲取 SQLite 連接"""
        from utils.database import get_database_manager
        db_manager = get_database_manager()
        with db_manager.get_connection() as conn:
            yield conn

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """執行 SQLite 查詢"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def execute_command(self, command: str, params: tuple = ()) -> int:
        """執行 SQLite 命令"""
        with self.get_connection() as conn:
            cursor = conn.execute(command, params)
            return cursor.rowcount


class SQLAlchemyAdapter(DatabaseAdapter):
    """SQLAlchemy 資料庫適配器"""

    def __init__(self):
        from utils.sqlalchemy_db import get_db_session
        self.get_session = get_db_session

    @contextmanager
    def get_connection(self):
        """獲取 SQLAlchemy 會話"""
        session = next(self.get_session())
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """執行 SQLAlchemy 查詢"""
        with self.get_connection() as session:
            result = session.execute(query, params)
            return [dict(row) for row in result]

    def execute_command(self, command: str, params: tuple = ()) -> int:
        """執行 SQLAlchemy 命令"""
        with self.get_connection() as session:
            result = session.execute(command, params)
            return result.rowcount


# 具體儲存庫實作
class AssessmentSessionRepository:
    """評測會話儲存庫"""

    def __init__(self, adapter: DatabaseAdapter):
        self.adapter = adapter

    def find_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """查找評測會話"""
        query = """
            SELECT session_id, status, created_at, completed_at, metadata
            FROM sessions
            WHERE session_id = ?
            UNION ALL
            SELECT session_id, 'COMPLETED' as status, created_at,
                   completed_at, NULL as metadata
            FROM v4_sessions WHERE session_id = ?
        """
        results = self.adapter.execute_query(query, (session_id, session_id))
        return results[0] if results else None

    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """儲存會話資料"""
        # 根據版本選擇適當的表格
        if session_data.get('method') == 'v4':
            query = """
                INSERT OR REPLACE INTO v4_sessions
                (session_id, blocks_data, created_at)
                VALUES (?, ?, datetime('now'))
            """
            params = (session_data['session_id'], json.dumps(session_data.get('blocks_data', {})))
        else:
            query = """
                INSERT OR REPLACE INTO sessions
                (session_id, consent_id, status, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (
                session_data['session_id'],
                session_data.get('consent_id', ''),
                session_data.get('status', 'PENDING'),
                session_data.get('expires_at'),
                json.dumps(session_data.get('metadata', {}))
            )

        self.adapter.execute_command(query, params)
        return True


class ScoreRepository:
    """計分結果儲存庫"""

    def __init__(self, adapter: DatabaseAdapter):
        self.adapter = adapter

    def find_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """根據會話查找分數"""
        # 先查 v4 結果
        v4_query = """
            SELECT session_id, theta_scores, norm_scores, profile, completed_at
            FROM v4_assessment_results
            WHERE session_id = ?
        """
        results = self.adapter.execute_query(v4_query, (session_id,))
        if results:
            result = results[0]
            return {
                'session_id': result['session_id'],
                'method': 'v4',
                'theta_scores': json.loads(result['theta_scores']) if result['theta_scores'] else {},
                'norm_scores': json.loads(result['norm_scores']) if result['norm_scores'] else {},
                'profile': json.loads(result['profile']) if result['profile'] else {},
                'completed_at': result['completed_at']
            }

        # 再查 v1 結果
        v1_query = """
            SELECT session_id, extraversion, agreeableness, conscientiousness,
                   neuroticism, openness, strength_scores, calculated_at
            FROM scores
            WHERE session_id = ?
        """
        results = self.adapter.execute_query(v1_query, (session_id,))
        if results:
            result = results[0]
            return {
                'session_id': result['session_id'],
                'method': 'v1',
                'big_five_scores': {
                    'extraversion': result['extraversion'],
                    'agreeableness': result['agreeableness'],
                    'conscientiousness': result['conscientiousness'],
                    'neuroticism': result['neuroticism'],
                    'openness': result['openness']
                },
                'strength_scores': json.loads(result['strength_scores']) if result['strength_scores'] else {},
                'completed_at': result['calculated_at']
            }

        return None

    def save_v4_scores(self, session_id: str, scores_data: Dict[str, Any]) -> bool:
        """儲存 V4 分數"""
        query = """
            INSERT OR REPLACE INTO v4_assessment_results
            (session_id, responses, theta_scores, norm_scores, profile, completed_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        params = (
            session_id,
            json.dumps(scores_data.get('responses', [])),
            json.dumps(scores_data.get('theta_scores', {})),
            json.dumps(scores_data.get('norm_scores', {})),
            json.dumps(scores_data.get('profile', {}))
        )

        self.adapter.execute_command(query, params)
        return True

    def save_v1_scores(self, session_id: str, scores_data: Dict[str, Any]) -> bool:
        """儲存 V1 分數"""
        query = """
            INSERT OR REPLACE INTO scores
            (session_id, extraversion, agreeableness, conscientiousness,
             neuroticism, openness, strength_scores, provenance,
             algorithm_version, weights_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        big_five = scores_data.get('big_five_scores', {})
        params = (
            session_id,
            big_five.get('extraversion', 0),
            big_five.get('agreeableness', 0),
            big_five.get('conscientiousness', 0),
            big_five.get('neuroticism', 0),
            big_five.get('openness', 0),
            json.dumps(scores_data.get('strength_scores', {})),
            json.dumps(scores_data.get('provenance', {})),
            scores_data.get('algorithm_version', 'v1.0'),
            scores_data.get('weights_version', 'v1.0')
        )

        self.adapter.execute_command(query, params)
        return True


class ArchetypeRepository:
    """職業原型儲存庫"""

    def __init__(self, adapter: DatabaseAdapter):
        self.adapter = adapter

    def find_archetype(self, archetype_id: str) -> Optional[Dict[str, Any]]:
        """查找職業原型"""
        query = """
            SELECT archetype_id, archetype_name, archetype_name_en,
                   description, mbti_correlates, core_characteristics
            FROM career_archetypes
            WHERE archetype_id = ?
        """
        results = self.adapter.execute_query(query, (archetype_id,))
        if results:
            result = results[0]
            # 解析 JSON 欄位
            result['mbti_correlates'] = json.loads(result['mbti_correlates']) if result['mbti_correlates'] else []
            result['core_characteristics'] = json.loads(result['core_characteristics']) if result['core_characteristics'] else []
            return result
        return None

    def find_user_archetype_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """查找用戶原型分析結果"""
        query = """
            SELECT session_id, primary_archetype_id, secondary_archetype_id,
                   archetype_scores, dominant_talents, confidence_score
            FROM user_archetype_results
            WHERE session_id = ?
        """
        results = self.adapter.execute_query(query, (session_id,))
        if results:
            result = results[0]
            # 解析 JSON 欄位
            json_fields = ['archetype_scores', 'dominant_talents']
            for field in json_fields:
                if result[field]:
                    result[field] = json.loads(result[field])
            return result
        return None

    def save_user_archetype_result(self, session_id: str, result_data: Dict[str, Any]) -> bool:
        """儲存用戶原型分析結果"""
        query = """
            INSERT OR REPLACE INTO user_archetype_results
            (session_id, primary_archetype_id, secondary_archetype_id,
             archetype_scores, dominant_talents, supporting_talents,
             lesser_talents, confidence_score, analysis_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            session_id,
            result_data['primary_archetype_id'],
            result_data.get('secondary_archetype_id'),
            json.dumps(result_data['archetype_scores']),
            json.dumps(result_data['dominant_talents']),
            json.dumps(result_data.get('supporting_talents', [])),
            json.dumps(result_data.get('lesser_talents', [])),
            result_data['confidence_score'],
            json.dumps(result_data.get('metadata', {}))
        )

        self.adapter.execute_command(query, params)
        return True


class UnifiedDataAccess:
    """統一資料存取層"""

    def __init__(self, use_sqlite: bool = True):
        """
        初始化統一資料存取層

        Args:
            use_sqlite: 是否使用 SQLite (True) 或 SQLAlchemy (False)
        """
        if use_sqlite:
            from core.config import get_settings
            settings = get_settings()
            db_path = settings.database_url.replace("sqlite:///", "")
            self.adapter = SQLiteAdapter(db_path)
        else:
            self.adapter = SQLAlchemyAdapter()

        # 初始化儲存庫
        self.sessions = AssessmentSessionRepository(self.adapter)
        self.scores = ScoreRepository(self.adapter)
        self.archetypes = ArchetypeRepository(self.adapter)

        logger.info(f"✅ 統一資料存取層初始化 ({'SQLite' if use_sqlite else 'SQLAlchemy'})")

    @contextmanager
    def transaction(self):
        """事務管理"""
        with self.adapter.get_connection() as conn:
            try:
                yield conn
                # SQLite 使用 autocommit，SQLAlchemy 在適配器中處理
                if hasattr(conn, 'commit'):
                    conn.commit()
            except Exception:
                if hasattr(conn, 'rollback'):
                    conn.rollback()
                raise

    def health_check(self) -> Dict[str, Any]:
        """資料庫健康檢查"""
        try:
            # 簡單查詢測試連接
            result = self.adapter.execute_query("SELECT 1 as test")
            return {
                "status": "healthy",
                "adapter_type": type(self.adapter).__name__,
                "connection_test": "passed"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "adapter_type": type(self.adapter).__name__,
                "error": str(e)
            }


# 全域實例
_unified_data_access: Optional[UnifiedDataAccess] = None


def get_unified_data_access() -> UnifiedDataAccess:
    """獲取統一資料存取實例"""
    global _unified_data_access
    if _unified_data_access is None:
        _unified_data_access = UnifiedDataAccess(use_sqlite=True)
    return _unified_data_access


# 便利函式
def get_session_repository() -> AssessmentSessionRepository:
    """獲取會話儲存庫"""
    return get_unified_data_access().sessions


def get_score_repository() -> ScoreRepository:
    """獲取分數儲存庫"""
    return get_unified_data_access().scores


def get_archetype_repository() -> ArchetypeRepository:
    """獲取原型儲存庫"""
    return get_unified_data_access().archetypes