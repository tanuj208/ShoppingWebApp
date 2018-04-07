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
	email = Column('email',String(255),unique= True)
	mobile = Column('mobile',String(15),unique=True)
	password = Column('password',String(25))

	def __repr__(self):
		return "<User(name='%s', email='%s', mobile='%s', password='%s')>" %(self.name,self.email,self.mobile,self.password) 

engine=create_engine('sqlite:///user.db',echo=True)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
sqlsession = Session()

@app.route('/', methods=['POST','GET'])
def index(name=None,log=False):
	return render_template("homepage.html")

@app.route('/login', methods=['POST','GET'])
def login():
	if request.method=='POST':
		if request.form['password']=='password' and request.form['email']=='abc@abc.com':
			return index()
		else:
			flash('wrong password!')
			return render_template("login.html")
	return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method=='POST':
		user = User()
		user.email=str(request.form['email'])
		user.name=str(request.form['name'])
		user.mobile=str(request.form['tel'])
		user.password=str(request.form['password'])
		sqlsession.add(user)
		sqlsession.commit()
		session['user']=user.name
		return index()
	return render_template('signup.html')

@app.route('/usertable')
def usertable():
	users = sqlsession.query(User).all()
	return render_template('table.html',rows=users,message="USERS ::")

if __name__=='__main__':
	app.secret_key=os.urandom(12)
	app.run(debug=True)