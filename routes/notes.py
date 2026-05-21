"""
routes/notes.py — Encrypted notes CRUD.
Content is encrypted with Fernet before DB write and decrypted on read.
"""

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify)
from flask_login import login_required, current_user
from models import db, Note
from utils.crypto import encrypt, decrypt

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


@notes_bp.route("/")
@login_required
def index():
    tag   = request.args.get("tag", "")
    query = Note.query.filter_by(user_id=current_user.id)
    if tag:
        query = query.filter(Note.tags.contains(tag))
    all_notes = query.order_by(Note.updated_at.desc()).all()

    # Collect all unique tags for filter UI
    all_tags = set()
    for n in Note.query.filter_by(user_id=current_user.id).all():
        for t in n.tags.split(","):
            t = t.strip()
            if t:
                all_tags.add(t)

    return render_template("dashboard/notes.html",
                           notes=all_notes,
                           all_tags=sorted(all_tags),
                           active_tag=tag)


@notes_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        title   = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        tags    = request.form.get("tags", "").strip()

        if not title:
            flash("Title is required.", "danger")
            return render_template("dashboard/note_form.html", note=None)

        note = Note(
            user_id=current_user.id,
            title=title,
            content=encrypt(content),
            tags=tags
        )
        db.session.add(note)
        db.session.commit()
        flash("Note saved.", "success")
        return redirect(url_for("notes.index"))

    return render_template("dashboard/note_form.html", note=None)


@notes_bp.route("/<int:note_id>")
@login_required
def view(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    decrypted_content = decrypt(note.content)
    return render_template("dashboard/note_view.html",
                           note=note,
                           content=decrypted_content)


@notes_bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        note.title   = request.form.get("title", "").strip()
        content      = request.form.get("content", "").strip()
        note.content = encrypt(content)
        note.tags    = request.form.get("tags", "").strip()
        db.session.commit()
        flash("Note updated.", "success")
        return redirect(url_for("notes.view", note_id=note.id))

    # Decrypt for form pre-fill
    note_plain = {
        "id": note.id,
        "title": note.title,
        "content": decrypt(note.content),
        "tags": note.tags,
    }
    return render_template("dashboard/note_form.html", note=note_plain)


@notes_bp.route("/<int:note_id>/delete", methods=["POST"])
@login_required
def delete(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted.", "success")
    return redirect(url_for("notes.index"))


# ── API ─────────────────────────────────────────────────────────────────────

@notes_bp.route("/api/list")
@login_required
def api_list():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated_at.desc()).all()
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "tags": n.tags,
        "updated_at": n.updated_at.isoformat()
    } for n in notes])
