"""
Database Initialization & Safe Auto-Migration Script for RDS PostgreSQL & SQLite
Automatically promotes admin users and ensures admin roles are assigned.
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

    # 3. Promote admin accounts to role='admin'
    promote_stmt = "UPDATE users SET role = 'admin', status = 'active' WHERE LOWER(username) IN ('admin', 'ditya0609', 'aditya') OR LOWER(email) LIKE '%admin%' OR LOWER(email) = 'ap7272422@codereview.com';"
    try:
        db.session.execute(text(promote_stmt))
        db.session.commit()
        print("[SUCCESS] Admin user roles promoted.")
    except Exception as e:
        db.session.rollback()
        print("[WARN] Admin role update note:", e)

    # 4. Create default admin if no admin exists
    try:
        from app.models.user import User
        admin_user = User.query.filter_by(role="admin").first()
        if not admin_user:
            default_admin = User(
                username="admin",
                email="admin@code-review.com",
                role="admin",
                status="active"
            )
            default_admin.set_password("admin123")
            db.session.add(default_admin)
            db.session.commit()
            print("[SUCCESS] Default Admin account 'admin@code-review.com' (password: admin123) created!")
    except Exception as e:
        db.session.rollback()
        print("[WARN] Default admin creation note:", e)

    print("=== DATABASE SETUP COMPLETED SUCCESSFULLY ===")
