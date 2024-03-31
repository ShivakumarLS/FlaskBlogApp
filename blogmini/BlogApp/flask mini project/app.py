# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re,datetime


app = Flask(__name__)


app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'blogapp'

mysql = MySQL(app)

@app.route('/')
def home():
	return render_template('mainpage.html')

@app.route('/display',methods=['post','get'])
def display():
	return render_template('display.html')

@app.route('/postblog',methods=['POST','GET'])
def postblog():
	if request.method == 'POST' and 'blog_title' in request.form and 'blog_content' in request.form:
		title = request.form['blog_title']
		content = request.form['blog_content']
		time = datetime.datetime.now()
		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO blogdetails  VALUES (NULL,%s,%s,%s,%s)',(title,content,time,session['id'],))
		mysql.connection.commit()
		cur.close()
	return redirect(url_for('showall'))

@app.route('/showall',methods=['GET','POST'])
def showall():
	try:
		cur=mysql.connection.cursor()
		cur.execute('select blog_title,blog_content,username,blog_id from blogDetails as b inner join accounts as a on a.id=b.id')
		allblog=cur.fetchall()
		cur.close()
		return render_template("display.html",allblogs=allblog)
	except Exception as e:
		print(e)
		return "none"
	
@app.route('/edit',methods=['POST','GET'])
def edit():
	return render_template('edit.html')

@app.route('/update',methods=['POST','GET'])
def update():
	pass

@app.route('/auth',methods=['post','get'])
def auth():
	username = request.values.get('username')
	password = request.values.get('password')
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password))
	account = cursor.fetchone()
	if account:
		session['loggedin'] = True
		session['id'] = account['id']
		session['username'] = account['username']
		msg = 'Login success'
		return render_template('display.html', msg = session['username'])
	else:
		msg = 'Incorrect username / password !'
		return render_template('login.html', msg = msg)
	# return render_template('login.html',msg = "Invalid Credentias")
	
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	return render_template('login.html', msg = msg)

@app.route('/delete/<id>',methods=['post','get'])
def delete(id):
	try:
		cur=mysql.connection.cursor()
		cur.execute('delete from blogDetails where blog_id = %d',id)
		cur.execute('select blog_title,blog_content,username,blog_id from blogDetails as b inner join accounts as a on a.id=b.id')
		allblog=cur.fetchall()
		cur.close()
		return redirect(url_for(showall,allblogs = allblog))
	except Exception as e:
		print(e)
		return "none"
@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return render_template('mainpage.html')

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

app.run(debug=True)