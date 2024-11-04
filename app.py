from flask import Flask, render_template, request, session, jsonify
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
# Sessions are for temporary storage of individual users.
app.secret_key = 'test123'

home_title = 'ENSF607/608 Vacation Planner'

@app.route('/', methods=['GET', 'POST'])
def generate_trip():
    if request.method == 'POST':
        # Collect user inputs into 'trip_details' dictionary
        trip_details = {
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
            'output_pdf': 'pdfOutput' in request.form
        }

        # Store the trip details in the flask session
        session['trip_details'] = trip_details
        #session['trip_details'] = trip_details

        return render_template('plan.html')
    
    return render_template('home.html')


@app.route('/plan', methods=['POST'])
def plan():
    print("\n\n\nIn plan Route\n\n\n")
    # Retrieve trip details from the flask session
    trip_details = session.get('trip_details', {})
    
    # For the yes/no preferences will need to append to end of the prompt
    # Chained if statements are ugly but not sure about better way to do this
    preferences = [] 
    if trip_details['no_flying']:
        preferences.append("no air travel")
    if trip_details['disability_friendly']:
        preferences.append("disability friendly accomodations")
    if trip_details['family_friendly']:
        preferences.append("family friendly activities")
    if trip_details['group_discounts']:
        preferences.append("group discount options")

    # API prompt engineering
    prompt = f"""Create a detailed travel itinerary with the following specifications:
    Departure City: {trip_details.get('input_city')}
    Destination: {trip_details.get('trip_location')}
    Travel Dates: {trip_details.get('departure_date')} to {trip_details.get('return_date')}
    Theme: {trip_details.get('trip_theme')}
    Budget: {trip_details.get('trip_budget')}
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
      ])
      content = response.choices[0].message.content
      print(f"\n\n\nCONTENT {content}\n\n\n")
      vacation_plan = content.strip() if content else "No vacation plan available."
      return render_template('plan.html', vacation_plan=vacation_plan)
    
    except Exception as e:
      print(f"Error with API call {e}")
      return render_template('plan.html', error=f"Error with API call: {e}")



# Test run
print(__name__)
if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True, port=3000)
