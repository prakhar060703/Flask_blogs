from flask import Flask, render_template, request,flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user,UserMixin,logout_user,current_user
from datetime import datetime

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SECRET_KEY']= 'thisissecret'
db = SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)



class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    FirstName= db.Column(db.String(20), nullable=False)
    LastName= db.Column(db.String(20), nullable=False)
    email= db.Column(db.String(20),   nullable=False)
    password= db.Column(db.String(8), nullable=False)
    username= db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
class Blog(db.Model):
    blog_id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(80),nullable=False)
    author=db.Column(db.String(30),nullable=False)
    content=db.Column(db.Text(),nullable=False)
    pub_date=db.Column(db.DateTime(),nullable=False,default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/main")
def main():
    return render_template("main.html")

@app.route("/")
def index():
    data=Blog.query.all()
    return render_template("index.html",data=data)

@app.route("/register", methods=['GET','POST'])
def register():
   if request.method=='POST':
      FirstName= request.form.get('FirstName')
      LastName= request.form.get('LastName')
      email= request.form.get('email')
      password= request.form.get('password')
      username= request.form.get('username') 
      
      user=User(FirstName=FirstName, LastName=LastName,email=email,password=password,username=username)
      db.session.add(user)
      db.session.commit()
      flash('user has been registered sucessfully','success')
      return redirect('/login')

   return render_template("register.html")


@app.route("/login", methods=['GET','POST'])
def login():
   if request.method=='POST':
        username= request.form.get('username')
        password= request.form.get('password')
        user=User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect('/')
        else:
            flash('Invalid username or password', 'danger')
            return redirect('/login')
   return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')
@app.route("/blogout",methods=['GET','POST'])
def blogpost():
    if request.method=='POST':
        title= request.form.get('title')
        author=request.form.get('author')
        content=request.form.get('content')
        blog=Blog(title=title,author=author,content=content)
        db.session.add(blog)
        db.session.commit()
        flash('Your post has been submitted successfully','success')
        return redirect('/')
    return render_template('blog.html')

@app.route("/blog_detail/<int:id>",methods=['GET','POST'])
def blogdetail(id):
    blog = Blog.query.get(id)
    return render_template('blog_detail.html',blog=blog)

@app.route("/delete/<int:id>",methods=['GET','POST'])
def delete_post(id):
    blog = Blog.query.get(id)
    if current_user.username == blog.author or current_user.username == "rohit@6788":
        db.session.delete(blog)
        db.session.commit()
        flash('Post has been deleted', 'success')
    else:
        flash("You don't have permission to delete this post", 'danger')
    return redirect('/')



@app.route("/edit/<int:id>",methods=['GET','POST'])
def edit_post(id):
    blog = Blog.query.get(id)
    if current_user.username != blog.author:
        flash("You don't have permission to edit this post", 'danger')
        return redirect('/')
    if request.method=='POST':
        blog.title=request.form.get('title')
        blog.author=request.form.get('author')
        blog.content=request.form.get('content')
        db.session.commit()
        flash('Post has been updated','success')
        return redirect('/')
    return render_template('edit.html', blog=blog)

if __name__=="__main__":
    app.run(debug=True)