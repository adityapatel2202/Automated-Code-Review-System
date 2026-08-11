"""
Database Initialization & Safe Auto-Migration Script for RDS PostgreSQL & SQLite
Automatically sets admin accounts, passwords, and roles on container startup.
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

    # 3. Reset/Set Admin User credentials & roles cleanly
    from app.models.user import User

    admin_accounts = [
        ("ditya0609", "ap7272422@gmail.com", "A@di1121"),
        ("Aditya patel", "Ditya09@gmail.com", "A@di1121"),
        ("admin", "admin@code-review.com", "admin123"),
        ("ap7272422", "ap7272422@codereview.com", "A@di1121")
    ]

    for uname, email_addr, pwd in admin_accounts:
        try:
            u = User.query.filter((User.email == email_addr) | (User.username == uname)).first()
            if u:
                u.role = "admin"
                u.status = "active"
                u.set_password(pwd)
                db.session.commit()
                print(f"[ADMIN READY] Account '{u.email}' ({u.username}) password set & role='admin'")
            else:
                new_u = User(
                    username=uname,
                    email=email_addr,
                    role="admin",
                    status="active"
                )
                new_u.set_password(pwd)
                db.session.add(new_u)
                db.session.commit()
                print(f"[ADMIN CREATED] Account '{email_addr}' ({uname}) created & role='admin'")
        except Exception as e:
            db.session.rollback()
            print(f"[WARN] Admin setup for {email_addr}:", e)

    print("=== DATABASE SETUP COMPLETED SUCCESSFULLY ===")
