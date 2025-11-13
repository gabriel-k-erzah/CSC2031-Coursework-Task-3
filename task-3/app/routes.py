from flask import (
    Blueprint, render_template, request, flash,
    redirect, url_for, current_app, session
)
from sqlalchemy import text
from . import db
from .models import User, Post

main = Blueprint('main', __name__)

# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------
@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username', '').strip()
        pwd = request.form.get('password', '')

        user = User.query.filter(User.username == uname).first()

        if not user or user.password != pwd:
            current_app.logger.warning(
                "Failed login | ip=%s username=%s",
                request.remote_addr, uname
            )
            flash("Invalid credentials.")
            return render_template('login.html')

        # success
        session['user_id'] = user.id
        session['role'] = user.role

        current_app.logger.info(
            "Login success | ip=%s user_id=%s role=%s",
            request.remote_addr, user.id, user.role
        )
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')


# ------------------------------------------------------------
# DASHBOARD + ROLE LOGIC + SECURE SEARCH (Python 3.9 friendly)
# ------------------------------------------------------------
@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # require login
    if not session.get('user_id'):
        return redirect(url_for('main.login'))

    role = session.get('role')
    user_id = session.get('user_id')

    # ----- ROLE-BASED POST ACCESS USING LAMBDA DISPATCH -----
    role_handlers = {
        "admin": lambda: (
            Post.query
            .join(User, Post.author)
            .add_columns(
                Post.id,
                Post.title,
                Post.content,
                User.username.label('author')
            )
            .all(),
            "admin_full"
        ),

        "moderator": lambda: (
            db.session.query(
                Post.id,
                Post.title,
                User.username.label('author')
            )
            .join(User, Post.author)
            .all(),
            "mod_limited"
        ),

        "user": lambda: (
            Post.query
            .filter(Post.author_id == user_id)
            .join(User, Post.author)
            .add_columns(
                Post.id,
                Post.title,
                Post.content,
                User.username.label('author')
            )
            .all(),
            "user_own"
        ),
    }

    posts, mode = role_handlers.get(role, lambda: ([], "unknown"))()

    # ----- SECURE RAW SQL SEARCH (BOUND PARAMS) -----
    results = None
    if request.method == "POST" and request.form.get("search"):
        term = request.form.get("search", "").strip()

        base_sql = """
                   SELECT posts.id,
                          posts.title,
                          posts.content,
                          users.username AS author
                   FROM posts
                            JOIN users ON users.id = posts.author_id
                   WHERE (posts.title LIKE :term OR posts.content LIKE :term) \
                   """

        params = {"term": f"%{term}%"}

        # extra restriction for normal users
        if role == "user":
            base_sql += " AND users.id = :uid"
            params["uid"] = user_id

        # (optional) if you ever want to restrict mods differently, do it here too

        q = text(base_sql)
        results = db.session.execute(q, params).mappings().all()

        current_app.logger.info(
            "Search executed | ip=%s user_id=%s role=%s sql=%s params=%s",
            request.remote_addr, user_id, role, q.text, params
        )

    # render dashboard
    return render_template(
        'dashboard.html',
        posts=posts,
        mode=mode,
        results=results
    )


# ------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------
@main.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('main.login'))