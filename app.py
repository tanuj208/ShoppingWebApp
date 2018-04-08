from flask import *
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
import os

app=Flask(__name__)
Base = declarative_base()

class User(Base):
	__tablename__ = "user"

	id = Column('id', Integer,Sequence('user_id_seq'),primary_key=True)
	name = Column('name',String(255))
	email = Column('email',String(255))
	mobile = Column('mobile',String(15))
	password = Column('password',String(25))

	def __repr__(self):
		return "<User(name='%s', email='%s', mobile='%s', password='%s')>" %(self.name,self.email,self.mobile,self.password) 

engine=create_engine('sqlite:///user.db',echo=True)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
sqlsession = Session()

@app.route('/')
@app.route('/<name>')
def index(name=None):
	return render_template("homepage.html")

@app.route('/login', methods=['POST','GET'])
def login():
	if request.method=='POST':
		password=str(request.form['password'])
		email=str(request.form['email'])
		user = sqlsession.query(User).filter_by(email=email).first()
		if email=='' or password=='':
			return render_template("login.html",error="Fields can't be empty")
		if user is None:
			return render_template("login.html",error="Email does not exist!")
		elif user.password==password:
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
		user.email=str(request.form['email'])
		user.name=str(request.form['name'])
		user.mobile=str(request.form['tel'])
		user.password=str(request.form['password'])
		confirm=str(request.form['confirmation'])

		if user.email=='' or user.name=='' or user.mobile=='' or user.password=='':
			error="Field can't be empty"

		elif len(user.password)<8:
			error="Password should be more than 8 characters"

		elif confirm!=user.password:
			error="Passwords do not match"

		elif sqlsession.query(User).filter_by(email=user.email).first() is not None:
			error="Email exists"

		elif sqlsession.query(User).filter_by(mobile=user.mobile).first() is not None:
			error="Mobile number exists"

		if error:
			return render_template('signup.html',error=error)

		sqlsession.add(user)
		sqlsession.commit()
		session['user']=user.name
		return redirect(url_for('index',name=user.name))
	return render_template('signup.html',error=None)

@app.route('/usertable')
def usertable():
	users = sqlsession.query(User).all()
	return render_template('table.html',rows=users,message="USERS ::")

if __name__=='__main__':
	app.secret_key=os.urandom(12)
	app.run(debug=True)