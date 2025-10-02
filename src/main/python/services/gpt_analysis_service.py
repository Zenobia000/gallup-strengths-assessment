"""
GPT-5 深度分析服務
使用 OpenAI GPT-5 thinking model 對才幹評測結果進行深度分析
生成個人化、結構化的才幹摘要報告
"""

import openai
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PersonalizedSummary:
    """個人化摘要結果"""
    session_id: str
    primary_strengths: List[str]
    unique_combination: str
    contextual_excellence: str
    development_insights: str
    actionable_recommendations: List[str]
    leadership_style: str
    collaboration_approach: str
    growth_trajectory: str
    confidence_score: float
    generated_at: datetime

class GPTAnalysisService:
    """
    GPT-5 深度分析服務

    基於科學才幹分類結果，使用 GPT-5 thinking model 進行：
    1. 才幹組合深度分析
    2. 個人化優勢摘要
    3. 情境化表現預測
    4. 發展建議生成
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 GPT 分析服務

        Args:
            api_key: OpenAI API key，若未提供則從環境變數讀取
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)

    def analyze_talent_profile(self,
                             talent_classification: Dict,
                             norm_scores: Dict,
                             career_prototype: Dict,
                             session_id: str) -> PersonalizedSummary:
        """
        對完整才幹概況進行 GPT-5 深度分析

        Args:
            talent_classification: 科學分類結果
            norm_scores: 常模分數
            career_prototype: 職涯原型
            session_id: 會話ID

        Returns:
            個人化深度分析摘要
        """
        try:
            # 準備結構化輸入數據
            analysis_input = self._prepare_analysis_input(
                talent_classification, norm_scores, career_prototype
            )

            # 生成深度分析提示詞
            prompt = self._create_analysis_prompt(analysis_input)

            # 調用 GPT-5 thinking model
            response = self._call_gpt5_thinking_model(prompt)

            # 解析並結構化回應
            summary = self._parse_gpt_response(response, session_id)

            logger.info(f"GPT-5 analysis completed for session {session_id}")
            return summary

        except Exception as e:
            logger.error(f"GPT analysis failed for session {session_id}: {e}")
            # 返回備用摘要
            return self._create_fallback_summary(talent_classification, session_id)

    def _prepare_analysis_input(self,
                               talent_classification: Dict,
                               norm_scores: Dict,
                               career_prototype: Dict) -> Dict:
        """準備結構化的分析輸入數據"""

        classified_talents = talent_classification.get('classified_talents', {})
        summary = talent_classification.get('classification_summary', {})

        # 提取主導才幹詳細資訊
        dominant_talents = []
        for talent in classified_talents.get('dominant', []):
            talent_detail = {
                'dimension': talent['dimension'],
                'percentile': talent['percentile'],
                'stanine': talent['stanine'],
                'confidence': talent['confidence'],
                'interpretation': talent['interpretation']
            }
            dominant_talents.append(talent_detail)

        # 提取支援才幹
        supporting_talents = []
        for talent in classified_talents.get('supporting', []):
            supporting_talents.append({
                'dimension': talent['dimension'],
                'percentile': talent['percentile'],
                'stanine': talent['stanine']
            })

        # 提取發展才幹
        developing_talents = []
        for talent in classified_talents.get('developing', []):
            developing_talents.append({
                'dimension': talent['dimension'],
                'percentile': talent['percentile'],
                'stanine': talent['stanine']
            })

        return {
            'profile_type': summary.get('profile_type', ''),
            'dominant_talents': dominant_talents,
            'supporting_talents': supporting_talents,
            'developing_talents': developing_talents,
            'total_talents': summary.get('total_talents', 12),
            'career_prototype': {
                'name': career_prototype.get('prototype_name', ''),
                'hint': career_prototype.get('prototype_hint', ''),
                'suggested_roles': career_prototype.get('suggested_roles', []),
                'key_contexts': career_prototype.get('key_contexts', []),
                'blind_spots': career_prototype.get('blind_spots', [])
            },
            'recommendations': summary.get('recommendations', [])
        }

    def _create_analysis_prompt(self, analysis_input: Dict) -> str:
        """創建 GPT-5 thinking model 分析提示詞"""

        prompt = f"""
你是一位具有20年經驗的才幹發展專家和心理學家，專精於個人優勢分析。請對以下才幹評測結果進行深度分析，生成個人化的洞察報告。

## 評測結果數據

**概況類型**: {analysis_input['profile_type']}

**主導才幹** (Stanine 8-9，前11%):
{self._format_talents_for_prompt(analysis_input['dominant_talents'])}

**支援才幹** (Stanine 5-7，中段範圍):
{self._format_talents_for_prompt(analysis_input['supporting_talents'])}

**發展才幹** (Stanine 1-4，後40%):
{self._format_talents_for_prompt(analysis_input['developing_talents'])}

**職涯原型**: {analysis_input['career_prototype']['name']}
- 提示: {analysis_input['career_prototype']['hint']}
- 建議角色: {', '.join(analysis_input['career_prototype']['suggested_roles'])}
- 關鍵情境: {', '.join(analysis_input['career_prototype']['key_contexts'])}

## 分析要求

請進行以下深度分析，並以JSON格式回應：

1. **才幹組合分析**: 分析主導才幹之間的獨特組合效應
2. **情境化優勢**: 描述在什麼具體情境下能發揮卓越表現
3. **發展洞察**: 基於科學分類結果的發展建議
4. **行動建議**: 3-5個具體可執行的建議
5. **領導風格**: 基於才幹組合預測的領導方式
6. **協作方式**: 在團隊中的最佳定位和貢獻方式
7. **成長軌跡**: 未來發展的可能路徑

