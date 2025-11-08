# 🎟️ ICT Directorate Job Ticketing System

[![Built with Django](https://img.shields.io/badge/Built%20with-Django-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white)](https://render.com/)
[![Redis](https://img.shields.io/badge/WebSockets-Redis-D82C20?logo=redis&logoColor=white)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A web-based **ICT Support Ticketing System** designed for the **Redeemer’s University ICT Directorate**.  
It enables students and staff to submit, manage, and track ICT-related requests — while administrators oversee and assign tickets efficiently.

---

## 🚀 Features

- User registration and authentication  
- Role-based access control (**Admin**, **Staff**, **Student**)  
- Automatic role detection based on ID and department from a Google Drive CSV  
- Ticket creation, assignment, and progress tracking  
- Real-time WebSocket notifications  
- Comment and feedback system  
- Admin dashboard for user and ticket management  
- Responsive UI built with **Bootstrap**  

---

## ⚙️ Tech Stack

| Component | Technology |
|------------|-------------|
| Framework | Django 4.2, Django Channels |
| Database | SQLite (local) / Render Postgres (optional) |
| Frontend | HTML, CSS, Bootstrap |
| WebSockets | Redis + Channels |
| Deployment | Render |
| External Data | Google Drive CSV integration |

---

## 🧩 How It Works

### 1️⃣ Registration & Role Assignment

```mermaid
flowchart TD
    A[User opens Register page] --> B[Enter ID NUMBER + details]
    B --> C[Server loads CSV from Google Drive]
    C -->|Find row where ID NUMBER matches| D{Match found?}
    D -- No --> E[Show error: ID not found]
    D -- Yes --> F[Read FIRST NAME, LAST NAME, DEPARTMENT]
    F --> G{DEPARTMENT == DICT?}
    G -- Yes --> H[role = staff]
    G -- No --> I[role = student]
    H --> J[Create User + UserProfile]
    I --> J[Create User + UserProfile]
    J --> K[Redirect to Login]
```

**Notes**

* The system fetches the user data dynamically from Google Drive (CSV).
* The form auto-fills first name, last name, and department.
* If the department is **DICT**, the role is set to **staff**; otherwise, **student**.
* Admins are created manually as superusers.

---

### 2️⃣ Ticket Lifecycle

```mermaid
flowchart LR
    A[User creates ticket] --> B[Ticket saved - pending]
    B --> C{Admin assigns staff?}
    C -- Yes --> D[Status = assigned]
    D --> E[Staff starts work → In Progress]
    E --> F[Staff resolves → Resolved]
    F --> G[Admin/Staff closes → Closed]
    C -- No --> B
```

**Notes**

* Students: view and track only their tickets.
* Staff: see tickets assigned to them.
* Admins: view and manage all tickets.

---

### 3️⃣ Real-time Notifications

```mermaid
sequenceDiagram
    participant Client as Browser
    participant Django as Django Views
    participant Channels as Channels Layer
    participant Redis as Redis
    Client->>Django: Create/Update Ticket (HTTP)
    Django->>Channels: group_send("notifications", payload)
    Channels->>Redis: Publish event
    Redis-->>Channels: Fan-out to group
    Channels-->>Client: WebSocket message (ticket_notification)
```

**Triggered when:**

* Ticket is created
* Status is updated
* Ticket is assigned

**Tech used:**

* ASGI via `daphne`
* `channels_redis` for WebSockets
* `ws/notifications/` route for live updates

---

## 🛠️ Installation (Local Setup)

```bash
# 1. Clone repository
git clone https://github.com/YourUsername/ticketing-system-backend.git
cd ticketing-system-backend

# 2. Create a new Conda environment
conda create -n ticketingenv python=3.11

# 3. Activate the environment
conda activate ticketingenv

# 4. Install dependencies
pip install -r requirements.txt

# 5. Apply migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

---

## 🌐 Deployment on Render

* Uses **Daphne** as ASGI server
* **Redis** via external service (e.g. Redis Cloud or Upstash)
* **WhiteNoise** for static file serving

### Environment Variables

| Key                 | Description                |
| ------------------- | -------------------------- |
| `DJANGO_SECRET_KEY` | Your Django secret key     |
| `REDIS_URL`         | Your Redis connection URL  |
| `PYTHON_VERSION`    | Python version (e.g. 3.13.2) |

---

## 👥 Contributors

| Name                      | Role                             |
| ------------------------- | -------------------------------- |
| **Tomide Stephen Ayoola** | Backend Developer / Project Lead |
| **Joanne Atinuke Mcewen** | Frontend Developer / Project Lead|
| **DICT Directorate**      | Institutional Partners           |

---

## 🧾 License

**MIT License © 2025 Tomide Stephen Ayoola & Joanne Atinuke Mcewen**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.


