# CSC2031-Coursework-Task-3-
Creating a Flask application that demonstrates secure database interaction using SQLAlchemy ORM and parameterized queries

Added some styling to practice fronted.
Added some basic scripting for a pop-up to the whole project, 50/50 chance to keep it random. 
Added logging to the project. 

Tried to implement clean coding practices from, Clean code by Robert Cecil Martin

------------------------------------------------------------

running the app:

install the requirements.txt file
navigate to task-3 
reset the database then run the app.py file

python reset_db.py
python run.py


 ------------------------------------------------------------
Dash-board logic with switch statement, requires python 3.10, lamda function workaround in coursework to allow
python version 3.9, AI generation used in front end. 
------------------------------------------------------------

    @main.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        if not session.get('user_id'):
            return redirect(url_for('main.login'))
    
        role = session['role']
        user_id = session['user_id']
    
        # --- ROLE-BASED POST ACCESS (match/case) ---
        match role:
            case 'admin':
                posts = (
                    Post.query
                    .join(User, Post.author)
                    .add_columns(
                        Post.id,
                        Post.title,
                        Post.content,
                        User.username.label('author')
                    )
                    .all()
                )
                mode = 'admin_full'
    
            case 'moderator':
                posts = (
                    db.session.query(
                        Post.id,
                        Post.title,
                        User.username.label('author')
                    )
                    .join(User, Post.author)
                    .all()
                )
                mode = 'mod_limited'
    
            case 'user':
                posts = (
                    Post.query
                    .filter(Post.author_id == user_id)
                    .join(User, Post.author)
                    .add_columns(
                        Post.id,
                        Post.title,
                        Post.content,
                        User.username.label('author')
                    )
                    .all()
                )
                mode = 'user_own'
    
            case _:
                posts = []
                mode = 'unknown'
    
        # --- SECURE RAW SQL SEARCH (POST) ---
        results = None
        if request.method == 'POST' and request.form.get('search'):
            term = request.form.get('search', '').strip()
    
            q = text("""
                SELECT posts.id, posts.title, posts.content, users.username AS author
                FROM posts
                JOIN users ON users.id = posts.author_id
                WHERE posts.title LIKE :term OR posts.content LIKE :term
            """)
    
            params = {"term": f"%{term}%"}
    
            results = db.session.execute(q, params).mappings().all()
    
            # log query audit
            current_app.logger.info(
                "Search executed | ip=%s user_id=%s role=%s sql=%s params=%s",
                request.remote_addr, user_id, role, q.text, params
            )
    
        # render
        return render_template(
            'dashboard.html',
            posts=posts,
            mode=mode,
            results=results
        )
  