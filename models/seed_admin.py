from models.db import get_db_connection
from werkzeug.security import generate_password_hash


def seed_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

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

