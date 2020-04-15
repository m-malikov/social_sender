from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
import api_integration
from config import sqlalchemy_url

engine = create_engine(sqlalchemy_url)
models.Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()


def add_user(user_id):
    session.add(models.User(id=user_id))
    session.commit()


def tasks(user_id):
    return session.query(models.Task)\
        .filter(models.Task.user.id == user_id).all()


def task_status(task_id):
    return session.query(models.Post)\
        .filter(models.Post.task.id == task_id).one()


def send_task(user_id, text):
    task = models.Task(user_id=user_id, text=text, datetime=datetime.now())
    session.add(task)
    user = session.query(models.User).filter(models.User.id == user_id).one()
    for token in user.tokens:
        send_post(task.id, token.id)


class UnknownTargetError(ValueError):
    def __init__(self, target_code):
        ValueError.__init__(
            self,
            "Unknown target code: {}".format(target_code)
        )


def send_post(task_id, token_id):
    token = session.query(models.Token)\
        .filter(models.Token.id == token_id).one()
    task = session.query(models.Task)\
        .filter(models.Task.id == task_id).one()
    post = models.Post(
        task_id=task_id,
        id=token_id,
        status_code=models.PostStatus.waiting
    )
    session.add(post)

    try:
        api_integration.send(token.target, task.text, token.value)
    except api_integration.SendError as send_error:
        post.status_code = models.PostStatus.error
        post.error = str(send_error)
    else:
        post.status_code = models.PostStatus.ok
    finally:
        session.add(post)
        session.commit()


def add_token(user_id, target, value):
    session.add(models.Token(user_id=user_id, target=target, value=value))
    session.commit()


def get_tokens(user_id):
    return session.query(models.Token)\
        .filter(models.Token.user_id == user_id).all()
