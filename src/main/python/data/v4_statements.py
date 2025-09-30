"""
V4.0 Thurstonian IRT 語句池資料
包含12個維度的60個初始語句
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class StatementData:
    """語句資料結構"""
    statement_id: str
    dimension: str
    text: str
    social_desirability: float
    context: str  # "work", "team", "general"
    factor_loading: float = 0.7  # 初始預設值，待校準


# 12維度語句池定義
STATEMENT_POOL: Dict[str, List[Dict]] = {
    "Achiever": [
        {
            "statement_id": "ACH001",
            "text": "我每天都會列出待辦事項清單並逐項完成",
            "social_desirability": 5.2,
            "context": "work",
            "factor_loading": 0.75
        },
        {
            "statement_id": "ACH002",
            "text": "完成任務帶給我極大的滿足感",
            "social_desirability": 5.5,
            "context": "general",
            "factor_loading": 0.72
        },
        {
            "statement_id": "ACH003",
            "text": "我經常在下班後還繼續思考如何提高效率",
            "social_desirability": 4.8,
            "context": "work",
            "factor_loading": 0.68
        },
        {
            "statement_id": "ACH004",
            "text": "沒有具體成果的一天讓我感到焦慮",
            "social_desirability": 4.2,
            "context": "general",
            "factor_loading": 0.70
        },
        {
            "statement_id": "ACH005",
            "text": "我會追蹤並記錄自己的工作進度",
            "social_desirability": 5.1,
            "context": "work",
            "factor_loading": 0.73
        }
    ],
    "Activator": [
        {
            "statement_id": "ACT001",
            "text": "我傾向先開始行動，邊做邊調整",
            "social_desirability": 4.9,
            "context": "work",
            "factor_loading": 0.76
        },
        {
            "statement_id": "ACT002",
            "text": "長時間的會議討論讓我不耐煩",
            "social_desirability": 4.3,
            "context": "work",
            "factor_loading": 0.65
        },
        {
            "statement_id": "ACT003",
            "text": "我善於推動停滯的專案向前進展",
            "social_desirability": 5.6,
            "context": "work",
            "factor_loading": 0.78
        },
        {
            "statement_id": "ACT004",
            "text": "比起完美計劃，我更重視快速執行",
            "social_desirability": 4.7,
            "context": "general",
            "factor_loading": 0.71
        },
        {
            "statement_id": "ACT005",
            "text": "我經常是團隊中第一個採取行動的人",
            "social_desirability": 5.3,
            "context": "team",
            "factor_loading": 0.74
        }
    ],
    "Adaptability": [
        {
            "statement_id": "ADA001",
            "text": "突發狀況不會讓我感到慌張",
            "social_desirability": 5.4,
            "context": "general",
            "factor_loading": 0.72
        },
        {
            "statement_id": "ADA002",
            "text": "我能輕鬆調整計劃以應對新情況",
            "social_desirability": 5.2,
            "context": "work",
            "factor_loading": 0.75
        },
        {
            "statement_id": "ADA003",
            "text": "相比長期規劃，我更擅長處理當前事務",
            "social_desirability": 4.5,
            "context": "general",
            "factor_loading": 0.67
        },
        {
            "statement_id": "ADA004",
            "text": "變化帶給我新鮮感而非壓力",
            "social_desirability": 5.0,
            "context": "general",
            "factor_loading": 0.73
        },
        {
            "statement_id": "ADA005",
            "text": "我享受每天面對不同挑戰的工作",
            "social_desirability": 5.1,
            "context": "work",
            "factor_loading": 0.71
        }
    ],
    "Analytical": [
        {
            "statement_id": "ANA001",
            "text": "我需要充分的數據才能做出決定",
            "social_desirability": 5.0,
            "context": "work",
            "factor_loading": 0.77
        },
        {
            "statement_id": "ANA002",
            "text": "我經常質疑他人提出的結論是否有證據支持",
            "social_desirability": 4.4,
            "context": "general",
            "factor_loading": 0.69
        },
        {
            "statement_id": "ANA003",
            "text": "我擅長發現數據中的模式和趨勢",
            "social_desirability": 5.5,
            "context": "work",
            "factor_loading": 0.80
        },
        {
            "statement_id": "ANA004",
            "text": "情感因素很少影響我的判斷",
            "social_desirability": 4.6,
            "context": "general",
            "factor_loading": 0.66
        },
        {
            "statement_id": "ANA005",
            "text": "我喜歡深入研究問題的根本原因",
            "social_desirability": 5.3,
            "context": "work",
            "factor_loading": 0.74
        }
    ],
    "Arranger": [
        {
            "statement_id": "ARR001",
            "text": "我擅長同時管理多個任務和專案",
            "social_desirability": 5.6,
            "context": "work",
            "factor_loading": 0.79
        },
        {
            "statement_id": "ARR002",
            "text": "我能快速找出最有效的資源配置方案",
            "social_desirability": 5.4,
            "context": "work",
            "factor_loading": 0.76
        },
        {
            "statement_id": "ARR003",
            "text": "複雜的協調工作對我來說是種享受",
            "social_desirability": 4.8,
            "context": "work",
            "factor_loading": 0.70
        },
        {
            "statement_id": "ARR004",
            "text": "我經常重新安排計劃以達到更好效果",
            "social_desirability": 5.0,
            "context": "general",
            "factor_loading": 0.72
        },
        {
            "statement_id": "ARR005",
            "text": "我善於識別並調動團隊成員的優勢",
            "social_desirability": 5.7,
            "context": "team",
            "factor_loading": 0.81
        }
    ],
    "Belief": [
        {
            "statement_id": "BEL001",
            "text": "我的核心價值觀指引著我的所有決定",
            "social_desirability": 5.5,
            "context": "general",
            "factor_loading": 0.78
        },
        {
            "statement_id": "BEL002",
            "text": "工作的意義比薪資更重要",
            "social_desirability": 5.2,
            "context": "work",
            "factor_loading": 0.73
        },
        {
            "statement_id": "BEL003",
            "text": "我難以在價值觀不合的環境中工作",
            "social_desirability": 4.7,
            "context": "work",
            "factor_loading": 0.71
        },
        {
            "statement_id": "BEL004",
            "text": "我願意為自己相信的事業付出額外努力",
            "social_desirability": 5.4,
            "context": "general",
            "factor_loading": 0.76
        },
        {
            "statement_id": "BEL005",
            "text": "違背原則的成功對我毫無意義",
            "social_desirability": 5.3,
            "context": "general",
            "factor_loading": 0.74
        }
    ],
    "Command": [
        {
            "statement_id": "CMD001",
            "text": "在混亂情況下我自然會接手領導",
            "social_desirability": 5.1,
            "context": "team",
            "factor_loading": 0.77
        },
        {
            "statement_id": "CMD002",
            "text": "我不害怕與他人產生衝突",
            "social_desirability": 4.2,
            "context": "general",
            "factor_loading": 0.68
        },
        {
            "statement_id": "CMD003",
            "text": "我能讓猶豫不決的團隊快速行動",
            "social_desirability": 5.4,
            "context": "team",
            "factor_loading": 0.79
        },
        {
            "statement_id": "CMD004",
            "text": "直接表達意見比顧慮他人感受更重要",
            "social_desirability": 4.0,
            "context": "general",
            "factor_loading": 0.65
        },
        {
            "statement_id": "CMD005",
            "text": "我享受承擔決策責任的壓力",
            "social_desirability": 4.9,
            "context": "work",
            "factor_loading": 0.73
        }
    ],
    "Communication": [
        {
            "statement_id": "COM001",
            "text": "我能輕鬆地向不同背景的人解釋複雜概念",
            "social_desirability": 5.6,
            "context": "general",
            "factor_loading": 0.80
        },
        {
            "statement_id": "COM002",
            "text": "我經常成為團隊的發言人",
            "social_desirability": 5.0,
            "context": "team",
            "factor_loading": 0.72
        },
        {
            "statement_id": "COM003",
            "text": "寫作和演講對我來說很自然",
            "social_desirability": 5.2,
            "context": "general",
            "factor_loading": 0.75
        },
        {
            "statement_id": "COM004",
            "text": "我喜歡通過故事來傳達觀點",
            "social_desirability": 5.1,
            "context": "general",
            "factor_loading": 0.71
        },
        {
            "statement_id": "COM005",
            "text": "安靜的會議讓我忍不住想發言",
            "social_desirability": 4.5,
            "context": "work",
            "factor_loading": 0.67
        }
    ],
    "Competition": [
        {
            "statement_id": "CMP001",
            "text": "我經常將自己的表現與他人比較",
            "social_desirability": 4.3,
            "context": "general",
            "factor_loading": 0.70
        },
        {
            "statement_id": "CMP002",
            "text": "贏得競爭給我強大的動力",
            "social_desirability": 4.8,
            "context": "general",
            "factor_loading": 0.75
        },
        {
            "statement_id": "CMP003",
            "text": "第二名對我來說等同於失敗",
            "social_desirability": 3.9,
            "context": "general",
            "factor_loading": 0.66
        },
        {
            "statement_id": "CMP004",
            "text": "我會研究競爭對手以確保領先",
            "social_desirability": 5.0,
            "context": "work",
            "factor_loading": 0.73
        },
        {
            "statement_id": "CMP005",
            "text": "沒有競爭的環境讓我失去動力",
            "social_desirability": 4.4,
            "context": "work",
            "factor_loading": 0.69
        }
    ],
    "Connectedness": [
        {
            "statement_id": "CON001",
            "text": "我相信所有事件的發生都有其原因",
            "social_desirability": 5.0,
            "context": "general",
            "factor_loading": 0.71
        },
        {
            "statement_id": "CON002",
            "text": "我能看到不同事物之間的深層聯繫",
            "social_desirability": 5.3,
            "context": "general",
            "factor_loading": 0.74
        },
        {
            "statement_id": "CON003",
            "text": "幫助他人讓我感受到生命的意義",
            "social_desirability": 5.7,
            "context": "general",
            "factor_loading": 0.79
        },
        {
            "statement_id": "CON004",
            "text": "我重視團隊的集體成就勝過個人榮譽",
            "social_desirability": 5.4,
            "context": "team",
            "factor_loading": 0.76
        },
        {
            "statement_id": "CON005",
            "text": "巧合對我來說往往有特殊含義",
            "social_desirability": 4.6,
            "context": "general",
            "factor_loading": 0.67
        }
    ],
    "Consistency": [
        {
            "statement_id": "CST001",
            "text": "規則應該平等地適用於所有人",
            "social_desirability": 5.6,
            "context": "general",
            "factor_loading": 0.78
        },
        {
            "statement_id": "CST002",
            "text": "特權和例外讓我感到不適",
            "social_desirability": 5.0,
            "context": "general",
            "factor_loading": 0.72
        },
        {
            "statement_id": "CST003",
            "text": "我會確保每個人都有平等的機會",
            "social_desirability": 5.8,
            "context": "team",
            "factor_loading": 0.81
        },
        {
            "statement_id": "CST004",
            "text": "程序的一致性比靈活性更重要",
            "social_desirability": 4.5,
            "context": "work",
            "factor_loading": 0.68
        },
        {
            "statement_id": "CST005",
            "text": "我難以接受基於關係的優待",
            "social_desirability": 5.1,
            "context": "work",
            "factor_loading": 0.73
        }
    ],
    "Context": [
        {
            "statement_id": "CTX001",
            "text": "了解事情的來龍去脈對我很重要",
            "social_desirability": 5.3,
            "context": "general",
            "factor_loading": 0.75
        },
        {
            "statement_id": "CTX002",
            "text": "我經常引用過去的經驗來解決當前問題",
            "social_desirability": 5.2,
            "context": "work",
            "factor_loading": 0.73
        },
        {
            "statement_id": "CTX003",
            "text": "沒有背景資訊我難以做出判斷",
            "social_desirability": 4.8,
            "context": "general",
            "factor_loading": 0.70
        },
        {
            "statement_id": "CTX004",
            "text": "我喜歡研究事物的歷史和演變",
            "social_desirability": 5.0,
            "context": "general",
            "factor_loading": 0.72
        },
        {
            "statement_id": "CTX005",
            "text": "理解組織文化的形成過程幫助我更好地融入",
            "social_desirability": 5.4,
            "context": "work",
            "factor_loading": 0.76
        }
    ]
}


def get_all_statements() -> List[StatementData]:
    """獲取所有語句資料"""
    statements = []
    for dimension, dimension_statements in STATEMENT_POOL.items():
        for stmt_dict in dimension_statements:
            statements.append(StatementData(
                statement_id=stmt_dict["statement_id"],
                dimension=dimension,
                text=stmt_dict["text"],
                social_desirability=stmt_dict["social_desirability"],
                context=stmt_dict["context"],
                factor_loading=stmt_dict["factor_loading"]
            ))
    return statements


def get_statements_by_dimension(dimension: str) -> List[StatementData]:
    """獲取特定維度的語句"""
    if dimension not in STATEMENT_POOL:
        raise ValueError(f"Unknown dimension: {dimension}")

    statements = []
    for stmt_dict in STATEMENT_POOL[dimension]:
        statements.append(StatementData(
            statement_id=stmt_dict["statement_id"],
            dimension=dimension,
            text=stmt_dict["text"],
            social_desirability=stmt_dict["social_desirability"],
            context=stmt_dict["context"],
            factor_loading=stmt_dict["factor_loading"]
        ))
    return statements


def get_statement_by_id(statement_id: str) -> StatementData:
    """根據ID獲取特定語句"""
    for dimension, dimension_statements in STATEMENT_POOL.items():
        for stmt_dict in dimension_statements:
            if stmt_dict["statement_id"] == statement_id:
                return StatementData(
                    statement_id=stmt_dict["statement_id"],
                    dimension=dimension,
                    text=stmt_dict["text"],
                    social_desirability=stmt_dict["social_desirability"],
                    context=stmt_dict["context"],
                    factor_loading=stmt_dict["factor_loading"]
                )
    raise ValueError(f"Statement not found: {statement_id}")


# 統計資訊
def get_pool_statistics() -> Dict:
    """獲取語句池統計資訊"""
    all_statements = get_all_statements()

    stats = {
        "total_statements": len(all_statements),
        "dimensions": len(STATEMENT_POOL),
        "statements_per_dimension": {},
        "social_desirability": {
            "mean": sum(s.social_desirability for s in all_statements) / len(all_statements),
            "min": min(s.social_desirability for s in all_statements),
            "max": max(s.social_desirability for s in all_statements),
        },
        "context_distribution": {},
        "factor_loading": {
            "mean": sum(s.factor_loading for s in all_statements) / len(all_statements),
            "min": min(s.factor_loading for s in all_statements),
            "max": max(s.factor_loading for s in all_statements),
        }
    }

    # 計算每維度語句數
    for dimension in STATEMENT_POOL:
        stats["statements_per_dimension"][dimension] = len(STATEMENT_POOL[dimension])

    # 計算情境分布
    context_counts = {}
    for stmt in all_statements:
        context_counts[stmt.context] = context_counts.get(stmt.context, 0) + 1
    stats["context_distribution"] = context_counts

    return stats

# Export dimension mapping for API
# Build dimension mapping from statement IDs to dimensions
DIMENSION_MAPPING = {}
for dimension, statements in STATEMENT_POOL.items():
    for stmt in statements:
        DIMENSION_MAPPING[stmt['statement_id']] = dimension