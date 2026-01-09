from models.db import get_db_connection

print("seed_kb_articles module loaded")


KB_ARTICLES = [
    {
        "title": "How to Request VPN Access",
        "slug": "how-to-request-vpn-access",
        "category": "Access",
        "summary": "Step-by-step guide for requesting remote access credentials",
        "content": """### Overview
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
Contact IT Support or submit a Security request."""
    },

    {
        "title": "Hardware Request Guidelines",
        "slug": "hardware-request-guidelines",
        "category": "Hardware",
        "summary": "What to include when requesting laptops, monitors, or peripherals",
        "content": """### Overview
Use this guide before submitting a hardware request to ensure faster approval and fulfillment.

### What Qualifies as a Hardware Request?
- Laptops or desktop computers
- Monitors, keyboards, mice, and docking stations
- Headsets, webcams, and other peripherals

### Approval Requirements
Most hardware requests require manager approval.

Your request may be delayed or denied if:
- Required justification is missing
- The request duplicates existing assigned equipment
- The item is outside standard company hardware offerings

### What to Include in Your Request
- Requested item(s)
- Business justification
- Urgency level
- Replacement or new equipment
- Any known issues with current hardware

### Standard Fulfillment Timeline
- Review within 1 business day
- Approval within 1–2 business days
- Delivery varies based on availability

### Need Help?
Contact IT Support before submitting your request."""
    },

    {
        "title": "Password Reset Process",
        "slug": "password-reset-process",
        "category": "Security",
        "summary": "How to reset your password and regain access securely",
        "content": """### Overview
If you are unable to access your account due to a forgotten or expired password, follow the steps below to reset your credentials securely.

For security reasons, password resets are handled through approved self-service tools or IT verification.

### When You Should Reset Your Password

You should reset your password if:

- You have forgotten your password
- Your password has expired
- Your account is locked after multiple failed login attempts
- You believe your credentials may have been compromised

### Self-Service Password Reset (Recommended)

Most users can reset their password without contacting IT.

1. Navigate to the company password reset portal
2. Verify your identity using multi-factor authentication (MFA)
3. Create a new password that meets security requirements
4. Log in using your updated credentials

> Password changes typically take effect immediately.

### Password Requirements

New passwords must meet the following criteria:

- Minimum length of 12 characters
- Include a mix of uppercase, lowercase, numbers, and symbols
- Cannot match previous passwords
- Must not include personal or easily guessable information

### If You Are Locked Out

If you cannot access the self-service reset portal:

- Submit a **Security** request from the dashboard
- Be prepared to verify your identity
- IT Support will assist during business hours

### Security Best Practices

To keep your account secure:

- Never share your password with anyone
- Do not reuse passwords from other systems
- Enable MFA on all supported applications
- Report suspicious login activity immediately

### Need Help?
If you continue to experience issues, contact IT Support or submit a Security request through the dashboard."""
    },

    {
        "title": "Software License Requests",
        "slug": "software-license-requests",
        "category": "Software",
        "summary": "Requesting licenses for approved software and tools",
        "content": """### Overview
Use this guide to request licenses for company-approved software and tools required for your role.

Software licenses are managed centrally to ensure compliance, cost control, and security.

### What Requires a Software License?
You may need a license for:

- Productivity tools
- Design or development software
- Security or compliance tools
- Role-specific applications

Free or open-source tools may still require review before use.

### Approval Requirements
Most software license requests require:

- Manager approval
- IT or Security review (for sensitive tools)

Requests may be denied if:

- The software is not approved
- A suitable alternative already exists
- The request lacks business justification

### What to Include in Your Request
To avoid delays, include:

- Software name and version
- Business justification
- Duration of use (temporary or ongoing)
- Any deadlines or urgency
- Whether the license is new or additional

Incomplete requests may be returned for clarification.

### Fulfillment Timeline
- Initial review: 1 business day  
- Approval: 1–3 business days  
- License provisioning: Varies by vendor

Some tools may require procurement approval and additional lead time.

### Before You Submit
Before requesting a license:

- Confirm the software is not already available to you
- Check for approved alternatives
- Ensure the software aligns with company policies

### Need Help?
If you are unsure whether a license is required, contact IT Support before submitting your request."""
    },

    {
        "title": "New Employee Onboarding Checklist",
        "slug": "new-employee-onboarding-checklist",
        "category": "onboarding",
        "summary": "Essential steps for new team members during their first week",
        "content": """### Overview
Welcome! This checklist outlines the essential steps to help new employees get set up and productive during their first week.

Some steps may already be completed depending on your role and start date.

### Day 1: Access & Accounts
Ensure you have access to:

- Company email
- Required internal systems
- Communication tools (chat, calendar, etc.)
- VPN access (if working remotely)

If you cannot log in, submit a Security request immediately.

### Equipment & Workspace
Confirm that you have received:

- Assigned laptop or desktop
- Required peripherals (monitor, keyboard, headset)
- Office access or remote setup instructions

Report any missing or damaged equipment to IT.

### Required Software
You may need access to:

- Role-specific tools
- Productivity software
- Security or compliance applications

Submit Software License Requests if anything is missing.

### Training & Documentation
During your first week, review:

- Company policies and guidelines
- Security awareness training
- Department-specific documentation
- Knowledge Base articles relevant to your role

### Support & Next Steps
If something is missing or unclear:

- Contact your manager
- Reach out to IT Support
- Use the Knowledge Base for self-service guidance

Getting set up correctly helps ensure a smooth start.

### Need Help?
If you experience issues during onboarding, submit the appropriate request through the dashboard or contact IT Support."""
    },
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