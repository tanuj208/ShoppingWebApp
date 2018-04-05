from flask import *
import os

app=Flask(__name__)

@app.route('/')
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

if __name__=='__main__':
	app.secret_key=os.urandom(12)
	app.run(debug=True)