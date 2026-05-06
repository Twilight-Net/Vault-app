# 🔐 Personal Vault — Secure Cloud Storage + Password Manager

A full-stack personal cloud vault built with **Flask + SQLite**. Store files, encrypted notes, bookmarks, and passwords behind a secure login.

---

## ✨ Features

| Feature | Details |
|---|---|
| Authentication | Signup / Login / Logout with **bcrypt**-hashed passwords |
| Files | Upload up to **50 MB**, image/video/doc/archive types, drag-drop UI |
| Notes | **Fernet-encrypted** (AES-128) notes with tag filtering |
| Links | Bookmark manager with favicon preview, tags, descriptions |
| Passwords | **Fernet-encrypted** vault with copy-to-clipboard, reveal, and built-in password generator |
| Search | Global vault search across all content types |
| Security | CSRF protection, XSS headers, `HttpOnly` session cookies, file type validation |

---

## 🚀 Quick Start

### 1. Clone / extract the project

```bash
cd vault
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If `python-magic` fails on Windows, install [python-magic-bin](https://pypi.org/project/python-magic-bin/) instead:
> ```bash
> pip install python-magic-bin
> ```

### 4. (Optional) Set environment variables

```bash
export SECRET_KEY="your-flask-secret-key-change-me"
export VAULT_FERNET_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

If you skip this, a random key is generated on first run and saved to `.vault_key`. **Back up `.vault_key`** — losing it means encrypted data is unrecoverable.

### 5. Run the server

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 📁 Project Structure

```
vault/
├── app.py                  # Flask app factory + entry point
├── models.py               # SQLAlchemy models (User, VaultFile, Note, Link, PasswordEntry)
├── requirements.txt
├── .vault_key              # Auto-generated Fernet encryption key (keep secret!)
├── vault.db                # SQLite database (auto-created)
│
├── routes/
│   ├── auth.py             # Signup, login, logout
│   ├── dashboard.py        # Overview + global search API
│   ├── files.py            # File upload, download, delete, preview
│   ├── notes.py            # Encrypted notes CRUD
│   ├── links.py            # Bookmarks CRUD
│   └── passwords.py        # Encrypted password vault CRUD
│
├── utils/
│   ├── crypto.py           # Fernet encrypt/decrypt helpers
│   └── security.py         # File validation helpers
│
├── templates/
│   ├── base.html           # Layout with sidebar + nav
│   ├── auth/
│   │   ├── login.html
│   │   └── signup.html
│   └── dashboard/
│       ├── index.html      # Overview / stats
│       ├── files.html      # File manager
│       ├── notes.html      # Notes list
│       ├── note_form.html  # Create / edit note
│       ├── note_view.html  # View decrypted note
│       ├── links.html      # Bookmark manager
│       └── passwords.html  # Password vault
│
├── static/
│   ├── css/style.css       # Dark vault UI theme
│   └── js/main.js          # Search, sidebar toggle, utilities
│
└── uploads/                # Uploaded files (UUID-named, secure)
```

---

## 🔒 Security Notes

- **Never commit `.vault_key` or `vault.db`** to version control. Add them to `.gitignore`.
- In production, set `SESSION_COOKIE_SECURE = True` and run behind HTTPS (e.g. Nginx + Let's Encrypt).
- The encryption key (`VAULT_FERNET_KEY`) is the root secret — store it in a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.) for production use.
- File uploads are stored with UUID names; originals never touch disk under their original name.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/files/api/list` | JSON list of your files |
| GET | `/notes/api/list` | JSON list of note titles |
| GET | `/links/api/list` | JSON list of bookmarks |
| GET | `/passwords/api/list` | JSON list of password entries (no passwords) |
| GET | `/passwords/<id>/reveal` | Decrypt and return a password (auth required) |
| GET | `/search?q=<query>` | Global search across all vault content |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| Flask | Web framework |
| Flask-Login | Session management |
| Flask-SQLAlchemy | ORM + SQLite |
| Flask-WTF | CSRF protection |
| bcrypt | Password hashing |
| cryptography | Fernet AES encryption |
| Pillow | Image processing |
| python-magic | MIME type detection |
| Werkzeug | File security utilities |
