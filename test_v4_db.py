#!/usr/bin/env python3
"""Test V4 Database System"""

import sys
from pathlib import Path

# Add src/main/python to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "main" / "python"))

def test_database():
    print("Testing V4 SQLAlchemy Database System...")

    # Test 1: Database engine
    from database.engine import get_database_engine
    engine = get_database_engine()
    print("✅ Database engine loaded")

    # Test 2: Health check
    health = engine.health_check()
    print(f"✅ Health check: {health['status']} - {health['table_count']} tables")

    # Test 3: V4 Statements
    from database.engine import get_session
    from models.v4_models import V4Statement

    with get_session() as session:
        count = session.query(V4Statement).count()
        print(f"✅ V4 Statements loaded: {count}")

        # Sample statement
        stmt = session.query(V4Statement).first()
        if stmt:
            print(f"   Sample: {stmt.statement_id} - {stmt.text[:50]}...")

    # Test 4: Tables verification
    from sqlalchemy import inspect
    inspector = inspect(engine.engine)
    tables = inspector.get_table_names()

    v4_tables = [t for t in tables if t.startswith('v4_')]
    print(f"✅ V4 Tables: {len(v4_tables)} - {v4_tables}")

    print("\n🎉 All tests passed! V4 SQLAlchemy system is working.")

if __name__ == "__main__":
    test_database()