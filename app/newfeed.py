from flask import Flask, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import time


app = Flask(__name__)
class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

users = {'user': User('user', 'password')}


def get_feed(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT blog.blogid, blog.accid, blog.content, blog.image, user.username FROM blog INNER JOIN user ON blog.accid = user.accid ORDER BY BlogID DESC")
    rows = cur.fetchall()
    cur.close()

    posts = []

    # Loop through fetched rows and populate 'posts' list
    for row in rows:
        blogid = row[0]
        accid = row[1]
        content = row[2]  
        image = row[3]  
        
        if image is not None:
            image_path = url_for('static', filename=f'img/uploads/{image}')
        else:
            image_path = None
        
        post = {
            'content': content,
            'image': image_path,
            'accid': accid,
            'blogid': blogid,
            'username': row[4]
        }
        posts.append(post)
    return posts

#hàm bình luận
def comment(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    
    acc_id = session.get('AccID')  # Lấy AccID từ phiên làm việc
    blog_id = request.form.get('blogid')
    comment = request.form.get('comment')

    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO comment(AccID, Comment) VALUES (%s, %s)", (acc_id, comment))
        cur.execute("SELECT LAST_INSERT_ID()")
        comment_id = cur.fetchone()[0]

        cur.execute("INSERT INTO blog_comment(BlogID, CommentID) VALUES (%s, %s)",(blog_id, comment_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('newfeed'))


#hàm show comment
def show_comment_details(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT comment.comment, blog_comment.blogID, user.Username, comment.commentID, comment.accID
        FROM comment
        INNER JOIN blog_comment ON comment.CommentID = blog_comment.CommentID
        INNER JOIN user ON user.AccID = comment.AccID
    """)
    comments = cur.fetchall()
    cur.close()

    comment_details = []

    for comment in comments:
        comment_text = comment[0].replace('\r\n', '<br>')  # Thay thế \r\n bằng <br>
        blogid = comment[1]
        username = comment[2]
        commentid = comment[3]
        accid = comment[4]
        
        comment_detail = {
            'comment': comment_text,
            'blogid': blogid,
            'username': username,
            'commentid': commentid,
            'accid': accid
        }
        comment_details.append(comment_detail)
        
    return comment_details

#hàm xóa bình luận
def del_comment_details(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    
    blogid = request.form.get('blogid')
    commentid = request.form.get('commentid')
    # print(blogid)
    # print(commentid)
    try:
        with mysql.connection.cursor() as cur:
            # Xóa bình luận từ bảng comment
            cur.execute("DELETE FROM comment WHERE CommentID = %s", (commentid,))
            # Xóa cặp (blogid, commentid) từ bảng blog_comment
            cur.execute("DELETE FROM blog_comment WHERE BlogID = %s AND CommentID = %s", (blogid, commentid))
            
            mysql.connection.commit()
            return redirect(url_for('newfeed'))
    except Exception:
        return "Đã xảy ra lỗi khi xóa bình luận"


#hàm sửa bình luận 
def update_comment(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
   
    commentid = request.form.get('commentid')
    # print(commentid)
    comment = request.form.get('comment')
    # print(comment)

    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute("UPDATE comment SET Comment = %s WHERE CommentID = %s", (comment, commentid))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('newfeed'))



#hàm like blog
def like(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    
    acc_id = session.get('AccID')
    blogid = request.form.get('blogid')

    if request.method == "POST":
        # likes = request.form['like']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO blog_like_test(BlogID, AccID, Likes) VALUES (%s, %s, %s)", (blogid, acc_id, True))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('newfeed'))



#hàm like set false
def del_like(mysql):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    
    acc_id = session.get('AccID')
    blogid = request.form.get('blogid')
    # likeid = request.form.get('likeid')
    try:
        with mysql.connection.cursor() as cur:
            # Xóa bình luận từ bảng comment
            cur.execute("DELETE FROM blog_like_test WHERE BlogID = %s AND AccID = %s", (blogid, acc_id))
            
            mysql.connection.commit()
            cur.close()
        return redirect(url_for('newfeed'))
    except Exception:
        return "false thất bại"
    


#hàm kiểm tra like
def show_like(mysql):
    acc_id = session.get('AccID')
    cur = mysql.connection.cursor()
    cur.execute("SELECT BlogID, AccID, Likes FROM blog_like_test WHERE AccID = %s  ", (acc_id, ))
    likes = cur.fetchall()
    cur.close()

    like_details = []

    for like in likes:
        blogid = like[0]
        accid = like[1]
        like = like[2]

        blog_like_aa = {
            'blogid' : blogid,
            'accid' : accid,
            'like' : like
            
        }
        like_details.append(blog_like_aa)
        
    return like_details
        

#count và hiển thị like ở newfeed
def count_like(mysql, blogid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(Likes) FROM blog_like_test WHERE BlogID = %s", (blogid,))
    row = cur.fetchone()
    count = row[0]
    mysql.connection.commit()
    cur.close()
    return count