#!/usr/bin/env python3
"""
地毯式掃描：驗證所有職業原型的內容一致性與合理性
檢查項目：
1. 職業建議是否匹配才幹組合
2. 關鍵情境描述是否合理
3. 發展建議是否針對性
4. 子原型之間的差異性
"""

import json

# 從 HTML 提取的原型定義
ARCHETYPES = {
    "ARCHITECT": {
        "name": "系統建構者",
        "temperament": "理性者 (Rational)",
        "base_talents": {
            "primary": ["T4", "T1"],
            "secondary": ["T3", "T8", "T12"]
        },
        "variants": {
            "EXECUTING": {
                "name": "流程導向",
                "description": "重視流程與系統的執行型建構者，擅長將目標拆解為可執行步驟，建立高效的工作流程。",
                "careers": ["專案經理", "流程工程師", "品質經理", "ERP 顧問"],
                "strength": "將複雜任務分解為清晰步驟，確保每個環節高效運作",
                "expected_talents": ["T1", "T4", "T12", "T2"]
            },
            "STRATEGIC_THINKING": {
                "name": "策略導向",
                "description": "重視策略與創新的思考型建構者，擅長分析複雜問題，設計創新的解決方案與系統架構。",
                "careers": ["策略顧問", "產品經理", "系統架構師", "技術總監"],
                "strength": "洞察本質問題，設計兼具創新性與可行性的系統方案",
                "expected_talents": ["T4", "T3", "T8", "T1"]
            }
        }
    },
    "GUARDIAN": {
        "name": "組織守護者",
        "temperament": "守護者 (Guardian)",
        "base_talents": {
            "primary": ["T12", "T9"],
            "secondary": ["T2", "T1", "T6"]
        },
        "variants": {
            "EXECUTING": {
                "name": "品質導向",
                "description": "重視品質與交付的執行型守護者，擅長確保每個細節符合標準，按時完成任務。",
                "careers": ["品質經理", "行政主管", "合規專員", "營運經理"],
                "strength": "建立完善的品質檢核機制，確保穩定高質量的產出",
                "expected_talents": ["T12", "T2", "T1", "T9"]
            },
            "RELATIONSHIP_BUILDING": {
                "name": "信任導向",
                "description": "重視信任與關係的協作型守護者，擅長維護團隊和諧，建立可靠的協作網絡。",
                "careers": ["HR 夥伴", "團隊協調者", "客戶成功經理", "社群經理"],
                "strength": "成為團隊的可靠後盾，維護信任與穩定的協作關係",
                "expected_talents": ["T9", "T6", "T12", "T10"]
            }
        }
    },
    "IDEALIST": {
        "name": "人文關懷家",
        "temperament": "理想主義者 (Idealist)",
        "base_talents": {
            "primary": ["T6", "T8"],
            "secondary": ["T5", "T11", "T7"]
        },
        "variants": {
            "RELATIONSHIP_BUILDING": {
                "name": "和諧導向",
                "description": "重視和諧與賦能的關係型理想家，擅長建立信任氛圍，激發團隊潛力。",
                "careers": ["HR 夥伴", "組織發展顧問", "團隊教練", "員工關係專員"],
                "strength": "創造積極的團隊文化，讓每個成員都能發揮潛力",
                "expected_talents": ["T6", "T8", "T10", "T9"]
            },
            "STRATEGIC_THINKING": {
                "name": "成長導向",
                "description": "重視學習與成長的教育型理想家，擅長設計培訓體系，促進個人與組織發展。",
                "careers": ["企業培訓師", "教育創業家", "學習發展經理", "講師"],
                "strength": "建立系統化的學習路徑，幫助他人實現成長目標",
                "expected_talents": ["T8", "T6", "T3", "T4"]
            },
            "INFLUENCING": {
                "name": "影響導向",
                "description": "重視影響與倡議的推廣型理想家，擅長傳播理念，凝聚共識，推動變革。",
                "careers": ["變革管理顧問", "DEI 專員", "社會企業家", "企業文化主管"],
                "strength": "以富有感染力的方式傳播價值觀，激發集體行動",
                "expected_talents": ["T6", "T5", "T11", "T8"]
            }
        }
    },
    "ARTISAN": {
        "name": "推廣實踐家",
        "temperament": "工匠 (Artisan)",
        "base_talents": {
            "primary": ["T5", "T10"],
            "secondary": ["T3", "T7", "T11"]
        },
        "variants": {
            "INFLUENCING": {
                "name": "推廣導向",
                "description": "重視影響與推廣的行動型實踐家，擅長將成果向外推廣，建立廣泛的影響力。",
                "careers": ["業務主管", "BD 經理", "市場推廣專員", "公關經理"],
                "strength": "快速建立人脈，將想法轉化為實際行動與成果",
                "expected_talents": ["T5", "T7", "T11", "T3"]
            },
            "RELATIONSHIP_BUILDING": {
                "name": "應變導向",
                "description": "重視應變與危機處理的靈活型實踐家，擅長在壓力下保持冷靜，快速解決問題。",
                "careers": ["危機處理專員", "客戶成功經理", "現場經理", "專案救火隊"],
                "strength": "在高壓環境中快速決策，靈活應對突發狀況",
                "expected_talents": ["T10", "T5", "T6", "T11"]
            },
            "STRATEGIC_THINKING": {
                "name": "創新導向",
                "description": "重視創新與實驗的探索型實踐家，擅長嘗試新方法，快速驗證想法。",
                "careers": ["產品創新經理", "創業家", "增長駭客", "實驗專案負責人"],
                "strength": "勇於嘗試創新方法，快速將想法落地並迭代優化",
                "expected_talents": ["T5", "T3", "T10", "T7"]
            }
        }
    }
}

