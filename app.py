from database import database
from flask import Flask, render_template_string, request, session, redirect, url_for, request, session, send_file
from flask.templating import render_template
from flask.json import jsonify
from openai import OpenAI
from dotenv import load_dotenv
from weasyprint import HTML
import os
import io
import re
import markdown

load_dotenv()

# OpenAI API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Database connection
db1 = database()

# App starts here
app = Flask(__name__)
app.config['SECRET_KEY'] = "vacationplan"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
home_title = 'Vacation Planner'

@app.route('/')
def home():
    return render_template('home.html', title=home_title)

@app.route('/login', methods=['POST'])
def login():
    session['user_name'] = request.form.get('usernameLogin')
    passHash = request.form.get('passwordLogin')
    if session['user_name'] is None or passHash is None:
        error_message = "Please enter a valid username and password."
        return render_template('home.html', title=home_title, ErrorMessageLogin=error_message)
    query = f"SELECT passHashMatch('{session['user_name']}', '{passHash}')"
    userValid = db1.query(query).scalar()
    if userValid == 1:
        # add user information  to session
        query = (
            f"SELECT userId FROM users "
            f"WHERE userName ='{session['user_name']}' limit 1"
        )
        user = db1.query(query)
        user = user.fetchall()
        session['user_id'] = user[0][0]
        session['guest_mode'] = False
        return render_template('home.html', Authenticated=True, Registered=True)
    else:
        error_message = "Please enter a valid username and password."
        return render_template('home.html', title=home_title, ErrorMessageLogin=error_message)

@app.route('/guest', methods=['POST'])
def guest():
    session['user_id'] = 0
    session['user_name'] = "Guest"
    session['guest_mode'] = True
    return render_template('home.html', Authenticated=True, Registered=True)


@app.route('/Logout', methods=['POST'])
def Logout():
    session.clear()
    return render_template('home.html', Authenticated=False, Registered=True)


@app.route('/SignUp', methods=['POST'])
def SignUp():
    userName = request.form.get('usernameSignUp')
    passHash = request.form.get('passwordSignUp')
    whitespace_pattern = r"\s"
    if not userName or not passHash or re.search(whitespace_pattern, userName) or re.search(whitespace_pattern, passHash):
        error_message = "Username and password cannot contain whitespaces."
        return render_template('home.html', title=home_title, ErrorMessageSignUp=error_message)
    query = f"SELECT COUNT(*) FROM users WHERE userName='{userName}'"
    user_count = db1.query(query).scalar()
    if user_count == 0:
        query = f"call AddUser('{userName}', '{passHash}')"
        db1.callprocedure(query)
        return render_template('home.html', title=home_title)
    else:
        error_message = "Please enter a valid username and password."
        return render_template('home.html', title=home_title, ErrorMessageSignUp=error_message)


@app.route('/trip_generator', methods=['POST'])
def generate_trip():
    # Collect user inputs into 'trip_details' dictionary
    trip_details = {
        'userName' : session['user_name'],
        'beginDate': request.form.get('dDate'),
        'endDate': request.form.get('rDate'),
        'departureCity': request.form.get('inputCity'),
        'location': request.form.get('tripLocation'),
        'tripTheam': request.form.get('tripTheme'),
        'budget': float(request.form.get('tripBudget')),
        'flying': int('noFlying' in request.form),
        'familyFriendly': int('familyFriendly' in request.form),
        'disabilityFriendly': int('disabilityFriendly' in request.form),
        'groupDiscount': int('groupDiscount' in request.form),
    }

    # Skip database storage for guest users
    if session['user_name'] != "Guest":
        # Save to database
        query = """
                call AddQueries(:userName, :beginDate, :endDate, :departureCity, :tripTheam, :location, 
                                :budget, :flying, :familyFriendly, :disabilityFriendly, :groupDiscount
                )
                """
        db1.callprocedure_param(query, trip_details)

    # ChatGPT Integration
    preferences = []
    if trip_details['flying']:
        preferences.append("no air travel")
    if trip_details['disabilityFriendly']:
        preferences.append("disability friendly accommodations")
    if trip_details['familyFriendly']:
        preferences.append("family friendly activities")
    if trip_details['groupDiscount']:
        preferences.append("group discount options")

    prompt = f"""Create a detailed travel itinerary with the following specifications:
    Departure City: {trip_details['departureCity']}
    Destination: {trip_details['location']}
    Travel Dates: {trip_details['departureCity']} to {trip_details['endDate']}
    Theme: {trip_details['tripTheam']}
    Budget: {trip_details['budget']}
    Special Requirements: {', '.join(preferences)}
    No more than 700 words.

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
        session['vacation_plan'] = content.strip() if content else "No vacation plan available."
        session['formatted_plan'] = session['vacation_plan'].replace('\n', '<br>')

        # Skip response storage for guest users
        if session['user_name'] != "Guest":
            query = "call AddResponse(:userName, :query, :response)"
            param = {'userName' : session['user_name'], 'query' : prompt, 'response' : session['formatted_plan']}
            db1.callprocedure_param(query, param)
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