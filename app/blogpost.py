from flask import Flask, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import time


app = Flask(__name__)
class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

users = {'user': User('user', 'password')}


def post(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    
    acc_id = session.get('AccID')  # Lấy AccID từ phiên làm việc
    content = request.form.get('content')
    image = request.files.get("image")

    if image:  
        image.save(f'app/static/img/uploads/{image.filename}')

    if content or image:  
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO blog(AccID, Content, Image) VALUES (%s, %s, %s)", (acc_id, content if content else None, image.filename if image else None))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('inner_page'))


def show_post_details(mysql):
    acc_id = session.get('AccID') 
    cur = mysql.connection.cursor()
    cur.execute("SELECT blog.blogid, blog.accid, blog.content, blog.image, user.username FROM blog INNER JOIN user ON user.accid = blog.accid WHERE blog.accid = %s ORDER BY blog.blogid DESC", (acc_id,))
    rows = cur.fetchall()  # Fetch all rows
    cur.close() 

    posts = []

    for row in rows:
        blogid = row[0]
        accid = row[1]
        content = row[2]  
        image = row[3]  
        username = row[4]  
        
        if image is not None:
            image_path = url_for('static', filename=f'img/uploads/{image}')        
        else:
            image_path = None

        post = {
            'content': content,
            'image': image_path,
            'accid': accid,
            'blogid' : blogid,
            'username' : username,
        }
        posts.append(post)
        
    return posts
       
def del_post(mysql):
  # Check if user is logged in, redirect to login if not
  if not session.get('logged_in'):
    return redirect(url_for('login_page'))

  # Extract blog ID and account ID from the form data
  blog_id = request.form.get('blogid')
  account_id = request.form.get('accid')

  try:
    # Connect to the database
    with mysql.connection.cursor() as cur:

      print(f"Deleting blog with ID: {blog_id} and account ID: {account_id}")  # Log for debugging

      # Execute the query with the actual blog and account IDs
      cur.execute("DELETE FROM blog WHERE blogid = %s AND accid = %s", (blog_id, account_id))  # Use tuple for parameters

      mysql.connection.commit()

      # Success message if deletion is successful
      return redirect(url_for('inner_page'))

  except mysql.connection.Error as err:
    # Handle database errors gracefully
    print(f"Error deleting blog post: {err}")



#hàm sửa
def update_post(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    try:
        blog_id = request.form.get('blogid')
        image = request.files.get('image')     
        content = request.form.get('content')    
        account_id = session.get('AccID')

        if image is not None and image.filename:
            image.save(f'app/static/img/uploads/{image.filename}')
            image_filename = image.filename
        else:
            image_filename = None

        with mysql.connection.cursor() as cur:
            # Update query (image first to potentially handle larger data earlier)
            update_query = "UPDATE blog SET image = %s, content = %s WHERE blogid = %s AND accid = %s"
            cur.execute(update_query, (image_filename, content, blog_id, account_id))

            mysql.connection.commit()

            # Success message
            return redirect(url_for('inner_page'))

    except mysql.connection.Error as err:
        print(f"Error updating blog post: {err}")
        return "Cập nhật không thành công. Vui lòng thử lại hoặc liên hệ quản trị viên."