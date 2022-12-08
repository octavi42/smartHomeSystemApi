import flask_sqlalchemy, os, time, wtforms
from operator import methodcaller
from os import name
from flask import Flask, json, request, jsonify
from flask.helpers import flash
from flask.views import MethodView
from flask_restful import Resource, Api
from marshmallow import fields
from marshmallow.schema import Schema
from sqlalchemy.orm import backref, defaultload
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_marshmallow import Marshmallow
# from dotenv import load_dotenv

app = Flask(__name__)
api = Api(app)

# s3 = S3Connection(os.environ['S3_KEY'], os.environ['S3_SECRET'])

# load_dotenv()

# DB_NAME = os.getenv("USER")
# DB_PASSWORD = os.getenv("PSSW")
# DB_IP = os.getenv("IP")
# DB_DATABASE = os.getenv("DB")

# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_NAME}:{DB_PASSWORD}@{DB_IP}/{DB_DATABASE}'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('CLEARDB_DATABASE_URL')


db = SQLAlchemy(app)
ma = Marshmallow(app)


    # type = db.relationship('Type', backref='things')
    
    # def __repr__(self):
    #     return '<Name %r>' % self.name


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    smar_thing = db.relationship("Smarthing", backref="parents")

class Smarthing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    name = db.Column(db.String(50), nullable=False)
    online = db.Column(db.Boolean, nullable=False, default=False)
    is_on = db.Column(db.Boolean, nullable=False, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    states = db.relationship("States", backref="parent", uselist=False)

class States(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smarthing_id = db.Column(db.Integer, db.ForeignKey('smarthing.id'))
    corrupt = db.Column(db.Boolean, default=False)
    corrupt_mess = db.Column(db.String(50), default="no problem")
    alarm = db.Column(db.Boolean, nullable=True, default=False)
    color = db.Column(db.String(50), nullable=True)



class StatesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = States
        load_instance = True
        sqla_session = db.session

    id = ma.auto_field()
    smarthing_id = ma.auto_field()
    corrupt = ma.auto_field()
    corrupt_mess = ma.auto_field()
    alarm = ma.auto_field()
    color = ma.auto_field()

session_schema = StatesSchema()
sessions_schema = StatesSchema(many=True)


class StatesSchemaIMP(ma.SQLAlchemySchema):
    class Meta:
        model = States
        load_instance = True
        sqla_session = db.session

    corrupt = ma.auto_field()
    corrupt_mess = ma.auto_field()
    alarm = ma.auto_field()

session_schema = StatesSchema()
sessions_schema = StatesSchema(many=True)


class SmarThingSchema(ma.SQLAlchemySchema):
    class Meta:
        # fields = ("id", "type_id", "name", "date_added")
        model = Smarthing
        load_instance = True
        sqla_session = db.session
        # include_fk = True

    id = ma.auto_field()
    type_id = ma.auto_field()
    # type_id = ma.auto_field()
    name = ma.auto_field()
    online = ma.auto_field()
    is_on = ma.auto_field()
    date_added = ma.auto_field()
    states = ma.Nested(StatesSchema)
    

    # smarThing = ma.Nested(TypeSchema)

thing_schema = SmarThingSchema()
things_schema = SmarThingSchema(many=True)


class SmarThingSchemaIMP(ma.SQLAlchemySchema):
    class Meta:
        # fields = ("id", "type_id", "name", "date_added")
        model = Smarthing
        load_instance = True
        sqla_session = db.session
        # include_fk = True

    online = ma.auto_field()
    is_on = ma.auto_field()
    states = ma.Nested(StatesSchemaIMP)

thing_schema_imp = SmarThingSchemaIMP()
things_schema_imp = SmarThingSchemaIMP(many=True)    


class TypeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Type
        load_instance = True
        sqla_session = db.session

    id = ma.auto_field()
    name = ma.auto_field()
    smar_thing = ma.Nested(SmarThingSchema, many=True)

    # things = ma.Nested(SmarThingSchema)
    # smarThings = ma.Nested(SmarThingSchema)

type_schema = TypeSchema()
types_schema = TypeSchema(many=True)

@app.route('/test')
def test():
    return f'database: {secretUrl}'

@app.route('/allTypes', methods=['GET'])
def getAll():
    types_all = Type.query.all()
    output = types_schema.dump(types_all)

    return jsonify(output)


@app.route('/allThings', methods=['GET'])
def getAllThings():
    things_all = Smarthing.query.all()
    output = things_schema.dump(things_all)

    return jsonify(output)


@app.route('/deleteDevice', methods=['DELETE'])
def delete():
    req_data = request.get_json()
    id = req_data['id']

    device_to_delete = Smarthing.query.get_or_404(int(id))
    things_all = Smarthing.query.all()

    db.session.delete(device_to_delete)
    db.session.commit()

    return "deleted"


@app.route('/addType', methods=['POST'])
def postType():
    req_data = request.get_json()

    name = req_data['name']

    new_type = Type(name=name)
    db.session.add(new_type)
    db.session.commit()

    return type_schema.jsonify(new_type)

@app.route('/addDevice', methods=['POST'])
def postDevice():
    req_data = request.get_json()

    name = req_data['name']
    type = req_data['type']

    find_type = Type.query.filter_by(name=type).first()

    new_device = Smarthing(name=name, parents=find_type)
    db.session.add(new_device)
    db.session.commit()

    return type_schema.jsonify(new_device)

@app.route('/addState', methods=['POST'])
def postStates():
    req_data = request.get_json()

    corrupt = req_data.get("corrupt")
    corrupt_mess = req_data.get("corrupt_mess")
    alarm = req_data.get("alarm")
    color = req_data.get("color")
    device = req_data.get("device")

    find_type = Smarthing.query.filter_by(name=device).first()
    new_state = States(corrupt=corrupt, corrupt_mess=corrupt_mess, alarm=alarm, color=color, parent=find_type)

    db.session.add(new_state)
    db.session.commit()

    return session_schema.jsonify(new_state)

@app.route('/importantDoors/<int:id>', methods=['GET'])
def important(id):
    if request.method == 'GET':
        thing = Smarthing.query.get(int(id))
        return thing_schema_imp.jsonify(thing)
    else:
        return "Method not allowed"

@app.route('/state/<int:id>', methods=['GET', 'PUT'])
def state(id):
    if request.method == 'PUT':
        
        # state = req_data['state']
        device_to_update = Smarthing.query.get(int(id))
        device_to_update.is_on = True
        db.session.commit()
        

        time.sleep(10)
        
        device_to_update.is_on = False
        db.session.commit()

        return thing_schema.jsonify(device_to_update)
    
    else:
        get_device_state = Smarthing.query.get(int(id))     

        return thing_schema.jsonify(get_device_state)

@app.route('/on/<int:id>', methods=['GET'])
def set_on(id):
        
    # state = req_data['state']
    device_to_update = Smarthing.query.get(int(id))
    device_to_update.is_on = True
    db.session.commit()

    return thing_schema.jsonify(device_to_update)


@app.route('/off/<int:id>', methods=['GET'])
def set_off(id):
        
    # state = req_data['state']
    device_to_update = Smarthing.query.get(int(id))
    device_to_update.is_on = False
    db.session.commit()

    return thing_schema.jsonify(device_to_update)


if __name__ == '__main__':
    app.debug = True
    app.run()