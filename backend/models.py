import os
from sqlalchemy import Column, String, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
from flask import jsonify
from flask_migrate import Migrate

from datetime import datetime
from dateutil.relativedelta import relativedelta

from roles_and_status import ForumRoles, UserStatus




database_path = os.environ['DATABASE_URL']
if database_path.startswith("postgres://"):
  database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


# '''
# Person
# Have title and release year
# '''
# class Person(db.Model):  
#   __tablename__ = 'People'

#   id = Column(db.Integer, primary_key=True)
#   name = Column(String)
#   catchphrase = Column(String)

#   def __init__(self, name, catchphrase=""):
#     self.name = name
#     self.catchphrase = catchphrase

#   def format(self):
#     return {
#       'id': self.id,
#       'name': self.name,
#       'catchphrase': self.catchphrase}

class Forum(db.Model):
    __tablename__ = 'forums'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(36), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    threads = db.relationship('Thread', backref=db.backref('forums'), lazy=True, cascade='all, delete')

    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
        
    def format_threads(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'threads': self.threads
        }

    # def __repr__(self):
    #     return jsonify({ 
    #         'id': self.id,
    #         'name': self.name,
    #         'description': self.description
    #     })

class Thread(db.Model):
    __tablename__ = 'threads'

    id = db.Column(db.Integer, primary_key=True)
    forum_id = db.Column(db.Integer, db.ForeignKey('forums.id'))
    title = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.String(), db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    pages = db.relationship('Page', backref=db.backref('threads'), lazy=True, cascade="all, delete")
    locked = db.Column(db.Boolean, default=False)

    def lock_thread(self):
        self.locked = True

    def unlock_thread(self):
        self.locked = False

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete()
        db.session.commit()

    def format(self):
        return {
            'forumId': self.forum_id,
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'dateCreated': self.date_created,
            'pages': len(self.pages),
            'locked': self.locked
        }
    
    def get_page_posts(self, page_number):
        return {
            'forumId': self.forum_id,
            'id': self.id,
            'title': self.title,
            'dateCreated': self.date_created,
            'posts': [post.format() for post in self.pages[page_number - 1].posts],
            'locked': self.locked
        }
    



class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(), db.ForeignKey('users.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'))
    content = db.Column(db.String(1024), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    date_edited = db.Column(db.DateTime)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        self.content = 'This post has been deleted.'
        self.date_edited = datetime.utcnow()
        self.update()

    def format(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'page_id': self.page_id,
            'content': self.content,
            'dateCreated': self.date_created,
            'dateEdited': self.date_edited
        }

class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'))
    page_number = db.Column(db.Integer)
    posts = db.relationship('Post', backref=db.backref('pages', uselist=False), order_by='posts.columns.date_created')

    def insert(self):
        db.session.add(self)
        db.session.commit() 

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String(36), nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow())
    posts = db.relationship('Post', backref=db.backref('users'), lazy=True)
    # role = db.Column(db.String(), nullable=False, default=ForumRoles.USER)
    role = db.Column(db.String(), nullable=False, default='USER')
    # status = db.Column(db.String(), nullable=False, default=UserStatus.NORMAL)
    status = db.Column(db.String(), nullable=False, default='NORMAL')
    probation_start_date = db.Column(db.DateTime)
    probation_end_date = db.Column(db.DateTime)

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'status': self.status,
            'probationStartDate': self.probation_start_date or '',
            'probationEndDate': self.probation_end_date or ''
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def set_role(self, new_role):
        status = 'FAILED'
        if new_role != self.role and new_role in ForumRoles.__members__:
            self.role = new_role
            status = 'SUCCESS'
        return status
    
    def set_status(self, new_status):
        status = 'FAILED'
        if new_status != self.status and new_status in UserStatus.__members__:
            self.status = new_status
            status = 'SUCCESS'
        return status
    
    def set_probation(self, probation_time):
        status = 'FAILED'
        hours = 0
        days = 0
        months = 0
        if probation_time == '1 HOUR':
            hours = 1
        if probation_time == '2 HOURS':
            hours = 2
        if probation_time == '6 HOURS':
            hours = 6
        if probation_time == '12 HOURS':
            hours = 12
        if probation_time == '1 DAY':
            days = 1
        if probation_time == '3 DAYS':
            days = 3
        if probation_time == '1 WEEK':
            days = 7
        if probation_time == '2 WEEKS':
            days = 14
        if probation_time == '1 MONTH':
            months = 1
        if probation_time == '2 MONTHS':
            months = 2
        if probation_time == '3 MONTHS':
            months = 3
        if probation_time == '6 MONTHS':
            months = 6
        if hours or days or months:
            self.probation_start_date = datetime.utcnow()
            self.probation_end_date = self.probation_start_date + relativedelta(hours=hours, days=days, months=months)
            status = 'SUCCESS'
        return status
