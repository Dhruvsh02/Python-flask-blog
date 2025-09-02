from flask import Flask , render_template , session , redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail 
from werkzeug.utils import secure_filename
from flask import request
import json
import os
import math


with open('config.json', 'r') as c:
    params = json.load(c)["params"]


local_server = True
app = Flask(__name__)

app.secret_key = 'aditi-2109'

app.config['UPLOAD_FOLDER'] = params['upload_location']

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['app_password']
)
mail = Mail(app)

if (local_server):  
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contacts(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    Phone_no = db.Column(db.String(15), unique=True ,nullable=False)
    Message = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)

class Posts(db.Model):
    S_no = db.Column(db.Integer, primary_key=True)
    Tittle = db.Column(db.String(50), nullable=False)
    Subtittle = db.Column(db.String(120) ,nullable=False)
    Slug = db.Column(db.String(21), unique=True, nullable=False)
    Content = db.Column(db.String(120) ,nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    Img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))
    #[0:params['no_of_posts']] 
    # pagination logic
    page = request.args.get('page',type = int)
    if (not page or page < 1):
        page = 1
    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    # first page
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    # last page
    elif page == last :
        prev = "/?page=" + str(page - 1)
        next = "#"
     # middle page
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    
    return render_template("index.html", params=params , posts = posts,prev = prev, next = next)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post = Posts.query.filter_by(Slug = post_slug).first() 
    return render_template("post.html" , params=params , post = post) 


@app.route("/about")
def about():
    return render_template("about.html" , params=params)

@app.route("/edit/<string:S_no>",methods = ['GET', 'POST'])
def edit(S_no):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            tittle = request.form.get('tittle')
            subtittle = request.form.get('subtittle')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')

            if S_no == '0':
                post = Posts(Tittle=tittle, Subtittle=subtittle, Slug=slug, Content=content, Img_file=img_file, Date=datetime.now())
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(S_no=S_no).first()
                post.Tittle = tittle
                post.Subtittle = subtittle
                post.Slug = slug
                post.Content = content
                post.Img_file = img_file
                db.session.commit()
                return redirect(f'/Edit/' + S_no)

        post = Posts.query.filter_by(S_no=S_no).first()
        return render_template("edit.html", params=params, post=post)

    return "You are not authorized to view this page"



@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    # If already logged in, show dashboard
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template("dashboard.html", params=params, posts=posts)

    # If login form is submitted
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            # Set session and show dashboard
            session['user'] = username
            posts = Posts.query.all()
            return render_template("dashboard.html", params=params, posts=posts)

    # If not logged in, show login page
    return render_template("login.html", params=params)


@app.route("/uploader",methods = ['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "File Uploaded Successfully"


@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect('/dashboard')

@app.route("/delete/<string:S_no>",methods = ['GET', 'POST'])
def delete(S_no):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(S_no=S_no).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')
    return "You are not authorized to delete this post"



@app.route("/contact",methods = ['GET', 'POST'])
def contact():
   if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone_no = request.form.get('phone_no')
        message = request.form.get('message')

        entry = Contacts(Name=name, email=email, Phone_no=phone_no, Message=message, Date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        
        mail.send_message('New Message from Adhruvana' + name ,
                           sender = params['gmail_user'],
                           recipients = [params['gmail_user']], 
                           body = message + "\n" + phone_no
                           )
        return "Form submitted successfully!" 
   
   return render_template("contact.html" , params=params)

if __name__ == "__main__":
    app.run(debug=True)

    