## 回應格式要求

請嚴格按照以下JSON格式回應：

```json
{{
    "unique_combination": "描述主導才幹的獨特組合特色（80-120字）",
    "contextual_excellence": "具體描述在哪些情境下能發揮卓越表現（100-150字）",
    "development_insights": "基於分類結果的深度發展洞察（120-180字）",
    "actionable_recommendations": [
        "具體建議1（30-50字）",
        "具體建議2（30-50字）",
        "具體建議3（30-50字）",
        "具體建議4（30-50字）"
    ],
    "leadership_style": "預測的領導風格描述（80-120字）",
    "collaboration_approach": "團隊協作的最佳方式（80-120字）",
    "growth_trajectory": "未來成長路徑建議（100-150字）",
    "confidence_score": 0.85
}}
```

請確保：
- 分析基於科學的Stanine分類結果
- 內容具體、可執行，避免空泛描述
- 體現個人化特色，不使用通用模板
- 語言專業但易懂，適合受評者閱讀
"""
        return prompt

    def _format_talents_for_prompt(self, talents: List[Dict]) -> str:
        """格式化才幹列表供提示詞使用"""
        if not talents:
            return "無"

        formatted = []
        for talent in talents:
            formatted.append(f"- {talent['dimension']} (PR: {talent['percentile']:.1f}%)")

        return '\n'.join(formatted)

    def _call_gpt5_thinking_model(self, prompt: str) -> str:
        """調用 GPT-5 thinking model"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # 使用最新可用模型，將來升級為 gpt-5
                messages=[
                    {
                        "role": "system",
                        "content": "你是專業的才幹發展專家，擅長深度分析個人優勢並提供具體建議。請嚴格按照要求的JSON格式回應，確保分析準確、深入且個人化。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"GPT API call failed: {e}")
            raise

    def _parse_gpt_response(self, response: str, session_id: str) -> PersonalizedSummary:
        """解析 GPT 回應並創建 PersonalizedSummary"""
        try:
            parsed = json.loads(response)

            return PersonalizedSummary(
                session_id=session_id,
                primary_strengths=self._extract_primary_strengths(parsed),
                unique_combination=parsed.get('unique_combination', ''),
                contextual_excellence=parsed.get('contextual_excellence', ''),
                development_insights=parsed.get('development_insights', ''),
                actionable_recommendations=parsed.get('actionable_recommendations', []),
                leadership_style=parsed.get('leadership_style', ''),
                collaboration_approach=parsed.get('collaboration_approach', ''),
                growth_trajectory=parsed.get('growth_trajectory', ''),
                confidence_score=parsed.get('confidence_score', 0.8),
                generated_at=datetime.utcnow()
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response: {e}")
            raise ValueError("GPT response is not valid JSON")

    def _extract_primary_strengths(self, parsed: Dict) -> List[str]:
        """從解析結果中提取主要優勢"""
        # 從 unique_combination 和 contextual_excellence 中提取關鍵優勢
        combination = parsed.get('unique_combination', '')
        excellence = parsed.get('contextual_excellence', '')

        # 簡單提取（可以進一步改進）
        strengths = []
        if '分析' in combination or '分析' in excellence:
            strengths.append('深度分析')
        if '執行' in combination or '執行' in excellence:
            strengths.append('高效執行')
        if '責任' in combination or '當責' in excellence:
            strengths.append('責任承擔')

        return strengths[:3]  # 最多3個主要優勢

    def _create_fallback_summary(self,
                                talent_classification: Dict,
                                session_id: str) -> PersonalizedSummary:
        """創建備用摘要（當 GPT 調用失敗時）"""
        classified = talent_classification.get('classified_talents', {})
        dominant = classified.get('dominant', [])

        # 提取主導才幹名稱
        dominant_names = [t['dimension'] for t in dominant[:2]]

        return PersonalizedSummary(
            session_id=session_id,
            primary_strengths=dominant_names,
            unique_combination=f"您的主導天賦聚焦於『{', '.join(dominant_names)}』，展現出獨特的優勢組合。",
            contextual_excellence="這種組合讓您在特定情境下能發揮卓越表現。",
            development_insights="建議持續強化主導才幹，同時關注支援才幹的發展。",
            actionable_recommendations=[
                "發揮主導才幹優勢",
                "建立個人品牌",
                "尋找匹配的工作環境",
                "培養團隊協作能力"
            ],
            leadership_style="基於分析和執行的領導風格",
            collaboration_approach="以專業能力為基礎的協作方式",
            growth_trajectory="朝向專業專家或管理領導方向發展",
            confidence_score=0.75,
            generated_at=datetime.utcnow()
        )

    def save_analysis_result(self,
                           summary: PersonalizedSummary,
                           db_manager) -> bool:
        """保存分析結果到資料庫"""
        try:
            with db_manager.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO gpt_analysis_results
                    (session_id, unique_combination, contextual_excellence,
                     development_insights, actionable_recommendations,
                     leadership_style, collaboration_approach, growth_trajectory,
                     confidence_score, generated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    summary.session_id,
                    summary.unique_combination,
                    summary.contextual_excellence,
                    summary.development_insights,
                    json.dumps(summary.actionable_recommendations, ensure_ascii=False),
                    summary.leadership_style,
                    summary.collaboration_approach,
                    summary.growth_trajectory,
                    summary.confidence_score,
                    summary.generated_at.isoformat()
                ))
                conn.commit()

            logger.info(f"GPT analysis saved for session {summary.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save GPT analysis: {e}")
            return False

def get_gpt_analysis_service() -> GPTAnalysisService:
    """獲取 GPT 分析服務實例"""
    return GPTAnalysisService()