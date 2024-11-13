import io
from flask import render_template, session
from models.vacation_model import VacationModel
import markdown
from weasyprint import HTML


class VacationController:
    """
    Controller class to manage vacation-related operations.

    This class interfaces with the VacationModel to perform actions such as
    user login, session management, trip planning, and PDF generation.
    """
    def __init__(self, vacation_model: VacationModel):
        """
        Initialize the VacationController with a VacationModel instance.

        Args:
            vacation_model (VacationModel): An instance of VacationModel to handle vacation-related operations.
        """
        self.vacation_model = vacation_model

    def login_user(self, user_data):
        """
        Log in a user using provided credentials.

        Args:
            user_data (dict): A dictionary containing user credentials.

        Returns:
            dict: A response from the VacationModel's login method.
        """
        return self.vacation_model.login(user_data)

    def set_guest_session(self):
        """
        Set the session for a guest user.
        """
        session['user_id'] = 0
        session['user_name'] = "Guest"
        session['guest_mode'] = True

    def logout(self):
        """
        Log out the current user.
        """
        session.clear()

    def sign_up_user(self, user_data):
        """
        Register a new user with the provided data.

        Args:
            user_data (dict): A dictionary containing user registration details.

        Returns:
            dict: A response from the VacationModel's register_user method.
        """
        return self.vacation_model.register_user(user_data)

    def generate_trip_plan(self, trip_details):
        """
        Generate a trip plan based on the provided details.

        Args:
            trip_details (dict): A dictionary containing trip details.

        Returns:
            dict: A dictionary containing the generated trip plan or an error message if details are missing.
        """
        missing_details = self.vacation_model.validate_trip_details(
            trip_details)
        if missing_details:
            return {"error": "Missing fields: " + ", ".join(missing_details)}

        if session.get('user_id') != 0:
            self.vacation_model.store_trip_query(trip_details)

        plan = self.vacation_model.generate_trip_itinerary(trip_details)

        if session.get('user_id') != 0:
            self.vacation_model.store_trip_response(
                session['user_name'], session['chatGPT_prompt'], plan)

        session['formatted_plan'] = plan.replace('\n', '<br>')
        return {"plan": markdown.markdown(session['formatted_plan'])}

    def get_user_queries(self, user_id):
        """
        Retrieve previous trip queries for a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of user queries from the VacationModel.
        """
        return self.vacation_model.fetch_user_queries(user_id)

    def get_user_vacation_plans(self, user_id):
        """
        Retrieve previous vacation plans for a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of user vacation plans from the VacationModel.
        """
        return self.vacation_model.fetch_user_vacation_plans(user_id)

    def generate_pdf(self):
        """
        Generate a PDF of the current vacation plan.

        Returns:
            dict: A dictionary containing the PDF file and its name, or an error message if no plan is available.
        """
        if 'formatted_plan' not in session:
            return {"error": "No vacation plan available for PDF generation."}

        html_content = render_template(
            'vacationPlan.html',
            vacation_plan=markdown.markdown(session['formatted_plan'])
        )

        pdf_output = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_output)
        pdf_output.seek(0)

        file_name = f"itinerary_for_{session.get('user_name', 'Guest')}.pdf"

        # Return file data in a dictionary to allow route handling of response
        return {
            "pdf_file": pdf_output,
            "file_name": file_name
        }