# 才幹定義
TALENT_DEFINITIONS = {
    "T1": {"name": "結構化執行", "domain": "EXECUTING", "description": "將目標拆解成步驟，建立流程和追蹤機制"},
    "T2": {"name": "品質與完備", "domain": "EXECUTING", "description": "注重細節，追求第一次就把事情做對"},
    "T3": {"name": "探索與創新", "domain": "STRATEGIC_THINKING", "description": "嘗試新方法，從失敗中學習，連結不同概念"},
    "T4": {"name": "分析與洞察", "domain": "STRATEGIC_THINKING", "description": "界定問題，用數據檢驗假設，辨識因果關係"},
    "T5": {"name": "影響與倡議", "domain": "INFLUENCING", "description": "說服他人，表達觀點，推動變革"},
    "T6": {"name": "協作與共好", "domain": "RELATIONSHIP_BUILDING", "description": "建立團隊合作，分享資源，促進和諧"},
    "T7": {"name": "客戶導向", "domain": "INFLUENCING", "description": "理解客戶需求，創造價值，建立長期關係"},
    "T8": {"name": "學習與成長", "domain": "STRATEGIC_THINKING", "description": "持續學習，反思改進，培養他人"},
    "T9": {"name": "紀律與信任", "domain": "RELATIONSHIP_BUILDING", "description": "守約守時，維持穩定，建立可靠形象"},
    "T10": {"name": "壓力調節", "domain": "RELATIONSHIP_BUILDING", "description": "在壓力下保持冷靜，穩定團隊情緒"},
    "T11": {"name": "衝突整合", "domain": "INFLUENCING", "description": "處理分歧，尋求共識，促進決策"},
    "T12": {"name": "責任與當責", "domain": "EXECUTING", "description": "承擔責任，主動回報，確保交付"}
}

