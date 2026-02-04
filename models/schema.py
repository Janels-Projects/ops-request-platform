import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app.db")

def create_user_integrations_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_integrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,

            -- Access / capability flags
            csv_export_enabled BOOLEAN DEFAULT 1,
            cloud_export_visible BOOLEAN DEFAULT 1,

            can_export BOOLEAN DEFAULT 1,
            can_view_integration_status BOOLEAN DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)


def create_kb_articles_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kb_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            is_published INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

def create_user_preferences_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,

            -- Notifications
            email_on_approval BOOLEAN DEFAULT 1,
            email_on_denial BOOLEAN DEFAULT 1,
            email_on_status_change BOOLEAN DEFAULT 1,
            email_on_comment BOOLEAN DEFAULT 1,
            daily_digest BOOLEAN DEFAULT 0,

            -- Display
            theme TEXT DEFAULT 'light',
            requests_per_page INTEGER DEFAULT 25,
            default_view TEXT DEFAULT 'list',

            -- Defaults
            default_department TEXT,
            default_priority TEXT DEFAULT 'medium',

            -- Communication
            timezone TEXT DEFAULT 'America/New_York',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # users table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # --- USERS SCHEMA UPGRADES (SAFE) ---
    # This checks existing columns so ALTER TABLE doesn't error.
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]

    if "full_name" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")

    if "department" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN department TEXT")

    if "avatar_url" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")

    # (rest of your tables continue below...)


    # requests table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        request_type TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'medium',
        department TEXT NOT NULL DEFAULT 'corporate',
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        reviewed_by INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
    )
    """)

    # ✅ Supporting tables 
    create_kb_articles_table(conn)
    create_user_preferences_table(conn)
    create_user_integrations_table(conn)

    conn.commit()
    conn.close()

