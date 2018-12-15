import imaplib
import json
import time

import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///landing.db'

db = SQLAlchemy(app)

GIT_TOKEN = '8b5da14674a9d607eb5a0fa944cc90b9bf3d5747'


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imapClient = db.Column(db.String(50), primary_key=False)
    email = db.Column(db.String(50), primary_key=False)
    password = db.Column(db.String(50), primary_key=False)
    trelloBoardId = db.Column(db.String(50), primary_key=False)
    googleCalendarId = db.Column(db.String(50), primary_key=False)
    gitUser = db.Column(db.String(50), primary_key=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), primary_key=False)
    start = db.Column(db.String(50), primary_key=False)
    end = db.Column(db.String(50), primary_key=False)


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


db.create_all()
db.session.commit()


def get_git_projects(user):
    projects = []

    r = requests.get('https://api.github.com/users/{user}/repos?page=1&per_page=100'.format(user=user),
                     headers={'Authorization': 'token %s' % GIT_TOKEN})

    if r.status_code == 200:

        data = r.content
        data = json.loads(data.decode('utf-8'))

        for item in data:
            projects.append(item['name'])

    return projects


def get_git_issues(projects):
    issues = 0

    for project in projects:

        r = requests.get('https://api.github.com/repos/celisoft/{project}/issues'.format(project=project),
                         headers={'Authorization': 'token %s' % GIT_TOKEN})

        if r.status_code == 200:

            data = r.content
            data = json.loads(data.decode('utf-8'))
            if data:
                issues += len(data)

    return issues


def obtain_git_data(issues_query, user):
    if issues_query is not None:
        projects = get_git_projects(user)
        issues = get_git_issues(projects)
    else:
        projects = get_git_projects(user)
        issues = 111

    return [len(projects), issues]


def init_imap_client(saved_settings):
    client = None
    if saved_settings[0].imapClient == 'imap-mail.outlook.com':

        # Outlook
        client = imaplib.IMAP4_SSL('imap-mail.outlook.com', port=993)
        client.login('{email}'.format(email=saved_settings[0].email),
                     '{password}'.format(password=saved_settings[0].password))

    elif saved_settings[0].imapClient == 'imap.gmail.com':

        # Gmail
        client = imaplib.IMAP4_SSL('imap.gmail.com', port=993)
        client.login('{email}'.format(email=saved_settings[0].email),
                     '{password}'.format(password=saved_settings[0].password))

    return client


def create_mail_counter(client):
    client.select()
    status, data = client.search(None, "UnSeen")
    if status != 'OK':
        print("No messages found!")
    else:
        val = len(data[0].split())

        if val != 0:
            print("Found mails amount : {}".format(val))
            new_mail_counter = MailCounter(count=val)
            db.session.add(new_mail_counter)
            db.session.commit()

    client.logout()


@app.route('/list')
def send_list():
    current_list = request.args.get('list')
    print(current_list)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'lcutepage@gmail.com'
    app.config['MAIL_PASSWORD'] = 'Xyl@nd1a'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail_client = Mail(app)

    saved_settings = Settings.query.all()
    email = saved_settings[0].email

    msg = Message(subject='Pimp My Cart', sender='zoebelleton@gmail.com', recipients=[email])
    msg.body = "LCuteP.list : " + current_list + \
               "\n We wish you a super cute experience !"
    mail_client.send(msg)
    return jsonify('Sent')


@app.route('/mail', methods=['GET', 'POST'])
def mail():
    saved_settings = Settings.query.all()

    if saved_settings:
        try:
            client = init_imap_client(saved_settings)
            create_mail_counter(client)

        except ConnectionError:
            print("Connection Error")

        return index()

    else:
        return ask_for_settings()


def get_mail(saved_settings):
    try:
        client = init_imap_client(saved_settings)
        create_mail_counter(client)

    except ConnectionError:
        print("Connection Error")

    return get_mail_amount()


def ask_for_settings():
    status = 'Settings'

    # Mail counter
    timestamp = time.strftime('%d %B %Y %H:%M:%S')

    return render_template(template_name_or_list='index.html',
                           timestamp=timestamp,
                           my_events=Event.query.all(),
                           status=status)


@app.route('/', methods=['GET', 'POST'])
def index():
    widget = request.form.get('widget')
    status = request.form.get('status')
    issues_query = request.form.get('issues_query')

    # Mail counter
    timestamp = time.strftime('%d %B %Y %H:%M:%S')

    # Weather data
    weather_data = WeatherData.query.all()

    # Settings
    saved_settings = Settings.query.all()

    todo_lists = None
    git_data = None

    if issues_query:
        if saved_settings:
            git_data = obtain_git_data(issues_query, saved_settings[0].gitUser)

    if status == 'update_weather':
        update_weather()
        status = 'Map'
    elif status == 'Mail':
        if saved_settings:
            get_mail(saved_settings)
    elif status == 'Todo':
        todo_lists = get_todo_lists()
    elif status == 'List':
        print("We will make a list")

    mail_amount = get_mail_amount()

    return render_template(template_name_or_list='index.html',
                           timestamp=timestamp,
                           my_events=Event.query.all(),
                           weather_data=weather_data,
                           status=status,
                           todo_lists=todo_lists,
                           mail_counter=mail_amount,
                           git_data=git_data,
                           saved_settings=saved_settings)


