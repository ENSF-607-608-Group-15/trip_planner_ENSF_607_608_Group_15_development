from flask import Flask
from flask.templating import render_template
from flask import request
from flask.json import jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

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

home_title = 'ENSF607/608 Vacation Planner'

@app.route('/', methods=['GET', 'POST'])
def generate_trip():
    if request.method == 'POST':
        input_city = request.form.get('inputCity')
        departure_date = request.form.get('iDate')
        return_date = request.form.get('rDate')
        trip_theme = request.form.get('tripTheme')
        trip_location = request.form.get('tripLocation')
        trip_budget = request.form.get('tripBudget')
        no_flying = 'noFlying' in request.form
        disability_friendly = 'disabilityFriendly' in request.form
        family_friendly = 'familyFriendly' in request.form
        group_discounts = 'groupDiscount' in request.form
        output_pdf = 'pdfOutput' in request.form
        
        print(input_city)
    
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


# Test run
print(__name__)
if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True, port=3000)
