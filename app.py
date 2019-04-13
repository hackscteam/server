from flask import Flask, request, jsonify
import flask
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    mobile = db.Column(db.String(80))
    address = db.Column(db.String(80))
    birthday = db.Column(db.String(80))
    email = db.Column(db.String(120))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.first_name


class Pending(db.Model):
    __tablename__ = "Pending"

    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    user1ID = db.Column(db.Integer)
    user2ID = db.Column(db.Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


class Wave(db.Model):
    __tablename__ = "Wave"

    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    userID = db.Column(db.Integer)
    lat = db.Column(db.Integer)
    long = db.Column(db.Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    recieveKey = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.time


users = [
    {'id': 0,
     'first_name': 'Zach',
     'last_name': 'Pinto',
     'mobile': '510-314-4473',
     'birthdate': '09/29/1999',
     'email': 'pintozachary@gmail.com'},
    {'id': 1,
     'first_name': 'Charles',
     'last_name': 'James',
     'mobile': '510-333-4473',
     'birthdate': '09/20/1999',
     'email': 'charles@gmail.com'}
]

pending = [
    {'recieveKey': 0,
     'user1ID': {
         'id': 0,
         'first_name': 'Zach',
         'last_name': 'Pinto',
         'mobile': '510-314-4473',
         'birthdate': '09/29/1999',
         'email': 'pintozachary@gmail.com'
     },
     'user2ID': {
     }, }
]

waves = [
    {'id': 0,
     'location': '39.5, 38.8',
     'time': 23,
     'recieveKey': 0
     }
]


@app.after_request
def allow_cross_domain(response: flask.Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    return response


@app.route('/', methods=['GET'])
def home():

    return "Test"


@app.route('/v1/waveaction', methods=['GET'])
def makeWave():

    ra = request.get_json()

    if 'id' in request.args and 'lat' in request.args and 'long' in request.args and 'time' in request.args:
        waveMatch = Wave.query.filter_by(
            lat=ra['lat'], long=ra['long'], time=ra['time']).first()
        if waveMatch:
            recieveKey = waveMatch.recieveKey
            # db.session.delete(waveMatch)
            # db.session.commit()
            pend = Pending.query.filter_by(id=recieveKey).first()
            pend.user2ID = ra['id']
            db.session.commit()
            return jsonify({'recieveKey': recieveKey})
        else:
            pending = Pending(user1ID=ra['id'])
            db.session.add(pending)
            db.session.commit()
            newWave = Wave(
                userID=ra['id'], lat=ra['lat'], long=ra['long'], time=ra['time'], recieveKey=pending.id)
            db.session.add(newWave)
            db.session.commit()
            return jsonify({'recieveKey': newWave.recieveKey})
    else:
        return "Error: No id field provided. Please specify an id."


@app.route('/v1/getcontact', methods=['GET'])
def getContact():
    # auth_url = client.get_auth_url()
    if 'userID' in request.args and 'recieveKey' in request.args:
        return jsonify({'hello': 'balls'})

    else:
        return "Error: No id field provided. Please specify an id."


@app.route('/v1/createuser', methods=['POST'])
def write():

    # print(request.body)
    print('good')
    rd = request.get_json()

    print(rd)
    newUser = User(first_name=rd['firstname'], last_name=rd['lastname'], mobile=rd['mobile'],
                   email=rd['email'], address=rd['address'], birthday=rd['birthdate'])
    db.session.add(newUser)
    db.session.commit()

    return jsonify({'id': newUser.id})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
