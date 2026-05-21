"""
routes/passwords.py — Encrypted password vault CRUD.
Passwords are encrypted at rest; revealed only on explicit reveal request.
"""

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify)
from flask_login import login_required, current_user
from models import db, PasswordEntry
from utils.crypto import encrypt, decrypt

passwords_bp = Blueprint("passwords", __name__, url_prefix="/passwords")


@passwords_bp.route("/")
@login_required
def index():
    query = PasswordEntry.query.filter_by(user_id=current_user.id)
    all_entries = query.order_by(PasswordEntry.site_name.asc()).all()
    return render_template("dashboard/passwords.html", entries=all_entries)


@passwords_bp.route("/new", methods=["POST"])
@login_required
def new():
    site_name = request.form.get("site_name", "").strip()
    site_url  = request.form.get("site_url", "").strip()
    username  = request.form.get("username", "").strip()
    password  = request.form.get("password", "")
    notes     = request.form.get("notes", "").strip()

    if not site_name or not username or not password:
        flash("Site name, username, and password are required.", "danger")
        return redirect(url_for("passwords.index"))

    entry = PasswordEntry(
        user_id=current_user.id,
        site_name=site_name,
        site_url=site_url,
        username=username,
        password=encrypt(password),
        notes=encrypt(notes) if notes else ""
    )
    db.session.add(entry)
    db.session.commit()
    flash("Password entry saved.", "success")
    return redirect(url_for("passwords.index"))


@passwords_bp.route("/<int:entry_id>/edit", methods=["POST"])
@login_required
def edit(entry_id):
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    entry.site_name = request.form.get("site_name", entry.site_name).strip()
    entry.site_url  = request.form.get("site_url", "").strip()
    entry.username  = request.form.get("username", entry.username).strip()

    new_pass = request.form.get("password", "")
    if new_pass:
        entry.password = encrypt(new_pass)

    notes = request.form.get("notes", "").strip()
    entry.notes = encrypt(notes) if notes else ""

    db.session.commit()
    flash("Entry updated.", "success")
    return redirect(url_for("passwords.index"))


@passwords_bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete(entry_id):
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted.", "success")
    return redirect(url_for("passwords.index"))


@passwords_bp.route("/<int:entry_id>/reveal")
@login_required
def reveal(entry_id):
    """Return the decrypted password via JSON (used by JS clipboard copy)."""
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    return jsonify({"password": decrypt(entry.password)})


@passwords_bp.route("/<int:entry_id>/reveal_notes")
@login_required
def reveal_notes(entry_id):
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    return jsonify({"notes": decrypt(entry.notes)})


# ── API ─────────────────────────────────────────────────────────────────────

@passwords_bp.route("/api/list")
@login_required
def api_list():
    entries = PasswordEntry.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": e.id,
        "site": e.site_name,
        "username": e.username,
        "url": e.site_url,
        "updated_at": e.updated_at.isoformat()
    } for e in entries])
