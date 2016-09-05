import os
import json

from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Boolean, Integer

from kim.mapper import Mapper
from kim.role import whitelist
from kim import field
from kim.exception import MappingInvalid


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:////opt/code/example.db')
app.config['DEBUG'] = True

db = SQLAlchemy(app)


# Models
class User(db.Model):

    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_admin = Column(Boolean, default=False)
    company_id = Column(String, db.ForeignKey('company.id'))

    company = db.relationship('Company')


class Company(db.Model):

    __tablename__ = 'company'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)


# DATABASE WILL BE RECREATED ON EVERY RUN - comment out next 2 lines to stop
db.drop_all()
db.create_all()

# Create default data
c1 = Company(name='Acme')
u1 = User(name='Bob Smith', company=c1)
u2 = User(name='Jane Doe', company=c1)

db.session.add_all([c1, u1])
db.session.commit()


# Kim mappers
class CompanyMapper(Mapper):
    __type__ = Company

    id = field.Integer(read_only=True)
    name = field.String()


def company_getter(session):
    session.data = json.loads(session.data)
    if 'id' in session.data:
        return db.session.query(Company).get(session.data['id'])


class UserMapper(Mapper):
    __type__ = User

    id = field.Integer(read_only=True)
    name = field.String()
    is_admin = field.Boolean(required=False, default=False)
    company = field.Nested(CompanyMapper, getter=company_getter)

    __roles__ = {
        'overview': whitelist('id', 'name')
    }


# Flask views
@app.route('/users/<string:user_id>', methods=['GET', 'PUT', 'PATCH'])
def user_detail(user_id):
    # Retrieve user from DB
    user = db.session.query(User).get(user_id)

    if request.method in ['PUT', 'PATCH']:

        # If this is a PATCH, pass partial
        partial = request.method == 'PATCH'

        # Instatiate the mapper and pass the request data
        mapper = UserMapper(obj=user, data=request.json,
                            partial=partial)

        try:
            # Validate the data and get a new User object back
            user = mapper.marshal()
        except MappingInvalid as e:
            # If data did not validate, return a 400
            return json.dumps(e.errors), 400

        # Save the updated User object
        db.session.add(user)
        db.session.commit()

    # Create an instance of UserMapper
    mapper = UserMapper(obj=user)

    # Get a python dict representing the user
    serialised = mapper.serialize()

    # Convert it to json and return it as the response
    return json.dumps(serialised), 200


@app.route('/users', methods=['GET', 'POST'])
def user_list():
    if request.method == 'POST':
        # Instatiate the mapper and pass the request data.
        # Do not pass an obj - causes a new User to be created
        mapper = UserMapper(data=request.json)

        try:
            # Validate the data and get a new User object back
            user = mapper.marshal()
        except MappingInvalid as e:
            # If data did not validate, return a 400
            return json.dumps(e.errors), 400

        # Save the updated User object
        db.session.add(user)
        db.session.commit()

        # Now serialise it and return it
        mapper = UserMapper(obj=user)
        serialised = mapper.serialize()

        # Convert it to json and return it as the response
        return json.dumps(serialised), 200

    else:
        # Retrieve all users from DB
        users = db.session.query(User).all()

        # Create a many-instance of UserMapper
        mapper = UserMapper.many()

        # Get a list of dicts representing each user in overview role
        serialised = mapper.serialize(users, role='overview')

        # Convert it to json and return it as the response
        return json.dumps(serialised), 200


@app.route('/')
def index():
    return '', 200
