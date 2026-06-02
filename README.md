# ⚡ CareerAI — AI-Powered Career Assistant for CSE Students

> A full-stack web platform that helps Computer Science students optimize their resumes, get AI career guidance, follow structured DSA roadmaps, and prepare for placements — all for free.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 📸 Features

| Feature                  | Description                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| 📄 **ATS Resume Scorer** | Upload PDF/DOCX → instant ATS score (0-100) with keyword, verb, formatting, and contact analysis |
| 🤖 **AI Career Chatbot** | Keyword-based + optional OpenAI GPT career advisor for DSA, SQL, Python, ML roadmaps             |
| 🗺️ **DSA Roadmap**       | Topic-wise learning path, YouTube channels, practice platforms, daily plan                       |
| 📊 **User Dashboard**    | Score history, stats, quick actions, career tips                                                 |
| 🛡️ **Admin Panel**       | Manage DSA resources, view resume metadata, user stats, score distribution                       |

---

## 🗂️ Project Structure

```
career_ai/
│
├── app.py                  # Flask app factory & entry point
├── config.py               # All configuration, env vars, ATS keywords
├── requirements.txt        # Python dependencies
├── Procfile                # Gunicorn deployment command
├── runtime.txt             # Python version for hosting
├── .env.example            # Environment variable template
├── .gitignore
├── README.md
│
├── database/
│   ├── __init__.py
│   └── db.py               # SQLite init, schema, query helpers, seed data
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Register, login, logout (user + admin)
│   ├── user.py             # Dashboard, resume upload, chat, DSA roadmap
│   ├── admin.py            # Admin dashboard, resource/suggestion management
│   └── api.py              # JSON endpoints for AJAX (chat, stats)
│
├── utils/
│   ├── __init__.py
│   ├── resume_parser.py    # PDF + DOCX text extraction
│   ├── ats_scorer.py       # 5-category ATS scoring engine
│   └── chatbot.py          # Keyword-based chatbot + OpenAI fallback
│
├── templates/
│   ├── base.html           # Base layout with navbar, flash messages, footer
│   ├── index.html          # Landing page
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html      # User dashboard
│   ├── resume_upload.html  # Upload form + history
│   ├── resume_result.html  # ATS score breakdown + suggestions
│   ├── chat.html           # Chat interface
│   ├── dsa_roadmap.html    # Tabbed roadmap page
│   ├── profile.html
│   └── admin/
│       ├── login.html
│       ├── dashboard.html
│       ├── resources.html
│       ├── edit_resource.html
│       ├── users.html
│       └── suggestions.html
│
└── static/
    ├── css/
    │   └── style.css       # Full dark-mode design system
    ├── js/
    │   ├── main.js         # Global UI (nav, flash, animations, markdown)
    │   ├── chat.js         # Chat send/receive/render
    │   └── resume.js       # Drag-drop upload, validation, loading
    └── uploads/            # Temporary upload directory (files deleted after analysis)
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.9+
- pip

### 1. Clone & Setup

```bash
git clone https://github.com/PinnamSathwikKumar/CarrerAI.git
cd career_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-strong-secret-key-here
FLASK_DEBUG=True
ADMIN_EMAIL=admin@careerAI.com
ADMIN_PASSWORD=YourStrongPassword
# Optional: Add OpenAI key for GPT chatbot
# OPENAI_API_KEY=sk-...
```

### 3. Run

```bash
python app.py
```

Visit: **http://localhost:5000**

The database is auto-created on first run with seed DSA resources and the default admin account.

---

> **⚠️ Change these immediately** before any production deployment via the `.env` file.

---

## 🤖 AI Chatbot Modes

### Mode 1: Keyword-Based (Default, Free)

Works out of the box with no API keys. Covers:

- DSA roadmap, Python, SQL, System Design, AI/ML
- Resume tips, internship strategies
- Interview preparation

### Mode 2: OpenAI GPT-3.5 (Optional)

Set `OPENAI_API_KEY` in `.env` for more natural, context-aware responses.
Estimated cost: ~$0.002 per conversation (very cheap).


---

## 📊 ATS Scoring Breakdown

| Category     | Points  | What's Checked                     |
| ------------ | ------- | ---------------------------------- |
| Keywords     | 40      | 60+ tech skills, tools, frameworks |
| Action Verbs | 20      | Strong vs weak verb detection      |
| Formatting   | 20      | Headers, bullets, dates, structure |
| Length       | 10      | Optimal word count (300-700 words) |
| Contact Info | 10      | Email, phone, LinkedIn, GitHub     |
| **Total**    | **100** |                                    |

**Grades:** A (85+) • B (70+) • C (55+) • D (40+) • F (<40)

---


## 🗄️ Database Tables

```sql
users          -- Student accounts
admins         -- Admin accounts
resumes        -- Resume metadata + ATS scores (no file stored)
dsa_resources  -- DSA topics, YouTube channels, platforms
suggestions    -- Career tips/suggestions
chat_history   -- Per-user chat messages
```

---

## 🔒 Security Features

- ✅ Passwords hashed with Werkzeug (PBKDF2-SHA256)
- ✅ Session-based authentication (Flask sessions)
- ✅ File type validation (whitelist: PDF, DOCX only)
- ✅ Max file size: 5 MB
- ✅ Secure filename (werkzeug `secure_filename`)
- ✅ Uploaded files deleted immediately after analysis
- ✅ Admin routes protected by separate session key
- ✅ SQL injection prevention via parameterized queries
- ✅ CSRF protection via same-site cookie policy

---

## ⚡ Performance 

- Files deleted immediately after processing
- Gunicorn with 2 sync workers (configurable via `Procfile`)
- No in-memory caching needed (SQLite is fast for this scale)

---

## 🛠️ Tech Stack

| Layer        | Technology                                 |
| ------------ | ------------------------------------------ |
| Backend      | Python 3.11 + Flask 3.0                    |
| PDF Parsing  | pdfplumber + PyPDF2 fallback               |
| DOCX Parsing | python-docx                                |
| AI           | Keyword engine + OpenAI GPT-3.5 (optional) |
| Frontend     | Vanilla HTML, CSS, JavaScript              |
| Fonts        | Space Grotesk + JetBrains Mono             |

---

## 📝 Development Notes

### Adding New Chat Topics

Edit `utils/chatbot.py` → `CAREER_KB` dictionary:

```python
'your_topic': {
    'keywords': ['keyword1', 'keyword2'],
    'response': """Your markdown response here"""
}
```

### Adding New ATS Keywords

Edit `config.py` → `TECH_KEYWORDS` list.

### Adding DSA Resources via Admin Panel

Login at `/admin/login` → Resources → Add Resource

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 💬 Support

- Open an issue on GitHub
- Email: pinnamsathwikkumar@gmail.com

---

_Built with ❤️ for students aiming for their dream jobs._