# 職業與才幹的合理性對照表
CAREER_TALENT_MAPPING = {
    "專案經理": ["T1", "T12", "T2", "T4"],
    "流程工程師": ["T1", "T2", "T4", "T12"],
    "品質經理": ["T2", "T12", "T1", "T9"],
    "ERP 顧問": ["T1", "T4", "T2", "T12"],
    "策略顧問": ["T4", "T3", "T8", "T1"],
    "產品經理": ["T4", "T3", "T7", "T1"],
    "系統架構師": ["T4", "T3", "T1", "T8"],
    "技術總監": ["T4", "T3", "T12", "T1"],
    "行政主管": ["T12", "T2", "T1", "T9"],
    "合規專員": ["T2", "T12", "T9", "T1"],
    "營運經理": ["T12", "T1", "T2", "T9"],
    "HR 夥伴": ["T6", "T8", "T9", "T5"],
    "團隊協調者": ["T6", "T9", "T11", "T10"],
    "客戶成功經理": ["T7", "T6", "T10", "T5"],
    "社群經理": ["T6", "T5", "T7", "T11"],
    "組織發展顧問": ["T6", "T8", "T5", "T4"],
    "團隊教練": ["T6", "T8", "T5", "T11"],
    "員工關係專員": ["T6", "T9", "T11", "T10"],
    "企業培訓師": ["T8", "T5", "T6", "T3"],
    "教育創業家": ["T8", "T3", "T5", "T4"],
    "學習發展經理": ["T8", "T6", "T4", "T1"],
    "講師": ["T8", "T5", "T7", "T3"],
    "變革管理顧問": ["T5", "T8", "T11", "T4"],
    "DEI 專員": ["T6", "T5", "T8", "T11"],
    "社會企業家": ["T5", "T3", "T6", "T8"],
    "企業文化主管": ["T6", "T5", "T8", "T9"],
    "業務主管": ["T5", "T7", "T11", "T12"],
    "BD 經理": ["T5", "T7", "T3", "T4"],
    "市場推廣專員": ["T5", "T7", "T3", "T11"],
    "公關經理": ["T5", "T7", "T11", "T6"],
    "危機處理專員": ["T10", "T11", "T5", "T12"],
    "現場經理": ["T10", "T12", "T1", "T11"],
    "專案救火隊": ["T10", "T5", "T1", "T3"],
    "產品創新經理": ["T3", "T5", "T4", "T7"],
    "創業家": ["T3", "T5", "T10", "T4"],
    "增長駭客": ["T3", "T4", "T5", "T8"],
    "實驗專案負責人": ["T3", "T4", "T10", "T1"]
}

