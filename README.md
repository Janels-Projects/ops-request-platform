![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-lightgrey)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)
![Status](https://img.shields.io/badge/Status-Active-success)


# Atlas Ops – Internal Operations Request Platform
Atlas Ops is a Flask-based internal operations platform built to model real enterprise request workflows.

**Primary goals:**
- Demonstrate backend-first system design
- Enforce lifecycle state transitions
- Model real internal tooling patterns
---
## Why This Project

This project was built to demonstrate backend engineering skills using patterns commonly found in internal enterprise tools, including:

- Role-based access control
- Backend-enforced state machines
- Derived metrics instead of static counters
- Single-source-of-truth data modeling

## Features

### Authentication & Authorization
- JWT-based authentication stored in **HttpOnly cookies**
- Secure login and logout
- Role-based access control:
  - **Users** submit and track requests
  - **Admins** review, manage, and complete requests
- Global 403 handling for unauthorized access

---

### Request Lifecycle
Requests move through a controlled lifecycle enforced on the backend:

pending → approved → in_progress → completed


---
- Admins can approve or deny pending requests
- Approved requests can be started (work begins)
- In-progress requests can be completed
- Invalid or duplicate transitions are prevented server-side

---
### Request Creation
Users can submit requests with:
- Request type
- Category (Access, Hardware, Software, etc.)
- Department (Corporate, Healthcare, Legal)
- Priority (Low, Medium, High)

---

### Admin Dashboard
- Backend-driven metrics (derived data, not static)
- Pending queue with real-time lifecycle state
- Conditional admin actions based on request status
- Client-side filtering by:
  - Status
  - Category
  - Department
  - Priority
- Metrics include:
  - Pending request count
  - New requests today
  - Average approval time

All dashboard data is driven from a **single source of truth** in the backend.

---

### Architecture
- Flask with Blueprints
- SQLite database
- Safe startup migrations
- Centralized request table
- Clean separation of concerns:
  - `routes/` – application logic
  - `models/` – database and schema
  - `templates/` – server-rendered views
  - `static/` – CSS and JavaScript

---

## Tech Stack
- Python
- Flask
- SQLite
- Jinja2
- HTML / CSS / JavaScript

---

## Project Status
Core backend functionality is complete and stable.

### Planned Enhancements
- User dashboard lifecycle visibility (in-progress / completed)
- Review notes for audit context
- SLA / due date tracking
- Attachments support
- UI polish and documentation improvements

---

## Design Decisions
- UI is intentionally minimal to emphasize backend correctness
- Business rules are enforced server-side (not in templates)
- Metrics are derived from data, not stored


---
## Notable Backend Highlights

- Single `/review` endpoint handling all admin state transitions
- Backend-enforced lifecycle validation (no invalid transitions)
- Metrics derived from live data instead of stored counters
- Unified dataset (`requests`) used for tables and charts


---
## Screenshots
_(Coming soon)_

---

## Author
Built by **Janel** as a backend-focused portfolio project demonstrating production-style internal tooling.
