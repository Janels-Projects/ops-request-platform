from models.db import get_db_connection
from werkzeug.security import generate_password_hash


def seed_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if admin already exists
    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        ("admin@example.com",)
    )
    existing_admin = cursor.fetchone()

    if existing_admin:
        conn.close()
        print("ℹ️ Admin user already exists")
        return

    password_hash = generate_password_hash("admin123")

    cursor.execute(
        """
        INSERT INTO users (email, password, role)
        VALUES (?, ?, ?)
        """,
        ("admin@example.com", password_hash, "admin")
    )

    conn.commit()
    conn.close()

    print("✅ Admin user created")

