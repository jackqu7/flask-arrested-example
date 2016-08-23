import os

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Boolean

from kim.mapper import Mapper
from kim.role import whitelist
from kim import field

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:////opt/code/example.db')

db = SQLAlchemy(app)


class User(db.Model):

    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    name = Column(String)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    company_id = Column(String, db.ForeignKey('company.id'))

    company = db.relationship('Company')


class Company(db.Model):

    __tablename__ = 'company'
    id = Column(String, primary_key=True)
    name = Column(String)


class UserMapper(Mapper):
    __type__ = User

    id = field.String(read_only=True)
    name = field.String()
    password = field.String()
    is_admin = field.Boolean(required=False, default=False)

    __roles__ = {
        'public': whitelist('name', 'id', 'is_admin')
    }


class CompanyMapper(Mapper):
    __type__ = User

    id = field.String(read_only=True)
    name = field.String()

    __roles__ = {
        'public': whitelist('name', 'id')
    }


@app.route('/')
def index():
    return '', 200
