#!/usr/bin/env python3
"""
測試 report-detail.html 的資料串接邏輯
"""

import requests
import json

def test_report_detail_data():
    """測試團隊角色報告的資料載入"""

    # 測試所有 UAT session
    test_sessions = [
        ("v4_feda08de8341", "EXECUTING"),
        ("v4_750be3ac07bd", "STRATEGIC_THINKING"),
        ("v4_58ad1d92d898", "INFLUENCING"),
        ("v4_61068e55c9d3", "RELATIONSHIP_BUILDING")
    ]

    print("=" * 80)
    print("團隊角色與協作潛力報告 - 資料串接測試")
    print("=" * 80)

    for session_id, expected_domain in test_sessions:
        print(f"\n測試 Session: {session_id} (預期主導領域: {expected_domain})")
        print("-" * 80)

        try:
            # 呼叫 API
            response = requests.get(f"http://localhost:8005/api/assessment/results/{session_id}")
            response.raise_for_status()
            data = response.json()

            scores = data.get("scores", {})

            # 模擬前端邏輯：解析才幹分數
            talent_scores = []
            for key, score in scores.items():
                if key.startswith('t') and '_' in key:
                    talent_id = key.split('_')[0].upper().replace('T', 'T')
                    talent_scores.append({
                        "id": talent_id,
                        "key": key,
                        "score": score
                    })

            # 排序
            talent_scores.sort(key=lambda x: x["score"], reverse=True)

            # 顯示 Top 6
            print(f"\nTop 6 才幹 (用於原型計算):")
            for i, talent in enumerate(talent_scores[:6], 1):
                print(f"  {i}. {talent['id']} - {talent['key']}: {talent['score']:.1f}")

            # 計算領域分布
            domain_map = {
                't1': 'EXECUTING', 't2': 'EXECUTING', 't12': 'EXECUTING',
                't3': 'STRATEGIC_THINKING', 't4': 'STRATEGIC_THINKING', 't8': 'STRATEGIC_THINKING',
                't5': 'INFLUENCING', 't7': 'INFLUENCING', 't11': 'INFLUENCING',
                't6': 'RELATIONSHIP_BUILDING', 't9': 'RELATIONSHIP_BUILDING', 't10': 'RELATIONSHIP_BUILDING'
            }

            domain_totals = {'EXECUTING': 0, 'STRATEGIC_THINKING': 0, 'INFLUENCING': 0, 'RELATIONSHIP_BUILDING': 0}
            domain_counts = {'EXECUTING': 0, 'STRATEGIC_THINKING': 0, 'INFLUENCING': 0, 'RELATIONSHIP_BUILDING': 0}

            for talent in talent_scores:
                talent_key = talent['key'].split('_')[0]
                domain = domain_map.get(talent_key)
                if domain:
                    domain_totals[domain] += talent['score']
                    domain_counts[domain] += 1

            print(f"\n四大領域貢獻度:")
            for domain in ['EXECUTING', 'STRATEGIC_THINKING', 'INFLUENCING', 'RELATIONSHIP_BUILDING']:
                avg = domain_totals[domain] / domain_counts[domain] if domain_counts[domain] > 0 else 0
                print(f"  {domain}: {avg:.1f} (平均)")

            # 模擬原型計算
            archetype_scores = {
                'ARCHITECT': 0,    # 主導: T4, T1 / 輔助: T3, T8, T12
                'GUARDIAN': 0,     # 主導: T12, T9 / 輔助: T2, T1, T6
                'IDEALIST': 0,     # 主導: T6, T8 / 輔助: T5, T11, T7
                'ARTISAN': 0       # 主導: T5, T10 / 輔助: T3, T7, T11
            }

            top6_ids = [t['id'] for t in talent_scores[:6]]
            top4_ids = [t['id'] for t in talent_scores[:4]]

            # ARCHITECT
            if 'T4' in top4_ids: archetype_scores['ARCHITECT'] += 2
            if 'T1' in top4_ids: archetype_scores['ARCHITECT'] += 2
            for tid in ['T3', 'T8', 'T12']:
                if tid in top6_ids: archetype_scores['ARCHITECT'] += 1

            # GUARDIAN
            if 'T12' in top4_ids: archetype_scores['GUARDIAN'] += 2
            if 'T9' in top4_ids: archetype_scores['GUARDIAN'] += 2
            for tid in ['T2', 'T1', 'T6']:
                if tid in top6_ids: archetype_scores['GUARDIAN'] += 1

            # IDEALIST
            if 'T6' in top4_ids: archetype_scores['IDEALIST'] += 2
            if 'T8' in top4_ids: archetype_scores['IDEALIST'] += 2
            for tid in ['T5', 'T11', 'T7']:
                if tid in top6_ids: archetype_scores['IDEALIST'] += 1

            # ARTISAN
            if 'T5' in top4_ids: archetype_scores['ARTISAN'] += 2
            if 'T10' in top4_ids: archetype_scores['ARTISAN'] += 2
            for tid in ['T3', 'T7', 'T11']:
                if tid in top6_ids: archetype_scores['ARTISAN'] += 1

            print(f"\n團隊原型分數:")
            sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
            for archetype, score in sorted_archetypes:
                print(f"  {archetype}: {score} 分")

            primary_archetype = sorted_archetypes[0][0]
            archetype_names = {
                'ARCHITECT': '系統建構者 (理性者)',
                'GUARDIAN': '組織守護者 (守護者)',
                'IDEALIST': '人文關懷家 (理想主義者)',
                'ARTISAN': '推廣實踐家 (工匠)'
            }

            print(f"\n✅ 主要原型: {archetype_names[primary_archetype]}")
            print(f"   預期領域: {expected_domain}")

        except Exception as e:
            print(f"❌ 錯誤: {e}")

    print("\n" + "=" * 80)
    print("測試完成！請在瀏覽器中開啟以下 URL 驗證視覺化效果：")
    print("=" * 80)
    for session_id, domain in test_sessions:
        print(f"  {domain}: http://localhost:8005/static/report-detail.html?session={session_id}")

if __name__ == "__main__":
    test_report_detail_data()
