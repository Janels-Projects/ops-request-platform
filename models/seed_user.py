from werkzeug.security import generate_password_hash
from models.db import get_db_connection


def seed_user():
    conn = get_db_connection()
    cursor = conn.cursor()

    password_hash = generate_password_hash("user123")

    cursor.execute(
        """
        INSERT INTO users (email, password, role)
        VALUES (?, ?, ?)
        """,
        ("user@example.com", password_hash, "user")
    )

    conn.commit()
    conn.close()

    print("✅ Normal user created")
