from flask import Flask, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin



app = Flask(__name__)
class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

users = {'user': User('user', 'password')}


# Sửa thông tin user
def edit_user(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    acc_id = session.get('AccID')  # Lấy AccID từ phiên làm việc

    if request.method == "POST":
        details = request.form
        fullname = details['fullname']
        date = details['date']
        phone = details['phone']
        gender = details['gender']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE user SET Username = %s, Date = %s, Phone = %s, Gender = %s WHERE AccID = %s", (fullname, date, phone, gender, acc_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('user_page'))


def show_user_details(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    
    acc_id = session.get('AccID')  # Lấy AccID từ phiên làm việc

    cur = mysql.connection.cursor()
    cur.execute("SELECT user.username, user.date, user.phone, user.gender, account.email FROM user INNER JOIN account ON user.AccID = account.AccID WHERE account.AccID = %s", (acc_id,))
    user_data = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return render_template('user/user.html', fullname=user_data[0], date=user_data[1], phone=user_data[2],  gender = user_data[3], email=user_data[4])