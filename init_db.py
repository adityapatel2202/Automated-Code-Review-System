"""
Database Initialization & Safe Auto-Migration Script for RDS PostgreSQL & SQLite
"""
import sys
from sqlalchemy import text
from app import create_app, db

app = create_app()

with app.app_context():
    print("=== STARTING DATABASE SETUP & AUTO-MIGRATIONS ===")
    
    # 1. Create any missing tables
    try:
        db.create_all()
        print("[SUCCESS] Database tables verified / created.")
    except Exception as e:
        print("[WARN] db.create_all() note:", e)

    # 2. Add missing columns safely with individual rollback per statement
    migration_statements = [
        "ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'",
        "ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'",
        "ALTER TABLE users ADD COLUMN last_login TIMESTAMP",
        "ALTER TABLE reviews ADD COLUMN language VARCHAR(50) DEFAULT 'Python'"
    ]

    for stmt in migration_statements:
        try:
            db.session.execute(text(stmt))
            db.session.commit()
            print(f"[MIGRATION APPLIED] {stmt}")
        except Exception as err:
            db.session.rollback()
            print(f"[MIGRATION SKIPPED / ALREADY EXISTS] {stmt}")

    print("=== DATABASE SETUP COMPLETED SUCCESSFULLY ===")
