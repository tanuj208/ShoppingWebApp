from flask import *
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from flask.ext.hashing import Hashing
import os

app=Flask(__name__)
Base = declarative_base()
hashing=Hashing(app)

class User(Base):
	__tablename__ = "user"

	id = Column('id', Integer,Sequence('user_id_seq'),primary_key=True)
	username=Column('username',String(255))
	name = Column('name',String(255))
	email = Column('email',String(255))
	mobile = Column('mobile',String(15))
	password = Column('password',String(25))

	def __repr__(self):
		return "<User(username='%s' name='%s', email='%s', mobile='%s', password='%s')>" %(self.username,self.name,self.email,self.mobile,self.password) 

engine=create_engine('sqlite:///user.db',echo=True)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
sqlsession = Session()

@app.route('/')
@app.route('/<username>')
def index(username=None):
	return render_template("homepage.html")

@app.route('/login', methods=['POST','GET'])
def login():
	if request.method=='POST':
		password=hashing.hash_value(str(request.form['password']),salt='abcd')
		username=str(request.form['username'])
		user = sqlsession.query(User).filter_by(username=username).first()
		if username=='' or hashing.check_value(password,'',salt='abcd'):
			return render_template("login.html",error="Fields can't be empty")
		if user is None:
			return render_template("login.html",error="Username does not exist!")
		elif hashing.check_value(user.password,password,salt='abcd'):
			sqlsession.add(user)
			sqlsession.commit()
			session['user']=user.name
			return redirect(url_for('index',name=user.name))
		else:
			return render_template("login.html",error="Wrong Password!")
	return render_template('login.html',error=None)

@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method=='POST':
		error=None
		user = User()
		user.username=str(request.form['username'])
		user.email=str(request.form['email'])
		user.name=str(request.form['name'])
		user.mobile=str(request.form['tel'])
		user.password=hashing.hash_value(str(request.form['password']),salt='abcd')
		confirm=hashing.hash_value(str(request.form['confirmation']),salt='abcd')

		if user.username=='' or user.email=='' or user.name=='' or user.mobile=='' or hashing.check_value(user.password,'',salt='abcd'):
			error="Field can't be empty"

		elif len(user.password)<8:
			error="Password should be more than 8 characters"

		elif confirm!=user.password:
			error="Passwords do not match"

		elif sqlsession.query(User).filter_by(username=user.username).first() is not None:
			error="Username already exists"

		elif sqlsession.query(User).filter_by(email=user.email).first() is not None:
			error="Email already exists"

		elif sqlsession.query(User).filter_by(mobile=user.mobile).first() is not None:
			error="Mobile number already exists"

		if error:
			return render_template('signup.html',error=error)

		sqlsession.add(user)
		sqlsession.commit()
		session['user']=user.username
		return redirect(url_for('index',username=user.username))
	return render_template('signup.html',error=None)

@app.route('/usertable')
def usertable():
	users = sqlsession.query(User).all()
	return render_template('table.html',rows=users,message="USERS ::")

if __name__=='__main__':
	app.secret_key=os.urandom(12)
	app.run(debug=True)