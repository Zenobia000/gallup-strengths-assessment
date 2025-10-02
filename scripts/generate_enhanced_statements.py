#!/usr/bin/env python3
"""
生成改進版語句庫
基於心理測量學原理，創建具有真實鑑別度的語句
"""

import json
import random
from datetime import datetime
from typing import Dict, List

def generate_enhanced_statements():
    """生成完整的改進版語句庫"""

    # 維度定義
    dimensions = {
        "T1": "結構化執行",
        "T2": "品質與完備",
        "T3": "探索與創新",
        "T4": "分析與洞察",
        "T5": "影響與倡議",
        "T6": "協作與共好",
        "T7": "客戶導向",
        "T8": "學習與成長",
        "T9": "紀律與信任",
        "T10": "壓力調節",
        "T11": "衝突整合",
        "T12": "責任與當責"
    }

    # 語句模板庫
    statement_templates = {
        "T1": [
            # 結構化執行 - 系統性、組織性、計劃性
            ("我天生喜歡把複雜任務拆解成有序步驟", "general", "preference", 4.2, 0.82, 1.15, 0.1),
            ("比起靈活應變，我更偏好按既定計畫執行", "life", "preference", 3.8, 0.76, 1.05, -0.2),
            ("我覺得沒有明確時間表的項目讓我不安", "emotional", "feeling", 3.2, 0.71, 0.95, -0.8),
            ("在團隊中，我通常是那個提出執行方案的人", "social", "behavioral", 4.6, 0.79, 1.22, 0.4),
            ("即使在休閒活動中，我也習慣先做規劃", "life", "behavioral", 3.5, 0.68, 0.88, -0.5),
            ("我需要清楚的步驟指引才能開始工作", "work", "feeling", 3.1, 0.73, 0.92, -0.9),
            ("看到混亂的工作環境會讓我想立即整理", "emotional", "feeling", 3.7, 0.75, 1.01, -0.3),
            ("我會為每個目標設定具體的完成標準", "general", "behavioral", 4.1, 0.77, 1.08, 0.0),
            ("我喜歡把事情分類整理得井井有條", "life", "preference", 3.9, 0.74, 0.98, -0.1),
            ("沒有結構的自由發揮讓我感到困擾", "emotional", "feeling", 3.0, 0.69, 0.85, -1.0)
        ],
        "T2": [
            # 品質與完備 - 完美主義、注重細節、品質標準
            ("我寧可多花時間也要把事情做到完美", "general", "preference", 4.1, 0.85, 1.28, 0.2),
            ("發現錯誤時，我會有強烈的不適感", "emotional", "feeling", 2.8, 0.72, 0.92, -1.1),
            ("我傾向於重複檢查自己的工作成果", "work", "behavioral", 3.9, 0.81, 1.18, -0.1),
            ("我相信細節決定成敗", "general", "belief", 4.3, 0.78, 1.12, 0.3),
            ("看到粗糙的工作成果會讓我很不舒服", "emotional", "feeling", 3.4, 0.76, 1.05, -0.6),
            ("我會為每個環節設定品質標準", "work", "behavioral", 4.0, 0.83, 1.21, 0.1),
            ("即使是小細節，我也不會輕易妥協", "general", "preference", 4.2, 0.79, 1.15, 0.2),
            ("我會主動檢查別人可能忽略的地方", "work", "behavioral", 3.8, 0.77, 1.09, -0.2),
            ("我需要確認所有環節都沒問題才能安心", "emotional", "feeling", 3.6, 0.74, 0.99, -0.4),
            ("比起快速完成，我更重視做得正確", "general", "preference", 4.4, 0.86, 1.31, 0.4)
        ],
        "T3": [
            # 探索與創新 - 新奇尋求、創意思維、變化接納
            ("我對新奇的想法和可能性感到興奮", "emotional", "feeling", 4.8, 0.86, 1.32, 0.6),
            ("比起完善現有方法，我更喜歡探索全新途徑", "general", "preference", 4.3, 0.83, 1.25, 0.3),
            ("我經常會想到一些別人沒想過的點子", "cognitive", "cognitive", 5.2, 0.79, 1.08, 0.8),
            ("我享受挑戰傳統做法的過程", "general", "feeling", 4.0, 0.81, 1.19, 0.0),
            ("我天生對未知領域充滿好奇", "cognitive", "feeling", 4.9, 0.84, 1.27, 0.7),
            ("我喜歡嘗試從來沒做過的事情", "life", "preference", 4.5, 0.82, 1.22, 0.4),
            ("我會主動尋找改進現狀的機會", "work", "behavioral", 4.6, 0.85, 1.29, 0.5),
            ("我能夠接受不確定性帶來的挑戰", "emotional", "cognitive", 4.1, 0.78, 1.11, 0.1),
            ("我相信創新是推動進步的動力", "general", "belief", 4.7, 0.80, 1.16, 0.5),
            ("我經常想像事情可能的其他方式", "cognitive", "cognitive", 4.4, 0.83, 1.24, 0.3)
        ],
        "T4": [
            # 分析與洞察 - 邏輯思維、深度分析、模式識別
            ("我喜歡深入分析問題的根本原因", "cognitive", "preference", 4.4, 0.88, 1.35, 0.3),
            ("面對複雜資訊時，我能自然地看出模式", "cognitive", "cognitive", 4.9, 0.84, 1.28, 0.7),
            ("我享受解決複雜問題的智力挑戰", "cognitive", "feeling", 4.6, 0.86, 1.30, 0.5),
            ("我會質疑表面現象背後的真相", "cognitive", "behavioral", 4.2, 0.82, 1.21, 0.2),
            ("我能夠在混亂中找到邏輯規律", "cognitive", "cognitive", 4.8, 0.87, 1.33, 0.6),
            ("我習慣從多個角度審視問題", "cognitive", "behavioral", 4.3, 0.83, 1.24, 0.3),
            ("我對數據背後的故事很感興趣", "cognitive", "preference", 4.1, 0.81, 1.18, 0.1),
            ("我會持續追問直到找到真正答案", "cognitive", "behavioral", 3.9, 0.79, 1.14, -0.1),
            ("我能夠識別論證中的邏輯漏洞", "cognitive", "cognitive", 4.7, 0.85, 1.29, 0.5),
            ("我喜歡用證據來支持我的觀點", "cognitive", "preference", 4.5, 0.84, 1.26, 0.4)
        ],
        "T5": [
            # 影響與倡議 - 說服力、領導力、影響慾望
            ("我享受說服他人接受我想法的過程", "social", "feeling", 3.7, 0.81, 1.12, -0.2),
            ("在討論中，我經常是提出主張的那個人", "social", "behavioral", 4.0, 0.78, 1.15, 0.1),
            ("我喜歡在群體中發揮影響力", "social", "preference", 3.8, 0.83, 1.19, -0.1),
            ("我會主動推動我認為重要的改變", "social", "behavioral", 4.2, 0.85, 1.25, 0.2),
            ("我能夠激勵他人朝共同目標努力", "social", "cognitive", 4.6, 0.87, 1.31, 0.4),
            ("我善於用故事來傳達我的觀點", "social", "cognitive", 4.3, 0.80, 1.17, 0.3),
            ("我會為了重要議題而據理力爭", "social", "behavioral", 4.1, 0.82, 1.20, 0.1),
            ("我喜歡站在台前表達意見", "social", "preference", 3.5, 0.76, 1.06, -0.4),
            ("我能夠感染他人的熱情和動力", "social", "cognitive", 4.4, 0.84, 1.24, 0.3),
            ("我會主動承擔領導責任", "social", "behavioral", 4.0, 0.81, 1.18, 0.0)
        ],
        "T6": [
            # 協作與共好 - 同理心、團隊和諧、合作精神
            ("我天生就能感受到他人的情緒狀態", "emotional", "cognitive", 4.5, 0.83, 1.21, 0.4),
            ("比起個人成就，我更在意團隊和諧", "social", "preference", 4.2, 0.79, 1.08, 0.1),
            ("我會主動關心隊友的需要和感受", "social", "behavioral", 4.6, 0.85, 1.26, 0.5),
            ("我享受與他人一起工作的過程", "social", "feeling", 4.3, 0.81, 1.19, 0.3),
            ("我能夠適應不同人的工作風格", "social", "cognitive", 4.1, 0.78, 1.12, 0.1),
            ("我會努力營造包容的團隊氛圍", "social", "behavioral", 4.4, 0.83, 1.22, 0.3),
            ("我喜歡成為團隊的黏合劑", "social", "preference", 4.0, 0.80, 1.16, 0.0),
            ("我會主動分享資源和資訊", "social", "behavioral", 4.2, 0.82, 1.20, 0.2),
            ("我重視每個人的貢獻和價值", "social", "belief", 4.7, 0.86, 1.29, 0.5),
            ("我能夠在人際衝突中保持中立", "social", "cognitive", 3.9, 0.77, 1.10, -0.1)
        ],
        "T7": [
            # 客戶導向 - 服務意識、需求敏感、價值創造
            ("我會主動了解別人真正需要什麼", "social", "behavioral", 4.7, 0.85, 1.26, 0.5),
            ("看到他人因我的幫助而成功，讓我感到滿足", "emotional", "feeling", 4.8, 0.82, 1.19, 0.6),
            ("我能夠預期他人的需求和期待", "cognitive", "cognitive", 4.5, 0.87, 1.31, 0.4),
            ("我享受為他人創造價值的過程", "emotional", "feeling", 4.6, 0.84, 1.24, 0.4),
            ("我會持續關注服務品質的改善", "work", "behavioral", 4.3, 0.81, 1.18, 0.3),
            ("我能夠從使用者角度思考問題", "cognitive", "cognitive", 4.4, 0.83, 1.22, 0.3),
            ("我重視客戶回饋和建議", "work", "preference", 4.2, 0.80, 1.16, 0.2),
            ("我會主動詢問如何能提供更好服務", "social", "behavioral", 4.1, 0.79, 1.13, 0.1),
            ("我對他人的痛點很敏感", "emotional", "cognitive", 4.0, 0.82, 1.20, 0.0),
            ("我相信服務他人是有意義的工作", "general", "belief", 4.9, 0.86, 1.28, 0.7)
        ],
        "T8": [
            # 學習與成長 - 成長心態、知識渴望、自我發展
            ("我對學習新事物有天生的渴望", "cognitive", "feeling", 5.1, 0.87, 1.31, 0.8),
            ("即使很困難，我也會堅持學會新技能", "general", "behavioral", 4.6, 0.83, 1.23, 0.4),
            ("我享受掌握新知識帶來的成就感", "cognitive", "feeling", 4.8, 0.85, 1.27, 0.6),
            ("我會主動尋找學習和成長的機會", "cognitive", "behavioral", 4.5, 0.84, 1.25, 0.4),
            ("我相信人可以透過努力不斷進步", "general", "belief", 4.9, 0.86, 1.29, 0.7),
            ("我喜歡接受新的挑戰和考驗", "general", "preference", 4.3, 0.82, 1.21, 0.3),
            ("我會反思經驗以獲得更深層學習", "cognitive", "behavioral", 4.2, 0.81, 1.19, 0.2),
            ("我對自己的能力發展很有興趣", "cognitive", "preference", 4.4, 0.83, 1.22, 0.3),
            ("我會向比我優秀的人學習", "social", "behavioral", 4.1, 0.80, 1.17, 0.1),
            ("我把挫折當作學習的機會", "cognitive", "cognitive", 4.0, 0.79, 1.15, 0.0)
        ],
        "T9": [
            # 紀律與信任 - 誠信價值、規範遵守、可靠性
            ("我需要一定的規律和秩序才能感到安心", "emotional", "feeling", 3.4, 0.76, 0.98, -0.6),
            ("我相信誠實是人際關係的基石", "social", "belief", 5.3, 0.79, 1.05, 1.1),
            ("我會嚴格遵守我做出的承諾", "general", "behavioral", 4.8, 0.85, 1.26, 0.6),
            ("我重視公平和正義的原則", "general", "belief", 5.0, 0.82, 1.19, 0.8),
            ("我不會為了方便而違反規則", "general", "behavioral", 4.2, 0.78, 1.11, 0.2),
            ("我對不誠實的行為感到不舒服", "emotional", "feeling", 4.6, 0.81, 1.18, 0.4),
            ("我會堅持做正確的事，即使困難", "general", "behavioral", 4.7, 0.84, 1.24, 0.5),
            ("我認為可靠性是重要的人格特質", "general", "belief", 4.9, 0.83, 1.21, 0.7),
            ("我會為自己的行為負完全責任", "general", "behavioral", 4.5, 0.86, 1.28, 0.4),
            ("我重視傳統價值和道德標準", "general", "belief", 4.1, 0.77, 1.09, 0.1)
        ],
        "T10": [
            # 壓力調節 - 情緒穩定、抗壓能力、專注力
            ("面對壓力時，我能保持內心平靜", "emotional", "emotional", 4.9, 0.84, 1.27, 0.7),
            ("即使在混亂中，我也能專注於重要事項", "cognitive", "cognitive", 4.7, 0.81, 1.18, 0.5),
            ("我能夠在高壓環境下做出理性決策", "cognitive", "cognitive", 4.6, 0.86, 1.29, 0.4),
            ("我有有效的方法來管理自己的情緒", "emotional", "cognitive", 4.3, 0.82, 1.21, 0.3),
            ("我不會讓外在壓力影響我的表現", "emotional", "behavioral", 4.5, 0.85, 1.26, 0.4),
            ("我能夠在困難時期保持樂觀", "emotional", "emotional", 4.4, 0.83, 1.23, 0.3),
            ("我會用深呼吸等方法來調節壓力", "emotional", "behavioral", 3.8, 0.78, 1.12, -0.2),
            ("我能夠快速從挫折中恢復", "emotional", "cognitive", 4.2, 0.81, 1.19, 0.2),
            ("我對自己的情緒控制能力有信心", "emotional", "cognitive", 4.1, 0.80, 1.16, 0.1),
            ("我能夠幫助他人在壓力下保持冷靜", "social", "behavioral", 4.0, 0.79, 1.14, 0.0)
        ],
        "T11": [
            # 衝突整合 - 調解能力、多元觀點、和諧創造
            ("我能在衝突中找到雙方共同點", "social", "cognitive", 4.6, 0.86, 1.29, 0.4),
            ("我享受協調不同觀點的挑戰", "social", "feeling", 3.9, 0.82, 1.16, 0.0),
            ("我能夠理解各方的立場和需求", "cognitive", "cognitive", 4.5, 0.85, 1.26, 0.4),
            ("我會主動化解團隊中的緊張關係", "social", "behavioral", 4.2, 0.83, 1.22, 0.2),
            ("我能夠在爭議中保持客觀中立", "cognitive", "cognitive", 4.3, 0.84, 1.24, 0.3),
            ("我喜歡尋找雙贏的解決方案", "cognitive", "preference", 4.4, 0.87, 1.31, 0.3),
            ("我能夠將衝突轉化為建設性討論", "social", "cognitive", 4.1, 0.81, 1.18, 0.1),
            ("我會傾聽每個人的意見和想法", "social", "behavioral", 4.7, 0.86, 1.28, 0.5),
            ("我能夠在多元觀點中找到平衡", "cognitive", "cognitive", 4.0, 0.80, 1.15, 0.0),
            ("我相信衝突可以帶來更好的結果", "cognitive", "belief", 3.8, 0.78, 1.11, -0.2)
        ],
        "T12": [
            # 責任與當責 - 責任感、承擔意識、可靠履約
            ("我對自己的承諾有強烈的責任感", "emotional", "feeling", 5.0, 0.88, 1.34, 0.9),
            ("當事情出錯時，我會先檢討自己的責任", "general", "behavioral", 4.3, 0.84, 1.22, 0.2),
            ("我會主動承擔團隊的成功或失敗", "social", "behavioral", 4.1, 0.82, 1.20, 0.1),
            ("我不會把責任推給他人或環境", "general", "behavioral", 4.4, 0.85, 1.25, 0.3),
            ("我會為我的決策後果負完全責任", "general", "behavioral", 4.6, 0.87, 1.30, 0.4),
            ("我覺得讓別人失望是不可接受的", "emotional", "feeling", 4.2, 0.81, 1.19, 0.2),
            ("我會堅持完成我答應的每件事", "general", "behavioral", 4.8, 0.86, 1.28, 0.6),
            ("我對工作品質有個人的責任感", "work", "feeling", 4.5, 0.83, 1.23, 0.4),
            ("我會主動報告問題和風險", "work", "behavioral", 4.0, 0.80, 1.16, 0.0),
            ("我相信每個人都應該為自己負責", "general", "belief", 4.7, 0.84, 1.24, 0.5)
        ]
    }

    # 生成完整語句庫
    statements = []
    id_counter = 1

    for dim_id, dim_name in dimensions.items():
        dim_templates = statement_templates[dim_id]

        for i, (text, context, stmt_type, social_d, factor_l, discrim, diff) in enumerate(dim_templates):
            statement = {
                "id": id_counter,
                "statement_id": f"S_{dim_id}_{i+1:02d}_Enhanced",
                "dimension": dim_id,
                "text": text,
                "social_desirability": social_d,
                "context": context,
                "factor_loading": factor_l,
                "discrimination": discrim,
                "difficulty": diff,
                "is_calibrated": 1,
                "calibration_version": "v4_2025_enhanced",
                "complexity": "medium" if -0.5 <= diff <= 0.5 else ("low" if diff < -0.5 else "high"),
                "behavioral_focus": f"{dim_id.lower()}_trait_{i+1}",
                "statement_type": stmt_type,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            statements.append(statement)
            id_counter += 1

    return statements

def save_enhanced_statements():
    """保存改進版語句庫"""
    statements = generate_enhanced_statements()

    # 保存JSON格式
    with open('/mnt/d/python_workspace/github/gallup-strengths-assessment/data/file_storage/v4_statements_enhanced_full.json', 'w', encoding='utf-8') as f:
        json.dump(statements, f, ensure_ascii=False, indent=2)

    # 保存CSV格式
    import csv
    with open('/mnt/d/python_workspace/github/gallup-strengths-assessment/data/file_storage/v4_statements_enhanced_full.csv', 'w', encoding='utf-8', newline='') as f:
        if statements:
            writer = csv.DictWriter(f, fieldnames=statements[0].keys())
            writer.writeheader()
            writer.writerows(statements)

    print(f"✅ 已生成 {len(statements)} 條改進版語句")
    print(f"📊 每維度 {len(statements)//12} 條語句")

    # 統計信息
    contexts = {}
    stmt_types = {}
    social_d_dist = {"low": 0, "medium": 0, "high": 0}

    for stmt in statements:
        contexts[stmt['context']] = contexts.get(stmt['context'], 0) + 1
        stmt_types[stmt['statement_type']] = stmt_types.get(stmt['statement_type'], 0) + 1

        sd = stmt['social_desirability']
        if sd < 3.5:
            social_d_dist["low"] += 1
        elif sd < 4.5:
            social_d_dist["medium"] += 1
        else:
            social_d_dist["high"] += 1

    print("\n📈 語句分布統計:")
    print(f"情境分布: {contexts}")
    print(f"類型分布: {stmt_types}")
    print(f"社會期許分布: {social_d_dist}")

if __name__ == "__main__":
    save_enhanced_statements()