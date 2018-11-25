import imaplib

import requests


def get_mail():
    mail_server = imaplib.IMAP4_SSL \
        ('imap.gmail.com', 993)

    user = 'zoebelleton'
    password = 'B0r1ngPassw0rd'
    mail_server.login(user, password)
    stat, cnt = mail_server.select('Inbox')
    stat, dta = mail_server.fetch(cnt[0], '(UID BODY[TEXT]')
    print(dta[0][1])
    mail_server.close()
    mail_server.logout()


def get_weather(city, days):
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?id=" + city + "&units=metric&cnt=" + days + "&appid=254d0bd84bee0354b5b34e17f870cf04"
    response = requests.get(url)
    return response.json()
