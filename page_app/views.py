"""
Handling views of the web application
"""
# Flask
from flask import Flask, render_template, request, jsonify

# Logs
import logging

# Grand-py Robot
import page_app.logic

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """
    Index :return: web page template
    """
    return render_template('index.html')

