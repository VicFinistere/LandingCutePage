import imaplib

import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///landing.db'

db = SQLAlchemy(app)


class MailCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.String(50), primary_key=False)


class TodoCard(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_name = db.Column(db.String(50), primary_key=False)
    name = db.Column(db.String(50), primary_key=False)


class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), primary_key=False)
    temperature = db.Column(db.String(50), primary_key=False)
    description = db.Column(db.String(50), primary_key=False)
    icon = db.Column(db.String(50), primary_key=False)


def get_or_create_weather_data(name, temperature, description, icon):
    exists = db.session.query(WeatherData.id).filter_by(name=name).scalar() is not None

    if exists:
        return db.session.query(WeatherData).filter_by(name=name).first()
    else:
        new_weather_obj = WeatherData(name=name, temperature=temperature, description=description, icon=icon)
        db.session.add(new_weather_obj)
        db.session.commit()
        return name


@app.route('/rm', methods=['GET', 'POST'])
def rm():
    deleted_city = request.form['deleted_city']
    WeatherData.query.filter_by(name=deleted_city).delete()
    print("Removing " + deleted_city + " from cities !")
    db.session.commit()
    return index()


def create_weather_data(new_city):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=254d0bd84bee0354b5b34e17f870cf04'

    r = requests.get(url.format(new_city)).json()

    name = new_city
    temperature = r['main']['temp']
    description = r['weather'][0]['description'],
    icon = r['weather'][0]['icon'],
    print(new_city)
    get_or_create_weather_data(name=name, temperature=temperature, description=description[0], icon=icon[0])
    return name


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        new_city = request.form.get('city')

        if new_city:
            print("Request add for  " + new_city + " !")
            create_weather_data(new_city)
    return index()


@app.route('/update_weather', methods=['GET', 'POST'])
def update_weather():
    print("Update")
    cities = WeatherData.query.all()
    WeatherData.query.delete()
    print("Delete")
    for city in cities:
        new_city = city.name
        create_weather_data(new_city)

    return index()


def get_or_create_todo(list_name, name):
    exists = db.session.query(TodoCard.id).filter_by(name=name).scalar() is not None

    if exists:
        return db.session.query(TodoCard).filter_by(name=name).first()
    else:
        new_todo_obj = WeatherData(list_name=list_name, name=name)
        db.session.add(new_todo_obj)
        db.session.commit()
        return name


@app.route('/todo', methods=['GET', 'POST'])
def todo(board_id='5a58e9ba63b7c51ac07be475',
         api_key='69abc7b9ee8bdd9cd4919bde1a56e0bb',
         api_pass='a02694c95a37546e884b86f5c3045b85ca53c006dd0950733be2808c5ddcb157'):
    try:
        data = requests.get("https://api.trello.com/1/boards/{boardid}"
                            "?lists=open&list_fields=name&fields=name,desc"
                            "&key={key}&token={token}"
                            .format(boardid=board_id, key=api_key, token=api_pass)).json()

    except requests.exceptions.ConnectionError:
        print('Connexion error')
        return None

    for current_list in data['lists']:
        list_name = data['lists'][0]['name']  # To do list
        list_id = current_list['id']

        list_data = requests.get("https://api.trello.com/1/lists/{listid}?fields=name"
                                 "&cards=open&card_fields=name"
                                 "&key={key}&token={token}"
                                 .format(listid=list_id, key=api_key, token=api_pass)).json()

        for item in list_data['cards']:

            if item['name'] is not None and current_list['name'] is not None:
                get_or_create_todo(current_list['name'], item['name'])
            if list_name != current_list['name']:
                list_name = current_list['name']
                print("\n{}\n".format(list_name))

    return index()


@app.route('/city_map/<city>', methods=['GET', 'POST'])
def city_map(city):
    return index()


@app.route('/geoloc_map', methods=['GET', 'POST'])
def geoloc_map():
    return index()


@app.route('/mail', methods=['GET', 'POST'])
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
    except ConnectionError:
        print(val)
    return index()


def get_todo_list_names(todo_cards):
    todo_lists = []
    todo_list_name = todo_cards[0].list_name
    for i, todo_card in enumerate(todo_cards):

        # First time filled array
        if not todo_lists:
            todo_lists.append(todo_card.list_name)

        # When name changed
        elif todo_card.list_name != todo_list_name:
            todo_list_name = todo_card.list_name
            todo_lists.append(todo_card.list_name)

        # Parsing other cards of same list
        else:
            pass

    todo_lists = set(todo_lists)
    return todo_lists


def get_mail_amount(counters):
    mail_counter = []
    amount = len(counters)
    print("There is {} mail counters ...".format(amount))
    for counter_amount, counter in enumerate(counters):
        if counter_amount < amount - 1:
            print("Mail counters will be deleted")
            print(counter.id)
            MailCounter.query.filter_by(id=counter.id).delete()
            db.session.commit()
        mail_counter.append(counter.count)

    if len(mail_counter) > 1:
        mail_amount = mail_counter[-1]
    elif len(mail_counter) == 1:
        mail_amount = mail_counter[0]
    else:
        mail_amount = 0
    return mail_amount


def get_todo_lists(todo_cards):
    todo_lists = []

    if todo_cards:
        todo_lists_names = get_todo_list_names(todo_cards)
        todo_lists_names = list(todo_lists_names)

        # Create as much as list name items in list
        for i in todo_lists_names:
            todo_lists.append(i)

        for i in range(len(todo_lists)):
            new_list = []

            for todo_card in todo_cards:
                if todo_card.list_name == todo_lists[i]:
                    new_list.append(todo_card.name)
            list_name = todo_lists[i]
            todo_lists[i] = [0, []]
            todo_lists[i][0] = list_name
            todo_lists[i][1] = new_list
    return todo_lists


@app.route('/', methods=['GET', 'POST'])
def index():
    # Weather data
    weather_data = WeatherData.query.all()
    # To do list
    todo_cards = TodoCard.query.all()
    todo_lists = get_todo_lists(todo_cards)

    # Mail counter
    mails_counters = MailCounter.query.all()
    mail_amount = get_mail_amount(mails_counters)

    return render_template('index.html', weather_data=weather_data, todo_lists=todo_lists, mail_counter=mail_amount)
