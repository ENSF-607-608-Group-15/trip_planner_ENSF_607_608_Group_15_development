import io
from flask import render_template, session
from models.vacation_model import VacationModel
import markdown
from weasyprint import HTML


class VacationController:
    def __init__(self, vacation_model: VacationModel):
        self.vacation_model = vacation_model

    def login_user(self, user_data):
        return self.vacation_model.login(user_data)

    def set_guest_session(self):
        session['user_id'] = 0
        session['user_name'] = "Guest"
        session['guest_mode'] = True

    def logout(self):
        session.clear()

    def sign_up_user(self, user_data):
        return self.vacation_model.register_user(user_data)

    def generate_trip_plan(self, trip_details):
        missing_details = self.vacation_model.validate_trip_details(
            trip_details)
        if missing_details:
            return {"error": "Missing fields: " + ", ".join(missing_details)}

        if session.get('user_name') != "Guest":
            self.vacation_model.store_trip_query(trip_details)

        plan = self.vacation_model.generate_trip_itinerary(trip_details)

        if session.get('user_name') != "Guest":
            self.vacation_model.store_trip_response(
                session['user_name'], session['chatGPT_prompt'], plan)

        session['formatted_plan'] = plan.replace('\n', '<br>')
        return {"plan": markdown.markdown(session['formatted_plan'])}

    def get_user_queries(self, user_id):
        return self.vacation_model.fetch_user_queries(user_id)

    def get_user_vacation_plans(self, user_id):
        return self.vacation_model.fetch_user_vacation_plans(user_id)

    def generate_pdf(self):
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
