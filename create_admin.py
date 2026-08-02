"""
Utility script to create or promote an Admin User in the database.
Automatically applies missing column migrations for role, status, last_login, and language.
Usage:
    python create_admin.py
"""
from sqlalchemy import text
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # 1. Ensure new columns exist on DB tables (SQLite / Postgres auto-migration)
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
            print(f"[MIGRATION] Executed: {stmt}")
        except Exception:
            db.session.rollback()  # Column already exists or failed silently

    # 2. Ensure all tables are created
    db.create_all()

    # 3. Prompt for Admin Credentials
    print("\n--- Create Admin Account ---")
    email = input("Enter admin email (default: admin@code-review.com): ").strip() or "admin@code-review.com"
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    password = input("Enter admin password (default: admin123): ").strip() or "admin123"

    # 4. Create or Promote Admin User
    user = User.query.filter_by(email=email).first()
    if user:
        user.role = "admin"
        user.status = "active"
        user.set_password(password)
        db.session.commit()
        print(f"\n[SUCCESS] User '{user.username}' ({user.email}) updated to Admin role!")
    else:
        new_admin = User(
            username=username,
            email=email,
            role="admin",
            status="active"
        )
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        print(f"\n[SUCCESS] Admin User '{username}' ({email}) created successfully!")
