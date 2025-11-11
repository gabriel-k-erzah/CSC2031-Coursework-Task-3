from . import db
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey, Integer


#--------------------------------------------- user name class ---------------------------------------------------------
class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)  # (plain for task)
    role: Mapped[str] = mapped_column(String(16), nullable=False)       # 'admin'|'moderator'|'user'
    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all,delete")

#--------------------------------------------- post class --------------------------------------------------------------
class Post(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped[User] = relationship(back_populates="posts")

def seed_data(db):
    from .models import User, Post
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@example.com', password='admin123', role='admin')
        moderator = User(username='mod1', email='mod1@example.com', password='mod123', role='moderator')
        user1 = User(username='user1', email='user1@example.com', password='user123', role='user')
        user2 = User(username='user2', email='user2@example.com', password='user456', role='user')
        db.session.add_all([admin, moderator, user1, user2])
        db.session.commit()
    if Post.query.count() == 0:
        posts = [
            Post(title='Welcome Post', content='This is the first post.', author_id=1),
            Post(title='Moderator Update', content='Moderator insights here.', author_id=2),
            Post(title='User Thoughts', content='User1 shares ideas.', author_id=3),
            Post(title='Another User Post', content='User2 contributes.', author_id=4)
        ]
        db.session.add_all(posts)
        db.session.commit()