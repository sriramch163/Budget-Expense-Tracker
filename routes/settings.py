import os, uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import User, Category
from forms import ProfileForm, ChangePasswordForm, AvatarForm
from app import db

settings_bp = Blueprint("settings", __name__)

UPLOAD_FOLDER = os.path.join("static", "avatars")

def _save_avatar(file):
    os.makedirs(os.path.join(current_app.root_path, UPLOAD_FOLDER), exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
    return f"avatars/{filename}"

@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def index():
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    profile_form = ProfileForm(obj=current_user)
    profile_form.default_category_id.choices = [(0, "— None —")] + [(c.id, c.name) for c in categories]
    pw_form = ChangePasswordForm()
    avatar_form = AvatarForm()

    if "save_profile" in request.form and profile_form.validate_on_submit():
        new_username = profile_form.username.data.strip()
        new_email    = profile_form.email.data.strip().lower()
        if new_username != current_user.username and User.query.filter_by(username=new_username).first():
            flash("Username already taken.", "danger")
        elif new_email != current_user.email and User.query.filter_by(email=new_email).first():
            flash("Email already in use.", "danger")
        else:
            current_user.username = new_username
            current_user.email    = new_email
            current_user.currency = profile_form.currency.data
            cat_id = profile_form.default_category_id.data
            current_user.default_category_id = cat_id if cat_id else None
            db.session.commit()
            flash("Profile updated.", "success")
        return redirect(url_for("settings.index"))

    if "change_password" in request.form and pw_form.validate_on_submit():
        if not current_user.check_password(pw_form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(pw_form.new_password.data)
            db.session.commit()
            flash("Password changed successfully.", "success")
        return redirect(url_for("settings.index"))

    if "upload_avatar" in request.form and avatar_form.validate_on_submit():
        if current_user.avatar:
            old = os.path.join(current_app.root_path, "static", current_user.avatar)
            if os.path.exists(old):
                os.remove(old)
        current_user.avatar = _save_avatar(avatar_form.avatar.data)
        db.session.commit()
        flash("Profile picture updated.", "success")
        return redirect(url_for("settings.index"))

    # Pre-fill default_category_id
    profile_form.default_category_id.data = current_user.default_category_id or 0
    return render_template("settings.html",
        profile_form=profile_form, pw_form=pw_form, avatar_form=avatar_form)
