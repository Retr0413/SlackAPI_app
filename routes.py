from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

bp = Blueprint('routes', __name__)

# MySQLの設定
db_config = {
    'user': 'root',
    'password': 'Hayato0623',
    'host': 'db',
    'database': 'slack_attendance'
}

# Gmailの設定
EMAIL_ADDRESS = 'hahayato.arima@gmail.com'  # あなたのGmailアドレス
EMAIL_PASSWORD = 'Hayato0623'  # あなたのGmailパスワード
RECIPIENT_EMAIL = 'hakukohayato@gmail.com'  # 受信者のメールアドレス

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

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
        print("Error: user_name is missing or None!")
        return "Error: User name is required.", 400

    clock_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f'{user}さんが{clock_in_time}に出勤しました。'
    send_email(subject=f"{user}の出勤通知", body=message)
    save_clock_in_to_db(user, clock_in_time)

    return redirect(url_for('routes.attendance', user=user))

@bp.route('/clock-out', methods=['POST'])
def clock_out():
    user = request.form.get('user')
    if not user:
        print("Error: user_name is missing or None!")
        return "Error: User name is required.", 400

    clock_out_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f'{user}さんが{clock_out_time}に退勤しました。'
    send_email(subject=f"{user}の退勤通知", body=message)
    save_clock_out_to_db(user, clock_out_time)

    return redirect(url_for('routes.attendance', user=user))

@bp.route('/attendance/<user>')
def attendance(user):
    record = get_latest_attendance(user)
    return render_template('attendance.html', record=record)
