from flask import *
from flask_sqlalchemy import SQLAlchemy 
import os

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customer.db'
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = "User"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	email = db.Column(db.String(255), unique=True)
	phone = db.Column(db.Integer,unique=True)
	password = db.Column(db.String(255))

	def __init__(self,name,email,mobile,password):
		self.name=name
		self.email=email
		self.mobile=mobile
		self.password=password

@app.route('/', methods=['POST','GET'])
def index():
	return render_template("homepage.html")

@app.route('/loginform')
def loginform():
	return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
	if request.method=='POST':
		if request.form['password']=='password' and request.form['username']=='admin':
			session['logged_in']=True
			return redirect(url_for('index'))
		else:
			session['logged_in']=False
			flash('wrong password!')
			return render_template("login.html")

@app.route('/signupform')
def signupform():
	return render_template('signup.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method=='POST':
		email=str(request.form['email'])
		name=str(request.form['name'])
		mobile=str(request.form['mobile'])
		password=str(request.form['password'])
		user=User(name,email,mobile,password)
		db.session.add(user)
		db.session.commit()
		return index()

if __name__=='__main__':
	app.secret_key=os.urandom(12)
	db.create_all()
	app.run(debug=True)