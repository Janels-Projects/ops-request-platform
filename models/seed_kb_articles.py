from models.db import get_db_connection
print("seed_kb_articles module loaded")


KB_ARTICLES = [
    {
        "title": "How to Request VPN Access",
        "slug": "how-to-request-vpn-access",
        "category": "Access",
        "summary": "Step-by-step guide for requesting remote access credentials",
        "content": """
### Overview
VPN access allows you to securely connect to company resources from remote locations.

### Who Can Request VPN Access?
- Full-time employees with remote work arrangements
- Contractors requiring access to internal systems
- Employees traveling for business

### Request Process
1. Submit a request from the dashboard
2. Provide location, reason, and duration
3. Manager approval
4. IT review within 24 hours
5. Credentials sent via email

### Need Help?
Contact IT Support or submit a Security request.
"""
    }
]

def seed_kb_articles():
    db = get_db_connection()
    cursor = db.cursor()

    for article in KB_ARTICLES:
        cursor.execute(
            """
            INSERT OR IGNORE INTO kb_articles
            (title, slug, category, summary, content)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                article["title"],
                article["slug"],
                article["category"],
                article["summary"],
                article["content"],
            )
        )

    db.commit()
