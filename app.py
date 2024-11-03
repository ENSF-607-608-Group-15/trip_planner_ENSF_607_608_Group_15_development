from flask import Flask, render_template_string, request, session, redirect, url_for
from flask.templating import render_template
from flask import request
from flask.json import jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from vacationdbclass import userClass, querieClass, chatGPTresponse


load_dotenv() 

# Put your OpenAI API key here
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# To make database related code work, go to database.py to add
# MySQL connection string and uncomment the code below
from database import database

db1 = database()

trips = db1.load_queries_dicts_from_db()


# App starts here

app = Flask(__name__)

home_title = 'ENSF607/608 Planning a Vacation'

# 1. consider change face icon
@app.route('/')
def hello_world():
  # to use database realted code, follow the instructions on line 11
  #jobs = database().load_jobs_dicts_from_db()
  return render_template('home.html', trips=trips, title=home_title)


@app.route('/plan', methods=['POST'])
def plan():
    country = request.form['country']
    vacation_type = request.form['vacation_type']

    # New ChatGPT API prompt
    prompt = f"Suggest a {vacation_type} vacation in {country}. Provide suggestions of things to do."

    # Use ChatCompletion (ChatGPT API) for the new interface
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a vacation planner."},
        {"role": "user", "content": prompt}
    ])
    content = response.choices[0].message.content
    vacation_plan = content.strip() if content else "No vacation plan available."

    return render_template('plan.html', vacation_plan=vacation_plan)

@app.route('/login',methods=['get'])
def login():
    userName = request.args.get('username')
    print (userName)
    passHash = request.args.get('password')
    print (passHash)
    if userName is None or passHash is None:
        return render_template('home.html', Authenticated="Invalid input") 
    query = f"SELECT * FROM users WHERE userName ='{userName}' and passHash='{passHash}' limit 1"
    myDb=database()
    user = myDb.query(query)
    print(user)
    if user:
        
        # add user infomation  to session
        # covert user to userClass list
        user=user.fetchall()
        myUser = userClass(user[0][0], user[0][1], user[0][2])
        print(myUser)
        # userList = [userClass(user[0][0], user[0][1], user[0][2])]
        # session['userName'] = myUser.userId
        # print(session['userName'])
        return render_template('home.html',Authenticated=True)
    else:
        return render_template('home.html', Authenticated="Invalid User Name or Password")
    
# Test run
print(__name__)
if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True, port=3000)
