from models.db import get_db_connection

def seed_request():
    conn = get_db_connection()
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO requests (user_id, request_type, category, status)
        VALUES (?, ?, ?, ?)
    """, (
        1,
        "VPN Access",
        "Access",
        "pending"
    ))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_request()
