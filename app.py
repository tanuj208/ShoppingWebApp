from flask import *
from sqlalchemy import *
import os

engine=create_engine('sqlite:///:memory:',echo=True)

app=Flask(__name__)
metadata=MetaData()

users=Table('Users',metadata,
	Column('id',Integer,Sequence('user_id_seq'),primary_key=True),
	Column('name',String(255)),
	Column('email',String(255)),
	Column('mobile',String(15)),
	Column('password',String(25))
	)
metadata.create_all(engine)

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
		mobile=str(request.form['tel'])
		password=str(request.form['password'])
		ins=users.insert().values(name=name,email=email,mobile=mobile,password=password)
		conn=engine.connect()
		metadata.create_all(engine)
		conn.execute(ins)
		return index()

if __name__=='__main__':
	app.secret_key=os.urandom(12)
	app.run(debug=True)