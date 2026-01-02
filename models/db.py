import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "app.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    print(f"USING DB: {DB_PATH}")
    return conn


def ensure_request_columns():
    """
    Ensures required columns exist on the requests table.
    Safe to run multiple times.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Get existing columns
    cur.execute("PRAGMA table_info(requests)")
    existing_columns = [row["name"] for row in cur.fetchall()]

    # Add priority column if missing
    if "priority" not in existing_columns:
        cur.execute("""
            ALTER TABLE requests
            ADD COLUMN priority TEXT DEFAULT 'medium'
        """)
        print("Added priority column")

    # Add department column if missing
    if "department" not in existing_columns:
        cur.execute("""
            ALTER TABLE requests
            ADD COLUMN department TEXT NOT NULL DEFAULT 'corporate'
        """)
        print("Added department column")

    # Add admin review notes column if missing
    if "admin_review_notes" not in existing_columns:
        cur.execute("""
            ALTER TABLE requests
            ADD COLUMN admin_review_notes TEXT
        """)
        print("Added admin_review_notes column")


    conn.commit()
    conn.close()
