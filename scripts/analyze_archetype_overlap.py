#!/usr/bin/env python3
"""
分析四大才幹領域與職業原型的重疊情況
驗證：不同才幹領域是否會對應到相同的職業原型
"""

import requests
import json
from collections import defaultdict

# 才幹定義
TALENT_DEFINITIONS = {
    "T1": {"name": "結構化執行", "domain": "EXECUTING"},
    "T2": {"name": "品質與完備", "domain": "EXECUTING"},
    "T3": {"name": "探索與創新", "domain": "STRATEGIC_THINKING"},
    "T4": {"name": "分析與洞察", "domain": "STRATEGIC_THINKING"},
    "T5": {"name": "影響與倡議", "domain": "INFLUENCING"},
    "T6": {"name": "協作與共好", "domain": "RELATIONSHIP_BUILDING"},
    "T7": {"name": "客戶導向", "domain": "INFLUENCING"},
    "T8": {"name": "學習與成長", "domain": "STRATEGIC_THINKING"},
    "T9": {"name": "紀律與信任", "domain": "RELATIONSHIP_BUILDING"},
    "T10": {"name": "壓力調節", "domain": "RELATIONSHIP_BUILDING"},
    "T11": {"name": "衝突整合", "domain": "INFLUENCING"},
    "T12": {"name": "責任與當責", "domain": "EXECUTING"}
}

# 原型定義
ARCHETYPES = {
    "ARCHITECT": {
        "name": "系統建構者",
        "primary": ["T4", "T1"],
        "secondary": ["T3", "T8", "T12"]
    },
    "GUARDIAN": {
        "name": "組織守護者",
        "primary": ["T12", "T9"],
        "secondary": ["T2", "T1", "T6"]
    },
    "IDEALIST": {
        "name": "人文關懷家",
        "primary": ["T6", "T8"],
        "secondary": ["T5", "T11", "T7"]
    },
    "ARTISAN": {
        "name": "推廣實踐家",
        "primary": ["T5", "T10"],
        "secondary": ["T3", "T7", "T11"]
    }
}

def calculate_archetype(top6_talents):
    """計算原型分數"""
    top4_ids = [t['id'] for t in top6_talents[:4]]
    top6_ids = [t['id'] for t in top6_talents[:6]]

    archetype_scores = {}

    for archetype_key, archetype_def in ARCHETYPES.items():
        score = 0

        # 主導才幹計分
        for talent_id in archetype_def["primary"]:
            if talent_id in top4_ids:
                score += 2

        # 輔助才幹計分
        for talent_id in archetype_def["secondary"]:
            if talent_id in top6_ids:
                score += 1

        archetype_scores[archetype_key] = score

    # 返回最高分的原型
    primary_archetype = max(archetype_scores.items(), key=lambda x: x[1])
    return primary_archetype[0], archetype_scores

def get_primary_domain(talent_scores):
    """計算主導領域"""
    domain_totals = defaultdict(float)
    domain_counts = defaultdict(int)

    for talent in talent_scores:
        domain = TALENT_DEFINITIONS[talent['id']]['domain']
        domain_totals[domain] += talent['score']
        domain_counts[domain] += 1

    # 計算平均分
    domain_averages = {
        domain: domain_totals[domain] / domain_counts[domain]
        for domain in domain_totals
    }

    primary_domain = max(domain_averages.items(), key=lambda x: x[1])
    return primary_domain[0], domain_averages

def analyze_session(session_id):
    """分析單一 session"""
    try:
        response = requests.get(f"http://localhost:8005/api/assessment/results/{session_id}")
        response.raise_for_status()
        data = response.json()

        scores = data.get("scores", {})

        # 解析才幹分數
        talent_scores = []
        for key, score in scores.items():
            if key.startswith('t') and '_' in key:
                talent_num = key.split('_')[0][1:]  # 't1' -> '1'
                talent_id = f"T{talent_num}"
                if talent_id in TALENT_DEFINITIONS:
                    talent_scores.append({
                        "id": talent_id,
                        "name": TALENT_DEFINITIONS[talent_id]['name'],
                        "domain": TALENT_DEFINITIONS[talent_id]['domain'],
                        "score": score
                    })

        talent_scores.sort(key=lambda x: x['score'], reverse=True)

        # 計算主導領域
        primary_domain, domain_averages = get_primary_domain(talent_scores)

        # 計算原型
        primary_archetype, archetype_scores = calculate_archetype(talent_scores[:6])

        return {
            "session_id": session_id,
            "top6_talents": talent_scores[:6],
            "primary_domain": primary_domain,
            "domain_averages": domain_averages,
            "primary_archetype": primary_archetype,
            "archetype_scores": archetype_scores,
            "archetype_name": ARCHETYPES[primary_archetype]['name']
        }

    except Exception as e:
        print(f"❌ Error analyzing {session_id}: {e}")
        return None

