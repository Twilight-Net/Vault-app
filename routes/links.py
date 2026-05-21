"""
routes/links.py — Bookmarks / saved links CRUD.
"""

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify)
from flask_login import login_required, current_user
from models import db, Link

links_bp = Blueprint("links", __name__, url_prefix="/links")


@links_bp.route("/")
@login_required
def index():
    tag   = request.args.get("tag", "")
    query = Link.query.filter_by(user_id=current_user.id)
    if tag:
        query = query.filter(Link.tags.contains(tag))
    all_links = query.order_by(Link.created_at.desc()).all()

    all_tags = set()
    for lk in Link.query.filter_by(user_id=current_user.id).all():
        for t in lk.tags.split(","):
            t = t.strip()
            if t:
                all_tags.add(t)

    return render_template("dashboard/links.html",
                           links=all_links,
                           all_tags=sorted(all_tags),
                           active_tag=tag)


@links_bp.route("/new", methods=["POST"])
@login_required
def new():
    title       = request.form.get("title", "").strip()
    url         = request.form.get("url", "").strip()
    description = request.form.get("description", "").strip()
    tags        = request.form.get("tags", "").strip()

    if not title or not url:
        flash("Title and URL are required.", "danger")
        return redirect(url_for("links.index"))

    # Prepend https if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    link = Link(user_id=current_user.id, title=title, url=url,
                description=description, tags=tags)
    db.session.add(link)
    db.session.commit()
    flash("Link saved.", "success")
    return redirect(url_for("links.index"))


@links_bp.route("/<int:link_id>/edit", methods=["POST"])
@login_required
def edit(link_id):
    link = Link.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    link.title       = request.form.get("title", link.title).strip()
    link.url         = request.form.get("url", link.url).strip()
    link.description = request.form.get("description", "").strip()
    link.tags        = request.form.get("tags", "").strip()
    db.session.commit()
    flash("Link updated.", "success")
    return redirect(url_for("links.index"))


@links_bp.route("/<int:link_id>/delete", methods=["POST"])
@login_required
def delete(link_id):
    link = Link.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    db.session.delete(link)
    db.session.commit()
    flash("Link deleted.", "success")
    return redirect(url_for("links.index"))


# ── API ─────────────────────────────────────────────────────────────────────

@links_bp.route("/api/list")
@login_required
def api_list():
    links = Link.query.filter_by(user_id=current_user.id).order_by(Link.created_at.desc()).all()
    return jsonify([{
        "id": lk.id, "title": lk.title,
        "url": lk.url, "tags": lk.tags,
        "created_at": lk.created_at.isoformat()
    } for lk in links])
