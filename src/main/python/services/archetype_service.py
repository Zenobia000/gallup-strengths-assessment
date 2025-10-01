"""
Career Archetype Service Layer

提供職業原型分析和職位推薦的核心服務，整合：
- 現有的 archetype_mapper.py 邏輯
- 資料庫持久化存儲
- 職位匹配算法
- 結果快取機制

遵循 Linus 原則：簡潔、實用、不過度設計
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import logging

from utils.database import get_database_manager, DatabaseError
from core.analysis.archetype_mapper import ArchetypeMapper, TalentProfile
from core.recommendation.career_matcher import CareerMatcher
from models.schemas import (
    CareerArchetype, CareerArchetypeBase, UserArchetypeResult, JobRecommendation,
    ArchetypeAnalysisRequest, ArchetypeAnalysisResponse,
    CareerPrototypeInfo
)

logger = logging.getLogger(__name__)


class ArchetypeService:
    """職業原型服務層 - 整合分析與持久化存儲"""

    def __init__(self):
        self.db_manager = get_database_manager()
        self.archetype_mapper = ArchetypeMapper()
        self.career_matcher = CareerMatcher()

    def analyze_user_archetype(self, session_id: str, talent_scores: Dict[str, float],
                             user_context: Optional[Dict[str, Any]] = None) -> UserArchetypeResult:
        """
        分析用戶職業原型

        Args:
            session_id: 評測會話識別碼
            talent_scores: T1-T12 才幹分數字典
            user_context: 用戶背景資訊（經驗、產業偏好等）

        Returns:
            UserArchetypeResult: 完整的原型分析結果
        """
        try:
            # 1. 使用現有的 archetype_mapper 進行分類
            talent_profile = self.archetype_mapper.classify_talents(talent_scores)
            primary_archetype = self.archetype_mapper.map_to_archetype(talent_profile)

            # 2. 計算所有4種原型的分數
            archetype_scores = self._calculate_all_archetype_scores(talent_profile)

            # 3. 獲取次要原型
            secondary_archetype = self._get_secondary_archetype(archetype_scores, primary_archetype.archetype_id)

            # 4. 計算信心分數
            confidence_score = self._calculate_confidence_score(talent_profile, archetype_scores)

            # 5. 從資料庫獲取完整原型資訊
            primary_archetype_data = self._get_archetype_from_db(primary_archetype.archetype_id)
            secondary_archetype_data = None
            if secondary_archetype:
                secondary_archetype_data = self._get_archetype_from_db(secondary_archetype)

            # 6. 格式化才幹資料
            dominant_talents = self._format_talents(talent_profile.dominant_talents)
            supporting_talents = self._format_talents(talent_profile.supporting_talents)
            lesser_talents = self._format_talents(talent_profile.lesser_talents)

            # 7. 建立結果物件
            result = UserArchetypeResult(
                session_id=session_id,
                primary_archetype=primary_archetype_data,
                secondary_archetype=secondary_archetype_data,
                archetype_scores=archetype_scores,
                dominant_talents=dominant_talents,
                supporting_talents=supporting_talents,
                lesser_talents=lesser_talents,
                confidence_score=confidence_score
            )

            # 8. 存儲到資料庫
            self._save_archetype_result(result)

            return result

        except Exception as e:
            logger.error(f"Failed to analyze user archetype for session {session_id}: {e}")
            raise

    def generate_job_recommendations(self, session_id: str, user_context: Optional[Dict[str, Any]] = None) -> List[JobRecommendation]:
        """
        生成職位推薦

        Args:
            session_id: 評測會話識別碼
            user_context: 用戶背景資訊

        Returns:
            List[JobRecommendation]: 職位推薦列表
        """
        try:
            # 1. 從資料庫獲取用戶原型結果
            archetype_result = self._get_archetype_result(session_id)
            if not archetype_result:
                raise ValueError(f"No archetype result found for session {session_id}")

            # 2. 重建才幹檔案用於職位匹配
            strength_profile = self._rebuild_strength_profile(archetype_result)

            # 3. 使用 career_matcher 進行職位匹配
            career_matches = self.career_matcher.find_career_matches(strength_profile, user_context or {})

            # 4. 轉換為 JobRecommendation 格式並分類
            recommendations = []
            for i, match in enumerate(career_matches[:10]):  # 取前10個推薦
                recommendation_type = self._determine_recommendation_type(match.match_score, i)

                rec = JobRecommendation(
                    job_role=self._format_job_role(match.job_role),
                    recommendation_type=recommendation_type,
                    match_score=match.match_score / 100.0,  # 轉換為0-1範圍
                    strength_alignment=match.strength_alignment,
                    development_gaps=match.development_needs,
                    recommendation_reasoning={"reasons": match.reasons},
                    priority_rank=i + 1,
                    confidence_level=match.confidence
                )
                recommendations.append(rec)

            # 5. 存儲推薦結果到資料庫
            self._save_job_recommendations(session_id, recommendations)

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate job recommendations for session {session_id}: {e}")
            raise

    def get_career_prototype_info(self, session_id: str) -> CareerPrototypeInfo:
        """
        獲取職業原型資訊用於前端顯示

        Args:
            session_id: 評測會話識別碼

        Returns:
            CareerPrototypeInfo: 職業原型資訊
        """
        try:
            # 從資料庫獲取原型結果
            archetype_result = self._get_archetype_result(session_id)
            if not archetype_result:
                raise ValueError(f"No archetype result found for session {session_id}")

            # 從資料庫獲取完整原型資訊
            archetype_data = self._get_archetype_from_db(archetype_result['primary_archetype_id'])

            # 獲取該原型的職位推薦
            job_recommendations = self._get_job_recommendations(session_id)
            suggested_roles = [rec['job_role']['role_name'] for rec in job_recommendations[:3]]

            # 建構前端所需的原型資訊
            prototype_info = CareerPrototypeInfo(
                prototype_name=archetype_data.archetype_name,
                prototype_hint=archetype_data.description,
                suggested_roles=suggested_roles or ["軟體架構師", "資料科學家", "解決方案架構師"],
                key_contexts=["策略規劃", "跨部門協作", "決策支援"],
                blind_spots=["避免過度分析", "設定決策截止點"],
                partnership_suggestions=["配對強『影響力/關係』夥伴共同推進"],
                mbti_correlation=f"可對應 {'/'.join(archetype_data.mbti_correlates[:2])} 原型"
            )

            return prototype_info

        except Exception as e:
            logger.error(f"Failed to get career prototype info for session {session_id}: {e}")
            # 返回預設值以避免前端錯誤
            return CareerPrototypeInfo(
                prototype_name="系統建構者",
                prototype_hint="把複雜轉為結構，可對應 INTJ/ISTJ 原型",
                suggested_roles=["產品經理", "資料科學家", "解決方案架構師"],
                key_contexts=["策略規劃", "跨部門協作", "決策支援"],
                blind_spots=["避免過度分析", "設定決策截止點"],
                partnership_suggestions=["配對強『影響力/關係』夥伴共同推進"],
                mbti_correlation="可對應 INTJ/ISTJ 原型"
            )

    def _calculate_all_archetype_scores(self, talent_profile: TalentProfile) -> Dict[str, float]:
        """計算所有4種原型的分數"""
        scores = {}

        # 獲取主導才幹ID列表
        dominant_talent_ids = [t[0] for t in talent_profile.dominant_talents]

        for archetype in self.archetype_mapper.archetypes:
            score = 0
            # 計算核心才幹匹配分數
            for talent in archetype.primary_talents:
                if talent in dominant_talent_ids:
                    score += 3

            # 計算輔助才幹匹配分數
            for talent in archetype.secondary_talents:
                if talent in dominant_talent_ids:
                    score += 1

            scores[archetype.archetype_id] = score

        return scores

    def _get_secondary_archetype(self, archetype_scores: Dict[str, float], primary_id: str) -> Optional[str]:
        """獲取次要原型"""
        sorted_scores = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)

        # 找第二高分的原型
        for archetype_id, score in sorted_scores:
            if archetype_id != primary_id and score > 0:
                return archetype_id

        return None

    def _calculate_confidence_score(self, talent_profile: TalentProfile, archetype_scores: Dict[str, float]) -> float:
        """計算信心分數"""
        max_score = max(archetype_scores.values())
        scores_list = list(archetype_scores.values())
        scores_list.sort(reverse=True)

        # 如果最高分明顯高於第二高分，信心度較高
        if len(scores_list) > 1:
            gap = scores_list[0] - scores_list[1]
            confidence = min(0.95, 0.7 + gap * 0.05)
        else:
            confidence = 0.8

        # 主導才幹數量影響信心度
        if len(talent_profile.dominant_talents) >= 3:
            confidence += 0.1

        return min(confidence, 1.0)

    def _get_archetype_from_db(self, archetype_id: str) -> Any:
        """從資料庫獲取原型資訊"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT archetype_id, archetype_name, archetype_name_en,
                       keirsey_temperament, mbti_correlates, description,
                       core_characteristics, work_environment_preferences,
                       leadership_style, decision_making_style, communication_style,
                       stress_indicators, development_areas
                FROM career_archetypes
                WHERE archetype_id = ?
            """, (archetype_id,))

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Archetype {archetype_id} not found in database")

            # 解析JSON欄位
            data = dict(row)
            json_fields = ['mbti_correlates', 'core_characteristics', 'work_environment_preferences',
                          'stress_indicators', 'development_areas']
            for field in json_fields:
                if data[field]:
                    data[field] = json.loads(data[field])

            # 返回符合 CareerArchetypeBase 的 Pydantic 模型
            return CareerArchetypeBase(
                archetype_id=data['archetype_id'],
                archetype_name=data['archetype_name'],
                archetype_name_en=data['archetype_name_en'],
                keirsey_temperament=data['keirsey_temperament'],
                description=data['description']
            )

    def _format_talents(self, talents: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
        """格式化才幹資料"""
        # T1-T12 才幹名稱映射
        talent_names = {
            'T1': '結構化執行', 'T2': '品質與完備', 'T3': '探索與創新',
            'T4': '分析與洞察', 'T5': '影響與倡議', 'T6': '協作與共好',
            'T7': '客戶導向', 'T8': '學習與成長', 'T9': '紀律與信任',
            'T10': '壓力調節', 'T11': '衝突整合', 'T12': '責任與當責'
        }

        return [
            {
                'dimension_id': talent_id,
                'dimension_name': talent_names.get(talent_id, talent_id),
                'score': score
            }
            for talent_id, score in talents
        ]

    def _save_archetype_result(self, result: UserArchetypeResult):
        """存儲原型分析結果到資料庫"""
        with self.db_manager.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_archetype_results
                (session_id, primary_archetype_id, secondary_archetype_id,
                 archetype_scores, dominant_talents, supporting_talents,
                 lesser_talents, confidence_score, analysis_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.session_id,
                result.primary_archetype.archetype_id,
                result.secondary_archetype.archetype_id if result.secondary_archetype else None,
                json.dumps(result.archetype_scores),
                json.dumps(result.dominant_talents),
                json.dumps(result.supporting_talents),
                json.dumps(result.lesser_talents),
                result.confidence_score,
                json.dumps({'generated_at': datetime.utcnow().isoformat()})
            ))

    def _get_archetype_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """從資料庫獲取原型結果"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT primary_archetype_id, secondary_archetype_id,
                       archetype_scores, dominant_talents, supporting_talents,
                       lesser_talents, confidence_score
                FROM user_archetype_results
                WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if row:
                data = dict(row)
                # 解析JSON欄位
                json_fields = ['archetype_scores', 'dominant_talents', 'supporting_talents', 'lesser_talents']
                for field in json_fields:
                    if data[field]:
                        data[field] = json.loads(data[field])
                return data
            return None

    def _rebuild_strength_profile(self, archetype_result: Dict[str, Any]):
        """從原型結果重建 StrengthProfile 物件"""
        # 這裡需要建立一個簡化的 StrengthProfile 物件
        # 為了與 career_matcher 相容
        class SimpleStrengthProfile:
            def __init__(self, talents_data):
                self.all_strengths = []
                self.top_5_strengths = []
                self.profile_confidence = archetype_result.get('confidence_score', 0.8)

                # 轉換才幹資料
                for talent in talents_data.get('dominant_talents', []):
                    strength = type('StrengthScore', (), {
                        'name': talent['dimension_id'],
                        'score': talent['score'],
                        'theme': type('Theme', (), {'name': talent['dimension_name']})()
                    })()
                    self.all_strengths.append(strength)
                    if len(self.top_5_strengths) < 5:
                        self.top_5_strengths.append(strength)

        return SimpleStrengthProfile(archetype_result)

    def _format_job_role(self, career_role) -> Dict[str, Any]:
        """格式化職位角色資料"""
        return {
            'role_id': career_role.role_name.lower().replace(' ', '_'),
            'role_name': career_role.role_name,
            'role_name_en': career_role.role_name,
            'industry_sector': career_role.industry_sector.value,
            'job_family': 'General',
            'seniority_level': 'mid',
            'description': career_role.description,
            'key_responsibilities': [],
            'required_skills': career_role.primary_strengths,
            'preferred_skills': career_role.secondary_strengths
        }

    def _determine_recommendation_type(self, match_score: float, rank: int) -> str:
        """確定推薦類型"""
        if rank < 3 and match_score > 80:
            return "primary"
        elif match_score > 60:
            return "stretch"
        else:
            return "development"

    def _save_job_recommendations(self, session_id: str, recommendations: List[JobRecommendation]):
        """存儲職位推薦到資料庫"""
        with self.db_manager.get_connection() as conn:
            # 先刪除舊的推薦
            conn.execute("DELETE FROM job_recommendations WHERE session_id = ?", (session_id,))

            # 插入新的推薦
            for rec in recommendations:
                conn.execute("""
                    INSERT INTO job_recommendations
                    (session_id, role_id, recommendation_type, match_score,
                     strength_alignment, development_gaps, recommendation_reasoning,
                     priority_rank, confidence_level, is_featured)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    rec.job_role['role_id'],
                    rec.recommendation_type,
                    rec.match_score,
                    json.dumps(rec.strength_alignment),
                    json.dumps(rec.development_gaps),
                    json.dumps(rec.recommendation_reasoning),
                    rec.priority_rank,
                    rec.confidence_level,
                    rec.priority_rank <= 3  # 前3個設為featured
                ))

    def _get_job_recommendations(self, session_id: str) -> List[Dict[str, Any]]:
        """從資料庫獲取職位推薦"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT jr.*, jrole.role_name, jrole.description, jrole.industry_sector
                FROM job_recommendations jr
                LEFT JOIN job_roles jrole ON jr.role_id = jrole.role_id
                WHERE jr.session_id = ?
                ORDER BY jr.priority_rank
            """, (session_id,))

            recommendations = []
            for row in cursor.fetchall():
                data = dict(row)
                data['job_role'] = {
                    'role_id': data['role_id'],
                    'role_name': data['role_name'] or '職位名稱',
                    'description': data['description'] or '職位描述',
                    'industry_sector': data['industry_sector'] or 'Technology'
                }
                recommendations.append(data)

            return recommendations


def get_archetype_service() -> ArchetypeService:
    """獲取職業原型服務實例"""
    return ArchetypeService()