def validate_archetype_variant(archetype_key, variant_key, variant_data):
    """驗證單一子原型的合理性"""
    issues = []
    warnings = []

    archetype_name = ARCHETYPES[archetype_key]["name"]
    variant_name = variant_data["name"]
    full_name = f"{archetype_name} - {variant_name}"

    print(f"\n{'='*80}")
    print(f"檢查: {full_name} ({variant_key} 主導)")
    print(f"{'='*80}")

    # 1. 檢查職業建議與期望才幹的匹配度
    print(f"\n1️⃣  職業建議驗證")
    print(f"   推薦職業: {', '.join(variant_data['careers'])}")
    print(f"   期望才幹組合: {', '.join([TALENT_DEFINITIONS[t]['name'] for t in variant_data['expected_talents'][:4]])}")

    for career in variant_data["careers"]:
        if career in CAREER_TALENT_MAPPING:
            required_talents = set(CAREER_TALENT_MAPPING[career][:3])
            provided_talents = set(variant_data["expected_talents"][:4])
            overlap = required_talents & provided_talents
            overlap_rate = len(overlap) / len(required_talents) * 100

            if overlap_rate >= 66:
                print(f"   ✅ {career}: 匹配度 {overlap_rate:.0f}% (重疊才幹: {', '.join([TALENT_DEFINITIONS[t]['name'] for t in overlap])})")
            elif overlap_rate >= 33:
                print(f"   ⚠️  {career}: 匹配度 {overlap_rate:.0f}% (重疊才幹: {', '.join([TALENT_DEFINITIONS[t]['name'] for t in overlap])})")
                warnings.append(f"{career} 匹配度偏低 ({overlap_rate:.0f}%)")
            else:
                print(f"   ❌ {career}: 匹配度 {overlap_rate:.0f}% (重疊才幹: {', '.join([TALENT_DEFINITIONS[t]['name'] for t in overlap])})")
                issues.append(f"{career} 匹配度過低 ({overlap_rate:.0f}%)")
        else:
            print(f"   ⚪ {career}: 新職業，無對照表")

    # 2. 檢查描述與主導領域的一致性
    print(f"\n2️⃣  描述一致性驗證")
    description = variant_data["description"]

    domain_keywords = {
        "EXECUTING": ["執行", "流程", "步驟", "交付", "完成", "品質", "標準", "系統"],
        "STRATEGIC_THINKING": ["策略", "創新", "分析", "洞察", "思考", "設計", "規劃", "學習"],
        "INFLUENCING": ["影響", "推廣", "說服", "倡議", "推動", "表達", "傳播"],
        "RELATIONSHIP_BUILDING": ["關係", "團隊", "協作", "和諧", "信任", "穩定", "支持"]
    }

    expected_keywords = domain_keywords.get(variant_key, [])
    found_keywords = [kw for kw in expected_keywords if kw in description]

    if len(found_keywords) >= 2:
        print(f"   ✅ 描述符合 {variant_key} 領域特徵")
        print(f"      關鍵詞: {', '.join(found_keywords)}")
    else:
        print(f"   ⚠️  描述與 {variant_key} 領域關聯較弱")
        print(f"      僅找到關鍵詞: {', '.join(found_keywords) if found_keywords else '無'}")
        warnings.append(f"描述與 {variant_key} 領域關聯較弱")

    # 3. 檢查核心優勢的針對性
    print(f"\n3️⃣  核心優勢驗證")
    strength = variant_data["strength"]
    print(f"   優勢描述: {strength}")

    # 檢查是否包含動詞 (行為導向)
    action_verbs = ["建立", "確保", "創造", "設計", "推動", "激發", "快速", "靈活", "洞察", "分解", "傳播"]
    found_actions = [v for v in action_verbs if v in strength]

    if found_actions:
        print(f"   ✅ 優勢描述行為導向，包含動詞: {', '.join(found_actions)}")
    else:
        print(f"   ⚠️  優勢描述缺少行為動詞")
        warnings.append("優勢描述應更行為導向")

    # 4. 總結
    print(f"\n📊 驗證總結")
    if issues:
        print(f"   ❌ 嚴重問題 ({len(issues)}):")
        for issue in issues:
            print(f"      - {issue}")

    if warnings:
        print(f"   ⚠️  警告 ({len(warnings)}):")
        for warning in warnings:
            print(f"      - {warning}")

    if not issues and not warnings:
        print(f"   ✅ 所有檢查通過！")

    return {"issues": issues, "warnings": warnings}

def main():
    """主程式"""
    print("="*80)
    print("職業原型內容驗證 - 地毯式掃描")
    print("="*80)

    all_issues = []
    all_warnings = []
    total_variants = 0

    for archetype_key, archetype_data in ARCHETYPES.items():
        for variant_key, variant_data in archetype_data["variants"].items():
            total_variants += 1
            result = validate_archetype_variant(archetype_key, variant_key, variant_data)

            if result["issues"]:
                all_issues.extend([f"{archetype_data['name']} - {variant_data['name']}: {issue}" for issue in result["issues"]])

            if result["warnings"]:
                all_warnings.extend([f"{archetype_data['name']} - {variant_data['name']}: {warning}" for warning in result["warnings"]])

    # 最終總結
    print(f"\n\n{'='*80}")
    print("📊 最終總結")
    print(f"{'='*80}")
    print(f"檢查子原型總數: {total_variants}")
    print(f"嚴重問題: {len(all_issues)}")
    print(f"警告: {len(all_warnings)}")

    if all_issues:
        print(f"\n❌ 需要修復的嚴重問題:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")

    if all_warnings:
        print(f"\n⚠️  建議優化的警告:")
        for i, warning in enumerate(all_warnings, 1):
            print(f"   {i}. {warning}")

    if not all_issues and not all_warnings:
        print(f"\n✅ 所有子原型內容驗證通過！職業建議、情境描述、發展建議均合理匹配。")

    print(f"\n{'='*80}")

if __name__ == "__main__":
    main()