def main():
    """主程式"""

    # 測試所有 UAT session
    test_sessions = [
        ("v4_feda08de8341", "EXECUTING"),
        ("v4_750be3ac07bd", "STRATEGIC_THINKING"),
        ("v4_58ad1d92d898", "INFLUENCING"),
        ("v4_61068e55c9d3", "RELATIONSHIP_BUILDING")
    ]

    print("=" * 100)
    print("四大才幹領域與職業原型匹配分析")
    print("=" * 100)
    print()

    results = []

    for session_id, expected_domain in test_sessions:
        result = analyze_session(session_id)
        if result:
            results.append(result)

    # 建立 領域 -> 原型 的映射
    domain_to_archetype = defaultdict(list)
    archetype_to_domain = defaultdict(list)

    for result in results:
        domain = result['primary_domain']
        archetype = result['primary_archetype']

        domain_to_archetype[domain].append({
            "archetype": archetype,
            "archetype_name": result['archetype_name'],
            "session": result['session_id'],
            "top3_talents": [t['name'] for t in result['top6_talents'][:3]]
        })

        archetype_to_domain[archetype].append({
            "domain": domain,
            "session": result['session_id'],
            "domain_scores": result['domain_averages']
        })

    # 顯示詳細結果
    print("📊 各領域對應的原型分布")
    print("-" * 100)

    for domain in ["EXECUTING", "STRATEGIC_THINKING", "INFLUENCING", "RELATIONSHIP_BUILDING"]:
        print(f"\n🎯 {domain} 領域:")

        if domain in domain_to_archetype:
            for item in domain_to_archetype[domain]:
                print(f"   → {item['archetype_name']} ({item['archetype']})")
                print(f"      Top 3 才幹: {', '.join(item['top3_talents'])}")
                print(f"      Session: {item['session']}")
        else:
            print("   ⚠️  沒有測試數據")

    print("\n" + "=" * 100)
    print("📊 各原型對應的領域分布")
    print("-" * 100)

    for archetype_key in ["ARCHITECT", "GUARDIAN", "IDEALIST", "ARTISAN"]:
        archetype_name = ARCHETYPES[archetype_key]['name']
        print(f"\n🎭 {archetype_name} ({archetype_key}):")

        if archetype_key in archetype_to_domain:
            for item in archetype_to_domain[archetype_key]:
                print(f"   → 來自 {item['domain']} 領域")
                print(f"      領域分數: {', '.join([f'{k}: {v:.1f}' for k, v in sorted(item['domain_scores'].items(), key=lambda x: x[1], reverse=True)][:3])}")
                print(f"      Session: {item['session']}")
        else:
            print("   ⚠️  沒有測試數據")

    # 重疊分析
    print("\n" + "=" * 100)
    print("🔍 重疊分析：同一原型是否來自不同領域？")
    print("-" * 100)

    overlap_found = False

    for archetype_key, instances in archetype_to_domain.items():
        domains = [item['domain'] for item in instances]
        unique_domains = set(domains)

        if len(unique_domains) > 1:
            overlap_found = True
            archetype_name = ARCHETYPES[archetype_key]['name']
            print(f"\n✅ 發現重疊！{archetype_name} ({archetype_key}) 來自多個領域:")

            for domain in unique_domains:
                domain_instances = [item for item in instances if item['domain'] == domain]
                print(f"   - {domain}: {len(domain_instances)} 個案例")

                for instance in domain_instances:
                    print(f"     • Session: {instance['session']}")
                    top3_scores = sorted(instance['domain_scores'].items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"       領域排名: {' > '.join([f'{k}({v:.1f})' for k, v in top3_scores])}")

    if not overlap_found:
        print("\n⚠️  當前測試數據中未發現重疊（可能需要更多測試案例）")

    # 總結
    print("\n" + "=" * 100)
    print("📝 總結")
    print("-" * 100)

    print(f"\n測試案例總數: {len(results)}")
    print(f"涵蓋領域: {len(domain_to_archetype)}/4")
    print(f"出現的原型: {len(archetype_to_domain)}/4")

    print("\n關鍵發現:")
    print("1. 四大才幹領域對應的原型分布:")
    for domain in domain_to_archetype:
        archetypes = set([item['archetype'] for item in domain_to_archetype[domain]])
        print(f"   - {domain}: {', '.join([ARCHETYPES[a]['name'] for a in archetypes])}")

    print("\n2. 每個原型可能來自的領域:")
    for archetype in archetype_to_domain:
        domains = set([item['domain'] for item in archetype_to_domain[archetype]])
        print(f"   - {ARCHETYPES[archetype]['name']}: {', '.join(domains)}")

    print("\n3. 是否存在「不同領域對應同一原型」的情況？")
    if overlap_found:
        print("   ✅ 是！確認存在重疊情況")
    else:
        print("   ⚠️  當前測試數據不足以確認")

    print("\n" + "=" * 100)

if __name__ == "__main__":
    main()
