from flask import Flask, render_template, url_for, request, session, redirect,Response
import pymongo
import json
from passlib.hash import pbkdf2_sha256
from functools import wraps

app = Flask(__name__)
client = pymongo.MongoClient('mongodb://localhost:27017/')
db=client.loginsys
app.secret_key='anukulisthekey'
class User:
    
    def register(self):
        user={
            'username':request.form['username'],
            'password':request.form['password']
        }
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        existing_user = db.users.find_one({'username':request.form['username']})
        if not existing_user:
            db.users.insert_one(user)
            session['username']=request.form['username']
            session['is_logged_in']=True
            return 1
        else:
            return 0
    
    def login(self):
        username=request.form.get('username')
        user =db.users.find_one({'username':username})
        print(username)
        print(user)
        if user:
            if pbkdf2_sha256.verify(request.form.get('password'), user['password']):
                return f'logged in as {session["username"]}'           
        return 'Invalid credentials'

def login_required(f):
  @wraps(f)
  def wrap():
    if 'logged_in' in session:
      return f()
    else:
      return redirect('/')
  
  return wrap

@app.route('/', methods=['GET'])
def home():
    return Response(
        response='The web application is running',
        status=200,
    )

@app.route('/register',methods=['GET','POST'])
def register():
    response= User().register()
    if response:
        return Response(
            response=json.dumps({"message":f"Successfully registered as {session['username']}"}),
            status=200
        )
    return Response(
            response=json.dumps({f"message":'Username already registered'}),
            status=400
        )

@app.route('/login',methods=['GET','POST'])
def login():
    return User().login()
    
@app.route('/dashboard',methods=['GET'])
@login_required
def dashboard():
    return 'Welcome to dashboard'
    

app.run(port=80,debug=True)