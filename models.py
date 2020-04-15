from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sqa
import enum

from supported_networks import SupportedNetworks

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sqa.Column(sqa.Integer, primary_key=True)
    vk_key = sqa.Column(sqa.String)
    tasks = sqa.orm.relationship("Task")
    tokens = sqa.orm.relationship("Token")


class Task(Base):
    __tablename__ = "tasks"

    id = sqa.Column(sqa.Integer, primary_key=True)
    user_id = sqa.Column(sqa.Integer, sqa.ForeignKey("users.id"))
    user = sqa.orm.relationship("User", back_populates="tasks")
    text = sqa.Column(sqa.String, nullable=False)
    datetime = sqa.Column(sqa.DateTime, nullable=False)
    posts = sqa.orm.relationship("Post")


class PostStatus(enum.Enum):
    ok = 0
    waiting = 1
    error = 2


class Post(Base):
    __tablename__ = "posts"

    id = sqa.Column(sqa.Integer, primary_key=True)
    task_id = sqa.Column(sqa.Integer, sqa.ForeignKey("tasks.id"))
    task = sqa.orm.relationship("Task", back_populates="posts")
    token_id = sqa.Column(sqa.Integer, sqa.ForeignKey("tokens.id"))
    status_code = sqa.Column(sqa.Enum(PostStatus), nullable=False)
    error = sqa.Column(sqa.Enum(PostStatus), nullable=True)


class Token(Base):
    __tablename__ = "tokens"

    id = sqa.Column(sqa.Integer, primary_key=True)
    user_id = sqa.Column(sqa.Integer, sqa.ForeignKey("users.id"))
    user = sqa.orm.relationship("User", back_populates="tokens")
    target = sqa.Column(sqa.Enum(SupportedNetworks), nullable=False)
    value = sqa.Column(sqa.String, nullable=False)
