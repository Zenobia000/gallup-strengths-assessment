"""
改進版語句庫載入器
提供切換到改進版語句庫的功能
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from utils.path_utils import get_file_storage_dir  # Cross-platform paths

logger = logging.getLogger(__name__)

class EnhancedStatementLoader:
    """改進版語句庫載入器"""

    @staticmethod
    def load_enhanced_statements() -> List[Dict[str, Any]]:
        """載入改進版語句庫"""
        try:
            enhanced_path = Path(get_file_storage_dir() / "v4_statements_enhanced_full.json"

            if enhanced_path.exists():
                with open(enhanced_path, 'r', encoding='utf-8') as f:
                    statements = json.load(f)
                logger.info(f"✅ 已載入改進版語句庫: {len(statements)} 條語句")
                return statements
            else:
                logger.warning("改進版語句庫不存在，回退到原始版本")
                return EnhancedStatementLoader.load_original_statements()

        except Exception as e:
            logger.error(f"載入改進版語句庫失敗: {e}")
            return EnhancedStatementLoader.load_original_statements()

    @staticmethod
    def load_original_statements() -> List[Dict[str, Any]]:
        """載入原始語句庫作為回退"""
        try:
            original_path = Path(get_file_storage_dir() / "v4_statements.json"

            with open(original_path, 'r', encoding='utf-8') as f:
                statements = json.load(f)
            logger.info(f"📚 已載入原始語句庫: {len(statements)} 條語句")
            return statements

        except Exception as e:
            logger.error(f"載入原始語句庫失敗: {e}")
            return []

    @staticmethod
    def load_enhanced_blocks() -> List[Dict[str, Any]]:
        """載入改進版題組"""
        try:
            blocks_path = Path(get_file_storage_dir() / "v4_blocks_enhanced.json"

            if blocks_path.exists():
                with open(blocks_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                blocks = data.get('blocks', [])
                logger.info(f"✅ 已載入改進版題組: {len(blocks)} 個題組")
                return blocks
            else:
                logger.warning("改進版題組不存在")
                return []

        except Exception as e:
            logger.error(f"載入改進版題組失敗: {e}")
            return []

    @staticmethod
    def backup_and_replace_statements():
        """備份原始語句庫並替換為改進版"""
        try:
            # 備份原始檔案
            original_path = Path(get_file_storage_dir() / "v4_statements.json"
            backup_path = Path(get_file_storage_dir() / "v4_statements_backup_original.json"

            if original_path.exists():
                import shutil
                shutil.copy2(original_path, backup_path)
                logger.info(f"✅ 已備份原始語句庫到: {backup_path}")

            # 載入改進版語句
            enhanced_statements = EnhancedStatementLoader.load_enhanced_statements()

            if enhanced_statements:
                # 替換主要語句庫檔案
                with open(original_path, 'w', encoding='utf-8') as f:
                    json.dump(enhanced_statements, f, ensure_ascii=False, indent=2)

                logger.info(f"✅ 已替換主要語句庫為改進版: {len(enhanced_statements)} 條語句")
                return True
            else:
                logger.error("改進版語句庫為空，未執行替換")
                return False

        except Exception as e:
            logger.error(f"替換語句庫失敗: {e}")
            return False

    @staticmethod
    def restore_original_statements():
        """恢復原始語句庫"""
        try:
            original_path = Path(get_file_storage_dir() / "v4_statements.json"
            backup_path = Path(get_file_storage_dir() / "v4_statements_backup_original.json"

            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, original_path)
                logger.info("✅ 已恢復原始語句庫")
                return True
            else:
                logger.error("找不到原始語句庫備份")
                return False

        except Exception as e:
            logger.error(f"恢復原始語句庫失敗: {e}")
            return False

    @staticmethod
    def get_statement_statistics(statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """獲取語句庫統計信息"""
        if not statements:
            return {}

        # 統計基本信息
        total_statements = len(statements)
        dimensions = {}
        contexts = {}
        statement_types = {}
        social_desirability_dist = {"low": 0, "medium": 0, "high": 0}

        for stmt in statements:
            # 維度統計
            dim = stmt.get('dimension', 'Unknown')
            dimensions[dim] = dimensions.get(dim, 0) + 1

            # 情境統計
            context = stmt.get('context', 'Unknown')
            contexts[context] = contexts.get(context, 0) + 1

            # 類型統計
            stmt_type = stmt.get('statement_type', 'Unknown')
            statement_types[stmt_type] = statement_types.get(stmt_type, 0) + 1

            # 社會期許分布
            sd = stmt.get('social_desirability', 4.0)
            if sd < 3.5:
                social_desirability_dist["low"] += 1
            elif sd < 4.5:
                social_desirability_dist["medium"] += 1
            else:
                social_desirability_dist["high"] += 1

        return {
            "total_statements": total_statements,
            "dimensions": dimensions,
            "contexts": contexts,
            "statement_types": statement_types,
            "social_desirability_distribution": social_desirability_dist,
            "average_social_desirability": sum(stmt.get('social_desirability', 4.0) for stmt in statements) / total_statements
        }


def main():
    """測試和示範功能"""
    print("🔧 改進版語句庫載入器測試")

    # 載入改進版語句
    enhanced_statements = EnhancedStatementLoader.load_enhanced_statements()

    if enhanced_statements:
        print("\n📊 改進版語句庫統計:")
        stats = EnhancedStatementLoader.get_statement_statistics(enhanced_statements)

        print(f"總語句數: {stats['total_statements']}")
        print(f"維度分布: {stats['dimensions']}")
        print(f"情境分布: {stats['contexts']}")
        print(f"類型分布: {stats['statement_types']}")
        print(f"社會期許分布: {stats['social_desirability_distribution']}")
        print(f"平均社會期許: {stats['average_social_desirability']:.2f}")

    # 載入改進版題組
    enhanced_blocks = EnhancedStatementLoader.load_enhanced_blocks()

    if enhanced_blocks:
        print(f"\n🎯 改進版題組數量: {len(enhanced_blocks)}")
        avg_score = sum(block.get('competitive_score', 0) for block in enhanced_blocks) / len(enhanced_blocks)
        print(f"平均競爭性得分: {avg_score:.3f}")

    print("\n✅ 測試完成")

if __name__ == "__main__":
    main()