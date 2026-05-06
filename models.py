"""
models.py — Database schema for Vault application.
All sensitive fields (notes content, stored passwords) are stored encrypted.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Registered vault user. Password is always stored as a bcrypt hash."""
    __tablename__ = "users"

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(64),  unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    files     = db.relationship("VaultFile",     backref="owner", lazy=True, cascade="all, delete-orphan")
    notes     = db.relationship("Note",          backref="owner", lazy=True, cascade="all, delete-orphan")
    links     = db.relationship("Link",          backref="owner", lazy=True, cascade="all, delete-orphan")
    passwords = db.relationship("PasswordEntry", backref="owner", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class VaultFile(db.Model):
    """Uploaded file metadata. The actual file lives in the uploads/ folder."""
    __tablename__ = "vault_files"

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename      = db.Column(db.String(256), nullable=False)   # stored name on disk (uuid-based)
    original_name = db.Column(db.String(256), nullable=False)   # original upload name
    file_type     = db.Column(db.String(64),  nullable=False)   # MIME type
    file_size     = db.Column(db.Integer,     nullable=False)   # bytes
    uploaded_at   = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def size_human(self):
        """Return human-readable file size."""
        for unit in ["B", "KB", "MB", "GB"]:
            if self.file_size < 1024:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024
        return f"{self.file_size:.1f} TB"

    @property
    def is_image(self):
        return self.file_type.startswith("image/")

    @property
    def is_video(self):
        return self.file_type.startswith("video/")

    def __repr__(self):
        return f"<VaultFile {self.original_name}>"


class Note(db.Model):
    """Encrypted personal note."""
    __tablename__ = "notes"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title      = db.Column(db.String(256), nullable=False)
    content    = db.Column(db.Text, nullable=False)   # Fernet-encrypted
    tags       = db.Column(db.String(256), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Note {self.title}>"


class Link(db.Model):
    """Saved bookmark / link entry."""
    __tablename__ = "links"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title       = db.Column(db.String(256), nullable=False)
    url         = db.Column(db.Text,        nullable=False)
    description = db.Column(db.Text,        default="")
    tags        = db.Column(db.String(256), default="")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Link {self.title}>"


class PasswordEntry(db.Model):
    """Encrypted password vault entry."""
    __tablename__ = "password_entries"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    site_name   = db.Column(db.String(256), nullable=False)
    site_url    = db.Column(db.String(512), default="")
    username    = db.Column(db.String(256), nullable=False)
    password    = db.Column(db.Text,        nullable=False)  # Fernet-encrypted
    notes       = db.Column(db.Text,        default="")      # Fernet-encrypted
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PasswordEntry {self.site_name}>"
