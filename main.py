from flask import Flask, request, jsonify
import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime, DECIMAL
import json
import datetime
import os

app = Flask(__name__)


# Environment variables are defined in app.yaml.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.first_name


class Pending(db.Model):
    __tablename__ = "Pending"

    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    user1ID = db.Column(db.Integer)
    user2ID = db.Column(db.Integer)
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


class Wave(db.Model):
    __tablename__ = "Wave"

    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    userID = db.Column(db.Integer)
    lat = db.Column(db.DECIMAL)
    lon = db.Column(db.DECIMAL)
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)
    recieveKey = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.time


@app.after_request
def allow_cross_domain(response: flask.Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    return response


@app.route('/', methods=['GET'])
def home():

    return "Test"


@app.route('/v1/test', methods=['GET'])
def test():
    wave = Wave.query.filter_by(id=0).first()
    return jsonify({'test': wave.id})


def getBestMatch(posMatches, timeCheck, checkID, lat, long):
    # print("gettingMatch")
    for wave in posMatches:
        print(wave)
        # print("gettingMatch")
        latDiff = wave.lat - lat
        print(latDiff)
        longDiff = wave.lon - long
        timediff = wave.created_date - timeCheck
        # print(diff.total_seconds())
        timediff = timediff.total_seconds()
        if abs(timediff) <= 45 and latDiff < 0.01 and longDiff < 0.01:
            # print(diff)
            return wave


@app.route('/v1/waveaction', methods=['POST'])
def makeWave():
        # waveMatch = getBestMatch(Wave.query.all(), timeCheck)
    ra = request.get_json()
    if ra['id'] and ra['lat'] and ra['long'] and ra['time']:

        timeCheck = datetime.datetime.utcnow()
        waveMatch = getBestMatch(
            Wave.query.filter(userID != ra['id']).all(), timeCheck, ra['id'], ra['lat'], ra['long'])

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
                userID=ra['id'], lat=ra['lat'], lon=ra['long'], recieveKey=pending.id)
            db.session.add(newWave)
            db.session.commit()
            return jsonify({'recieveKey': newWave.recieveKey})
    else:
        return "Error: No id field provided. Please specify an id."


@app.route('/v1/getcontact', methods=['POST'])
def getContact():
    ra = request.get_json()
    if ra['userid'] and ra['recieveKey']:
        pend = Pending.query.filter_by(id=ra['recieveKey']).first()
        if(pend.user1ID is None or pend.user2ID is None):
            print({'firstname': '~There is no one around!',
                   'user1': pend.user1ID,
                   'user2': pend.user2ID})
            return jsonify({'firstname': '~There is no one around!',
                            'user1': pend.user1ID,
                            'user2': pend.user2ID})
        if(pend.user1ID == ra['userid']):
            contact = User.query.filter_by(id=pend.user2ID).first()
        else:
            contact = User.query.filter_by(id=pend.user1ID).first()

        return jsonify({'firstname': contact.first_name,
                        'lastname': contact.last_name,
                        'mobile': contact.mobile,
                        'address': contact.address,
                        'birthdate': contact.birthday,
                        'email': contact.email
                        })

    else:
        return "Error: No id field provided. Please specify an id."


@app.route('/v1/createuser', methods=['POST'])
def write():

    # print(request.body)
    print('good')
    rd = request.get_json()

    newUser = User(first_name=rd['firstname'], last_name=rd['lastname'], mobile=rd['mobile'],
                   email=rd['email'], address=rd['address'], birthday=rd['birthdate'])
    db.session.add(newUser)
    db.session.commit()

    return jsonify({'id': newUser.id})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
