from flask import Flask, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin


app = Flask(__name__)
class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

users = {'user': User('user', 'password')}


# @app.route('/register', methods=["POST", "GET"])
def register(mysql):
    gender = request.form.get('gender')
    print(gender)
    if request.method == "POST":
        details = request.form
        account = details['account']
        password = details['password']
        email = details['email']
        username = details['username']
        date = details['date']
        phone = details['phone']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO account(PermissionID ,Account, Password, Email) VALUES (%s ,%s, %s, %s)", ('1' ,account, password, email))
        # Lấy giá trị account_id vừa được tạo
        cur.execute("SELECT LAST_INSERT_ID()")
        account_id = cur.fetchone()[0]

        cur.execute("INSERT INTO user(AccID, Username, Date, Phone, Gender) VALUES (%s, %s, %s, %s, %s)", (account_id, username, date, phone, gender))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login_page'))
    return render_template('index/register.html')
 


# Hàm login
def login(mysql):
    if request.method == 'POST':
        details = request.form
        account = details['account']
        password = details['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM account WHERE Account = %s AND Password = %s", (account, password))
        accounts = cur.fetchall()
        for acc in accounts:
            if acc[2] == account and acc[3] == password:
                session['logged_in'] = True
                session['account'] = account
                session['AccID'] = acc[0]  # Gán giá trị AccID từ acc[0] cho phiên làm việc
                cur.close()
                acc_id = session.get('AccID')  # Lấy AccID từ phiên làm việc
                print("acc_id:", acc_id)
                # flash('Đăng nhập thành công!', 'success')  # Hiển thị flash message
                return redirect(url_for('newfeed'))
                # return render_template('Onepage/inner-page.html')
        cur.close()
        flash('Tài khoản hoặc mật khẩu không chính xác', 'danger')
    return render_template('index/login.html')

def auth_logout():
    session.clear()  # Xóa tất cả các biến phiên làm việc
    return redirect(url_for('login_page'))  # Chuyển hướng về trang đăng nhập
