from flask import Flask,request,render_template,session,abort,flash
import os

app=Flask(__name__)

@app.route('/')
def index():
	return render_template("homepage.html")

@app.route('/login/', methods=['GET','POST'])
def login():
	if request.form['password']=='password' and request.form['username']=='admin':
		session['logged_in']=True
	else:
		flash('wrong password!')
	return render_template("login.html")

if __name__=='__main__':
	app.run(debug=True)