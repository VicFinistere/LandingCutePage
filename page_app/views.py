import imaplib

import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)


class MailCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.String(50), primary_key=False)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def get_or_create_city(name):
    exists = db.session.query(City.id).filter_by(name=name).scalar() is not None

    if exists:
        return db.session.query(City).filter_by(name=name).first()
    else:
        new_city_obj = City(name=name)
        db.session.add(new_city_obj)
        db.session.commit()
        return name


@app.route('/rm', methods=['POST'])
def rm():
    deleted_city = request.form['deleted_city']
    City.query.filter_by(name=deleted_city).delete()
    print("Removing " + deleted_city + " from cities !")
    db.session.commit()
    return index()


@app.route('/mail', methods=['POST'])
def mail():
    val = 0
    try:
        gmail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        gmail.login('zoebelleton@gmail.com', 'B0r1ngPassw0rd')
        gmail.select()

        val = len(gmail.search(None, 'UnSeen')[1][0].split())

        if val != 0:
            print("Found mails amount : {}".format(val))
            new_mail_counter = MailCounter(count=val)
            db.session.add(new_mail_counter)
            db.session.commit()
        else:
            print(val)
    except:
        print(val)
    return index()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_city = request.form.get('city')

        if new_city:
            print("Request add for  " + new_city + " !")
            get_or_create_city(new_city)

    cities = City.query.all()
    counters = MailCounter.query.all()

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=254d0bd84bee0354b5b34e17f870cf04'

    weather_data = []
    mail_counter = []

    for city in cities:
        r = requests.get(url.format(city.name)).json()

        weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        weather_data.append(weather)

    amount = len(counters)
    print("There is ...")
    print(amount)
    for counter_amount, counter in enumerate(counters):
        if counter_amount < amount - 1:
            print("It will be deleted")
            print(counter.id)
            MailCounter.query.filter_by(id=counter.id).delete()
            db.session.commit()
        mail_counter.append(counter.count)

    return render_template('index.html', weather_data=weather_data, mail_counter=mail_counter[-1])
