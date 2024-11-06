from database import database
from flask import Flask, render_template_string, request, session, redirect, url_for
from flask.templating import render_template
from flask import request, session, send_file
from flask.json import jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from vacationdbclass import userClass, querieClass, chatGPTresponse
from markupsafe import Markup
from weasyprint import HTML
import io
import markdown


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


@app.route('/login', methods=['POST'])
def login():
    userName = request.form.get('usernameLogin')
    passHash = request.form.get('passwordLogin')
    if userName is None or passHash is None:
        return render_template('home.html', title=home_title, errorMessage="Please use a valid username or password")
    query = f"SELECT passHashMatch('{userName}', '{passHash}')"
    userValid = db1.query(query).scalar()
    if userValid == 1:
        # add user infomation  to session
        # covert user to userClass list
        query = (
            f"SELECT userId, userName FROM users "
            f"WHERE userName ='{userName}' "
            f"and passHash='{passHash}' limit 1"
        )
        user = db1.query(query)
        user = user.fetchall()
        # myUser = userClass(user[0][0], user[0][1], user[0][2]) # TODO: This variable "myUser" is unused
        session['user_id'] = user[0][0]
        session['user_name'] = user[0][1]
        # userList = [userClass(user[0][0], user[0][1], user[0][2])]
        # session['userName'] = myUser.userId
        # print(session['userName'])
        return render_template('home.html', Authenticated=True, Registered=True, Guest=False)
    else:
        return render_template('home.html', title=home_title, errorMessage="Please use a valid username or password")


@app.route('/guest', methods=['POST'])
def guest():
    session['user_id'] = 0
    session['user_name'] = "Guest"
    return render_template('home.html', Authenticated=True, Registered=True, Guest=True)
    
@app.route('/Logout',methods=['POST'])
def Logout():
    session.clear()
    return render_template('home.html',Authenticated=False,Registered=True, Guest=False)
    
@app.route('/SignUp',methods=['POST'])
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
        # Changed key to match plan() function
        'input_city': request.form.get('inputCity'),
        'departure_date': request.form.get('dDate'),
        'return_date': request.form.get('rDate'),
        'trip_theme': request.form.get('tripTheme'),
        'trip_location': request.form.get('tripLocation'),
        'trip_budget': request.form.get('tripBudget'),
        'no_flying': 'noFlying' in request.form,
        'disability_friendly': 'disabilityFriendly' in request.form,
        'family_friendly': 'familyFriendly' in request.form,
        'group_discounts': 'groupDiscount' in request.form,
    }

    # Store the trip details in the flask session
    session['trip_details'] = trip_details

    # Save to database
    connection = engine.raw_connection()
    query = (
        f"call AddQueries('{session['user_name']}', "
        f"'{trip_details['departure_date']}', "
        f"'{trip_details['return_date']}', "
        f"'{trip_details['input_city']}', "
        f"'{trip_details['trip_theme']}', "
        f"'{trip_details['trip_location']}', "
        f"{trip_details['trip_budget']}, "
        f"{int(trip_details['no_flying'])}, "
        f"{int(trip_details['family_friendly'])}, "
        f"{int(trip_details['disability_friendly'])}, "
        f"{int(trip_details['group_discounts'])})"
    )
    cursor = connection.cursor()
    cursor.execute(query)
    session['lastQueryID'] = cursor.fetchone()[0]
    connection.commit()
    cursor.close()

    # ChatGPT Integration
    preferences = []
    if trip_details['no_flying']:
        preferences.append("no air travel")
    if trip_details['disability_friendly']:
        preferences.append("disability friendly accommodations")
    if trip_details['family_friendly']:
        preferences.append("family friendly activities")
    if trip_details['group_discounts']:
        preferences.append("group discount options")

    prompt = f"""Create a detailed travel itinerary with the following specifications:
    Departure City: {trip_details['input_city']}
    Destination: {trip_details['trip_location']}
    Travel Dates: {trip_details['departure_date']} to {trip_details['return_date']}
    Theme: {trip_details['trip_theme']}
    Budget: {trip_details['trip_budget']}
    Special Requirements: {', '.join(preferences)}

    Please provide:
    1. Daily itinerary breakdown
    2. Recommended accommodations
    3. Must-see attractions and activities
    4. Transportation recommendations
    5. Estimated costs for major expenses
    6. Local tips and cultural considerations
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert vacation planner who creates detailed, personalized travel itineraries."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        session['vacation_plan'] = content.strip(
        ) if content else "No vacation plan available."

        # Format the vacation plan with proper line breaks
        session['formatted_plan'] = session['vacation_plan'].replace(
            '\n', '<br>')

        # Use parameterized query instead of f-string
        query = "call AddResponse(%s, %s, %s, %s)"
        cursor = connection.cursor()
        cursor.execute(
            query, (session['user_name'], session['lastQueryID'], prompt, session['formatted_plan']))
        connection.commit()
        cursor.close()

        return render_template('home.html',
                               title=home_title,
                               Authenticated=True,
                               Registered=True,
                               vacation_plan=markdown.markdown(session['formatted_plan']))
    except Exception as e:
        return render_template('home.html',
                               title=home_title,
                               Authenticated=True,
                               Registered=True,
                               error=f"Error with API call: {e}")


@app.route('/displayUserQueries', methods=['POST'])
def displayUserQueries():
    trips = db1.load_queries_dicts_from_db(session['user_id'])
    return render_template('home.html', trips=trips, title=home_title, Authenticated=True, Registered=True)


@app.route('/displayUserVacationPlans', methods=['POST'])
def displayUserVacationPlans():
    vacations = db1.load_response_dicts_from_db(session['user_id'])

    # Assuming vacation['vacation_plan'] contains the markdown text
    for vacation in vacations:
        vacation['response'] = markdown.markdown(vacation['response'])

    return render_template('home.html', vacations=vacations, title=home_title, Authenticated=True, Registered=True)


@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    file_name = f"itinerary_for_{session['user_name']}.pdf"
    html_content = render_template(
        'vacationPlan.html', vacation_plan=markdown.markdown(session['formatted_plan']))
    pdf_output = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_output)
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name=file_name, mimetype='application/pdf')


print(__name__)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)


@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return text
    return Markup(text.replace('\n', '<br>'))
