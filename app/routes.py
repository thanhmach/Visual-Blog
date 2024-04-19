from flask import Flask, render_template, request, url_for, redirect, flash, session
from .auth import register as auth_register, login as auth_login, auth_logout
from .edit_user import edit_user as edit, show_user_details as show
from .blogpost import post, show_post_details as show_post, del_post as delete, update_post as sua_post
from .newfeed import get_feed, comment, show_comment_details, del_comment_details, update_comment, like, show_like, count_like, del_like

import base64
from flask_mysqldb import MySQL
from flask import jsonify
import os
from google.cloud import translate_v2 as translate

client = translate.Client()

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

mysql = MySQL(app)

# Index
@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        acc_id = session.get('AccID')
        return render_template('index/index.html', data = acc_id)
    else:
        return redirect(url_for('login'))

## chức năng tạo tài khoản và đăng nhập
@app.route('/register', methods=["POST", "GET"])
def register():
    return auth_register(mysql)

@app.route('/login', methods=["POST", "GET"])
def login():
   return auth_login(mysql)


## update thông tin user
@app.route('/update', methods =["POST", "GET"])
def update():
    return edit(mysql)

#hàm logout
@app.route('/logout')
def logout():
    return auth_logout()

#hàm đăng bài
@app.route('/blog-post', methods = ["POST", "GET"])
def blog():
    return post(mysql)

#hàm xóa bài
@app.route('/del_blog', methods = ["POST", "GET"])
def del_post():
    return delete(mysql)


#hàm edit blog
@app.route('/update_blog', methods = ["POST", "GET"])
def update_post():
    return sua_post(mysql)


@app.route('/newfeed', methods=["POST", "GET"])
def newfeed():
    # Lấy danh sách bài đăng từ hàm get_feed
    posts = get_feed(mysql)
    
    # Duyệt qua từng bài đăng và tính tổng lượt thích
    for post in posts:
        post['like_count'] = count_like(mysql, post['blogid'])

    comment_details = show_comment_details(mysql)
    like_details = show_like(mysql)

    return render_template('blog/blog.html', posts=posts, comment_details=comment_details, like_details=like_details)

@app.route('/like_blog', methods=["POST", "GET"])
def likes():
    return like(mysql)

@app.route('/del_like', methods =["POST", "GET"])
def dis_like():
    return del_like(mysql)

###Trả về 2 trang
@app.route('/register_page')
def register_page():
    return render_template('index/register.html')

@app.route('/index')
def return_index():
    return render_template('index/index.html')

#hàm load trang login
@app.route('/login_page', methods =["POST", "GET"])
def login_page():
    return render_template('index/login.html')

#hàm comment
@app.route('/comment', methods = ["GET","POST"])
def comment_blog():
    return comment(mysql)

#hàm hiển thị comment
@app.route('/get_comment')
def show_comment():
    return show_comment_details(mysql)

#hàm xóa comment
@app.route('/del_comment', methods = ["GET", "POST"])
def delete_comment():
    return del_comment_details(mysql)

#hàm update comment
@app.route('/update_comment', methods = ["GET", "POST"])
def updated_comment():
    return update_comment(mysql)

#Show thông tin user
@app.route('/user_page')
def user_page():
    return show(mysql)

@app.route('/inner')
def inner_page():
    show_blog = show_post(mysql)
    comment_details = show_comment_details(mysql)

    for post in show_blog:
        post['like_count'] = count_like(mysql, post['blogid'])
        
    return render_template('blog/inner-page.html',  posts=show_blog, comment_details=comment_details)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data['text']
    target_language = data['targetLanguage']
    
    translation = client.translate(text, target_language=target_language)
    translated_text = translation['translatedText']

    return jsonify({'translatedText': translated_text})