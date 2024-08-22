from flask import Blueprint, render_template, request, redirect, url_for
import requests
import mysql.connector
from datetime import datetime

bp = Blueprint('routes', __name__)

# MySQLの設定
db_config = {
    'user': 'root',
    'password': 'Hayato0623',
    'host': 'db',
    'database': 'slack_attendance'
}

# Slackの設定（直接コード内に設定）
SLACK_TOKEN = 'xoxb-7627471010593-7616094326114-p1eAmMQGrqKQ39THXK4mC2oi'  # あなたのトークンをここに設定
SLACK_CHANNEL_ID = 'C07J58QKA6Q'  # チャンネルIDを設定

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
    response_data = response.json()

    # レスポンスのデバッグ出力
    print("Slack API Request Data:", data)
    print("Slack API Response Data:", response_data)

    if not response_data.get('ok'):
        print(f"Error sending message to Slack: {response_data.get('error')}")
    else:
        print("Message sent successfully to Slack.")

    return response_data

def save_clock_in_to_db(user, clock_in_time):
    if not user:  # userがNoneまたは空の場合、処理を停止
        print("Error: user_name is missing or None!")
        return
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO attendance (user_name, clock_in_time) VALUES (%s, %s)', 
        (user, clock_in_time)
    )
    conn.commit()
    cursor.close()
    conn.close()

def save_clock_out_to_db(user, clock_out_time):
    if not user:  # userがNoneまたは空の場合、処理を停止
        print("Error: user_name is missing or None!")
        return
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE attendance SET clock_out_time = %s WHERE user_name = %s AND clock_out_time IS NULL', 
        (clock_out_time, user)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_latest_attendance(user):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM attendance WHERE user_name = %s ORDER BY clock_in_time DESC LIMIT 1",
        (user,)
    )
    record = cursor.fetchone()
    cursor.close()
    conn.close()
    return record

@bp.route('/')
def index():
    user_name = "LoggedInUser"  # 実際のログインユーザー名をここに設定
    return render_template('index.html', user_name=user_name)

@bp.route('/clock-in', methods=['POST'])
def clock_in():
    user = request.form.get('user')
    if not user:
        print("Error: user_name is missing or None!")  # デバッグ用メッセージ
        return "Error: User name is required.", 400
    
    clock_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f'{user}さんが{clock_in_time}に出勤しました。'
    send_slack_message(message)
    save_clock_in_to_db(user, clock_in_time)
    return redirect(url_for('routes.attendance', user=user))

@bp.route('/clock-out', methods=['POST'])
def clock_out():
    user = request.form.get('user')
    if not user:
        print("Error: user_name is missing or None!")  # デバッグ用メッセージ
        return "Error: User name is required.", 400
    
    clock_out_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f'{user}さんが{clock_out_time}に退勤しました。'
    send_slack_message(message)
    save_clock_out_to_db(user, clock_out_time)
    return redirect(url_for('routes.attendance', user=user))

@bp.route('/attendance/<user>')
def attendance(user):
    record = get_latest_attendance(user)
    return render_template('attendance.html', record=record)
