from flask import Blueprint, render_template, request, redirect, url_for
import requests
import mysql.connector
from datetime import datetime

bp = Blueprint('routes', __name__)

# MySQLの設定
db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'db',
    'database': 'slack_attendance'
}

# Slackの設定
SLACK_TOKEN = ''
SLACK_CHANNEL_ID = ''

def send_slack_message(text):
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': f'Bearer {SLACK_TOKEN}',
        'Content-Type': 'application/json; charset=utf-8'
    }
    data = {
        'channel': SLACK_CHANNEL_ID,
        'text': text
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def save_clock_in_to_db(user, clock_in_time):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO attendance (user, clock_in_time) VALUES (%s, %s)', 
        (user, clock_in_time)
    )
    conn.commit()
    cursor.close()
    conn.close()

def save_clock_out_to_db(user, clock_out_time):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE attendance SET clock_out_time = %s WHERE user = %s AND clock_out_time IS NULL', 
        (clock_out_time, user)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_latest_attendance(user):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM attendance WHERE user = %s ORDER BY clock_in_time DESC LIMIT 1",
        (user,)
    )
    record = cursor.fetchone()
    cursor.close()
    conn.close()
    return record

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/clock-in', methods=['POST'])
def clock_in():
    user = request.form.get('user')
    clock_in_time = datetime.now().strftime('%Y-&m-%d %H:%M:%S')
    message = f'{user}さんが{clock_in_time}に出勤しました。'
    send_slack_message(message)
    save_clock_in_to_db(user, clock_in_time)
    return redirect(url_for('routes.attendance', user=user))

@bp.route('/clock-out', methods=['POST'])
def clock_out():
    user = request.form.get('user')
    clock_out_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f'{user}さんが{clock_out_time}に退勤しました。'
    send_slack_message(message)
    save_clock_out_to_db(user, clock_out_time)
    return redirect(url_for('routes.attendance', user=user))

@bp.route('/attendance/<user>')
def attendance(user):
    record = get_latest_attendance(user)
    return render_template('attendance.html', record=record)