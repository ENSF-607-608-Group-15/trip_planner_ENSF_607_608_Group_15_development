from flask import session
from models.db_operations import DatabaseOperations
from sqlalchemy.exc import SQLAlchemyError
from openai import OpenAI
import os

GPT_CLIENT = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class VacationModel:
    def __init__(self, db_operations: DatabaseOperations):
        self.db_operations = db_operations


    def login(self, user_data):
        username = user_data.get("username")
        password = user_data.get("password")

        try:
            # Validate user with stored procedure
            validation_query = f"SELECT passHashMatch('{username}', '{password}')"
            user_valid = self.db_operations.execute_query(validation_query).scalar()

            if user_valid == 1:
                # If valid, fetch user ID
                user_id_query = (
                    f"SELECT userId FROM users "
                    f"WHERE userName ='{username}' limit 1"
                )
                user_id_result = self.db_operations.execute_query(user_id_query).fetchone()

                if user_id_result:
                    return {"id": user_id_result[0], "username": username}
                else:
                    return {"error": "User ID not found. Please try again."}
            else:
                return {"error": "Invalid username or password. Please try again."}

        except SQLAlchemyError as e:
            print(f"Database error during login: {e}")
            return {"error": "An error occurred. Please try again later."}


    def register_user(self, user_data):
        username = user_data['username']
        password = user_data['password']

        if not username or not password or " " in username or " " in password:
            return {"error": "Username and password cannot contain whitespace."}

        # Check if username is already taken
        query = f"SELECT COUNT(*) FROM users WHERE userName='{username}'"
        user_count = self.db_operations.execute_query(query).scalar()

        if user_count > 0:
            return {"error": "Username already exists."}

        # Add user to the database
        query = f"CALL AddUser('{username}', '{password}')"
        self.db_operations.call_procedure(query)
        return {"success": True}


    def validate_trip_details(self, trip_details):
        """ Check for any empty required fields in trip details and return a list of missing fields

        Parameters:
        trip_details (dict): Dictionary containing trip details

        Returns:
        list: List of strings representing the names of any required fields that are empty
        """
        missing_fields = []
        required_fields = {
            'departureCity': "Departure City",
            'beginDate': "Departure Date",
            'endDate': "Return Date",
            'location': "Desired Trip Location"
        }

        for field, display_name in required_fields.items():
            if not trip_details.get(field):
                missing_fields.append(display_name)
                
        return missing_fields


    def store_trip_query(self, trip_details):
        query = """
            CALL AddQueries(:userName, :beginDate, :endDate, :departureCity, 
                            :tripTheam, :location, :budget, :flying, :familyFriendly, 
                            :disabilityFriendly, :groupDiscount)
        """
        self.db_operations.call_procedure(query, trip_details)


    def generate_trip_itinerary(self, trip_details):
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
        Travel Dates: {trip_details['beginDate']} to {trip_details['endDate']}
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
        session['chatGPT_prompt'] = prompt

        try:
            response = GPT_CLIENT.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert vacation planner."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            return content.strip() if content else "No vacation plan available."
        except Exception as e:
            print(f"Error generating itinerary: {e}")
            return "Error generating itinerary."

    def store_trip_response(self, user_name, prompt, response):
        query = "CALL AddResponse(:userName, :query, :response)"
        param = {
            'userName': user_name,
            'query': prompt,
            'response': response.replace('\n', '<br>')  # or any formatting necessary
        }
        self.db_operations.call_procedure(query, param)

    def fetch_user_queries(self, user_id):
        return self.db_operations.load_queries_dicts_from_db(user_id)


    def fetch_user_vacation_plans(self, user_id):
        return self.db_operations.load_response_dicts_from_db(user_id)