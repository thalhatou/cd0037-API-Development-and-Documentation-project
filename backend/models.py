import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))


DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT=  os.getenv('DB_PORT',5432)
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '7y8a1h64')
DB_NAME = os.getenv('DB_NAME', 'trivia')

DATABASE_PATH = "postgresql://{}:{}@{}:{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, DATABASE_PATH=DATABASE_PATH):
    app.config["SQLALCHEMY_DATABASE_URI"] =DATABASE_PATH
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

"""
Question

"""
class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        status = True
        id = None
        try:
            db.session.add(self)
            db.session.commit()
            id = self.id
        except:
            db.session.rollback()
            status = False
        finally:
            db.session.close()
        return {"status": status, "id": id}

    def update(self):
        db.session.commit()

    def delete(self):
        status = True
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
            status = False
        finally:
            db.session.close()
        return status

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
            }

"""
Category

"""
class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
            }
