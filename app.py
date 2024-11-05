from database import database
from flask import Flask, render_template_string, request, session, redirect, url_for
from flask.templating import render_template
from flask import request, session
from flask.json import jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from vacationdbclass import userClass, querieClass, chatGPTresponse


load_dotenv()

# OpenAI API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Database connection
db1 = database()
engine = db1.engine

# App starts here
app = Flask(__name__)
app.config['SECRET_KEY'] = "vacationplan"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
home_title = 'ENSF607/608 Planning a Vacation'

# 1. consider change face icon


@app.route('/')
def home():
    return render_template('home.html', title=home_title)


@app.route('/plan', methods=['POST'])
def plan():
    country = request.form['country']
    vacation_type = request.form['vacation_type']

    # New ChatGPT API prompt
    prompt = f"Suggest a {vacation_type} vacation in {country}. Provide suggestions of things to do."

    # Use ChatCompletion (ChatGPT API) for the new interface
    response = client.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=[
                                                  {"role": "system",
                                                      "content": "You are a vacation planner."},
                                                  {"role": "user",
                                                      "content": prompt}
                                              ])
    content = response.choices[0].message.content
    vacation_plan = content.strip() if content else "No vacation plan available."

    return render_template('plan.html', vacation_plan=vacation_plan)


@app.route('/login', methods=['POST'])
def login():
    userName = request.form.get('usernameLogin')
    print(userName)
    passHash = request.form.get('passwordLogin')
    print(passHash)
    if userName is None or passHash is None:
        return render_template('home.html', title=home_title)
    query = f"SELECT passHashMatch('{userName}', '{passHash}')"
    userValid = db1.query(query).scalar()
    print(userValid)
    if userValid == 1:
        # add user infomation  to session
        # covert user to userClass list
        query = f"SELECT * FROM users WHERE userName ='{userName}' and passHash='{passHash}' limit 1"
        user = db1.query(query)
        user = user.fetchall()
        # myUser = userClass(user[0][0], user[0][1], user[0][2]) # TODO: This variable "myUser" is unused
        session['user_id'] = user[0][0]
        session['user_name'] = user[0][1]
        print(session['user_id'])
        # userList = [userClass(user[0][0], user[0][1], user[0][2])]
        # session['userName'] = myUser.userId
        # print(session['userName'])
        return render_template('home.html', Authenticated=True, Registered=True)
    else:
        return render_template('home.html', title=home_title)
@app.route('/Guest',methods=['get'])
def Guestlogin():
    session['user_id'] = 0
    session['user_name'] = "G"
    return render_template('home.html',Authenticated=True,Registed=True)
@app.route('/Logout',methods=['get'])
def Logout():
    session.clear()
    
    return render_template('home.html',Authenticated=False,Registed=True)
@app.route('/SignUp',methods=['get'])
def SignUp():
    userName = request.form.get('usernameSignUp')
    print(userName)
    passHash = request.form.get('passwordSignUp')
    print(passHash)
    if userName is None or passHash is None:
        return render_template('home.html', title=home_title)
    connection = engine.raw_connection()
    query = f"call AddUser('{userName}', '{passHash}')"
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()
    print('user added')
    return render_template('home.html', title=home_title)


"""
    if user:
        
        # add user infomation  to session
        # covert user to userClass list
        
        print(user)
        # userList = [userClass(user[0][0], user[0][1], user[0][2])]
        # session['userName'] = myUser.userId
        # print(session['userName'])
        return render_template('home.html',Registed=True)
    else:
        return render_template('home.html', Registed=False,ErrorMessageSignUp="Not Success!")
"""


@app.route('/trip_generator', methods=['POST'])
def generate_trip():
    # Collect user inputs into 'trip_details' dictionary
    trip_details = {
        'departure_city': request.form.get('inputCity'),
        'departure_date': request.form.get('dDate'),
        'return_date': request.form.get('rDate'),
        'trip_theme': request.form.get('tripTheme'),
        'trip_location': request.form.get('tripLocation'),
        'trip_budget': request.form.get('tripBudget'),
        'no_flying': 'noFlying' in request.form,
        'disability_friendly': 'disabilityFriendly' in request.form,
        'family_friendly': 'familyFriendly' in request.form,
        'group_discounts': 'groupDiscount' in request.form,
        'output_pdf': 'pdfOutput' in request.form
    }

    # Store the trip details in the flask session
    session['trip_details'] = trip_details

    connection = engine.raw_connection()
    query = f"call AddQueries({session['user_id']}, '{session['trip_details']['departure_date']}', '{session['trip_details']['return_date']}', '{session['trip_details']['departure_city']}', '{session['trip_details']['trip_theme']}', '{session['trip_details']['trip_location']}', {session['trip_details']['trip_budget']}, {int(session['trip_details']['no_flying'])}, {int(session['trip_details']['family_friendly'])}, {int(session['trip_details']['disability_friendly'])}, {int(session['trip_details']['output_pdf'])}, {int(session['trip_details']['group_discounts'])})"
    cursor = connection.cursor()
    cursor.execute(query)
    session['lastQueryID'] = cursor.fetchone()[0]
    print(session['lastQueryID'])
    connection.commit()
    cursor.close()
    print('query added')

    return render_template('home.html', title=home_title, Authenticated=True, Registered=True)


@app.route('/displayUserQueries', methods=['POST'])
def displayUserQueries():
    trips = db1.load_queries_dicts_from_db(session['user_id'])
    return render_template('home.html', trips=trips, title=home_title, Authenticated=True, Registered=True)


print(__name__)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)