@app.route('/events', methods=['GET', 'POST'])
def get_events():
    api_key = 'AIzaSyDbEzOFyKrBKm669WLAsEfmtOJV0DAPZLc'
    r = requests.get(
        f'https://www.googleapis.com/calendar/v3/calendars/zoebelleton%40gmail.com/events?key={api_key}')

    if r.status_code == 200:
        data = r.content
        data = json.loads(data.decode('utf-8'))

        for e in data['items']:
            event = [0, 0, 0]

            for key, value in e.items():
                if key == 'summary':
                    event[0] = value
                if key == 'start':
                    for k, v in value.items():
                        if k == 'dateTime':
                            event[1] = v
                if key == 'end':
                    for k, v in value.items():
                        if k == 'dateTime':
                            event[2] = v
            get_or_create_event(event[0], event[1], event[2])

    return index()


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':

        imap = request.form.get('imap')
        mail = request.form.get('mail')
        password = request.form.get('password')
        board_id = request.form.get('board_id')
        calendar_id = request.form.get('calendar_id')
        git_user = request.form.get('git_user')

        print(imap)
        print(mail)
        print(password)
        print(board_id)
        print(calendar_id)
        print(git_user)

        Settings.query.delete()
        if imap and mail and password and board_id and calendar_id:
            get_or_create_settings(imap, mail, password, board_id, calendar_id, git_user)
    return index()


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        new_city = request.form.get('city')

        if new_city:
            print("Request add for  " + new_city + " !")
            create_weather_data(new_city)
    return render_template(template_name_or_list='index.html',
                           timestamp=time.strftime('%d %B %Y %H:%M:%S'),
                           my_events=None,
                           weather_data=WeatherData.query.all(),
                           status='Map',
                           todo_lists=None,
                           mail_counter=get_mail_amount(),
                           git_data=None,
                           saved_settings=Settings.query.all())


def update_weather():
    cities = WeatherData.query.all()
    WeatherData.query.delete()
    for city in cities:
        new_city = city.name
        create_weather_data(new_city)


@app.route('/rm', methods=['GET', 'POST'])
def rm():
    deleted_city = request.form['deleted_city']
    WeatherData.query.filter_by(name=deleted_city).delete()
    print("Removing " + deleted_city + " from cities !")
    db.session.commit()
    return render_template(template_name_or_list='index.html',
                           timestamp=time.strftime('%d %B %Y %H:%M:%S'),
                           my_events=None,
                           weather_data=WeatherData.query.all(),
                           status='Map',
                           todo_lists=None,
                           mail_counter=get_mail_amount(),
                           git_data=None,
                           saved_settings=Settings.query.all())


@app.route('/city_map/<city>', methods=['GET', 'POST'])
def city_map(city):
    return render_template(template_name_or_list='index.html',
                           timestamp=time.strftime('%d %B %Y %H:%M:%S'),
                           my_events=None,
                           weather_data=WeatherData.query.all(),
                           status='Map',
                           todo_lists=None,
                           mail_counter=get_mail_amount(),
                           git_data=None,
                           saved_settings=Settings.query.all())


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


def get_or_create_weather_data(name, temperature, description, icon):
    exists = db.session.query(WeatherData.id).filter_by(name=name).scalar() is not None

    if exists:
        return db.session.query(WeatherData).filter_by(name=name).first()
    else:
        new_weather_obj = WeatherData(name=name, temperature=temperature, description=description, icon=icon)
        db.session.add(new_weather_obj)
        db.session.commit()
        return name


def get_or_create_settings(imap, mail, password, board_id, calendar_id, git_user):
    exists = db.session.query(Settings.id).filter_by(email=mail).scalar() is not None

    if exists:
        return db.session.query(Settings).filter_by(email=mail).first()
    else:
        new_settings_obj = Settings(imapClient=imap,
                                    email=mail,
                                    password=password,
                                    trelloBoardId=board_id,
                                    googleCalendarId=calendar_id,
                                    gitUser=git_user)

        db.session.add(new_settings_obj)
        db.session.commit()
        return password


def get_or_create_event(title, start, end):
    exists = db.session.query(Event.id).filter_by(title=title).scalar() is not None

    if exists:
        return db.session.query(Event).filter_by(title=title).first()
    else:
        new_event_obj = Event(title=title, start=start, end=end)
        db.session.add(new_event_obj)
        db.session.commit()
        return title


def get_or_create_todo(list_name, name):
    exists = db.session.query(TodoCard.id).filter_by(name=name).scalar() is not None

    if exists:
        return db.session.query(TodoCard).filter_by(name=name).first()
    else:
        new_todo_obj = WeatherData(list_name=list_name, name=name)
        db.session.add(new_todo_obj)
        db.session.commit()
        return name


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


def get_mail_amount():
    counters = MailCounter.query.all()

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

    return render_template(template_name_or_list='index.html',
                           timestamp=time.strftime('%d %B %Y %H:%M:%S'),
                           my_events=None,
                           weather_data=None,
                           status='Todo',
                           todo_lists=get_todo_lists(),
                           mail_counter=get_mail_amount(),
                           git_data=None,
                           saved_settings=Settings.query.all())


def get_todo_lists():
    todo_cards = TodoCard.query.all()
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
