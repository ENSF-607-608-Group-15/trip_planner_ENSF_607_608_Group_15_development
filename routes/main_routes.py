from flask import Blueprint, render_template, request, session, send_file
from controllers.vacation_controller import VacationController
from models.db_connection import DatabaseConnection
from models.db_operations import DatabaseOperations
from models.vacation_model import VacationModel

db_connection = DatabaseConnection()
db_operations = DatabaseOperations(db_connection.get_engine())
vacation_model = VacationModel(db_operations)
vacation_controller = VacationController(vacation_model)

main_routes = Blueprint('main_routes', __name__)

HOME_TITLE = 'Vacation Planner'

@main_routes.route('/')
def home():
    return render_template('home.html', title=HOME_TITLE)


@main_routes.route('/login', methods=['POST'])
def login():
    """ Authenticate user login by verifying username and password

    Returns:
    Takes the user to home page if login is successful, or displays error message if it fails
    """
    username = request.form.get('usernameLogin')
    password = request.form.get('passwordLogin')

    if not username or not password:
        error_message = "Please enter a valid username and password."
        return render_template('home.html', title=HOME_TITLE, ErrorMessageLogin=error_message)

    user_data = {"username": username, "password": password}
    login_response = vacation_controller.login_user(user_data)

    if login_response.get("error"):
        return render_template('home.html', title=HOME_TITLE, ErrorMessageLogin=login_response["error"])
    
    session['user_name'] = login_response['username']
    session['user_id'] = login_response['id']
    session['guest_mode'] = False

    return render_template('home.html', Authenticated=True, Registered=True)


@main_routes.route('/guest', methods=['POST'])
def guest():
    """ Log in a guest user and set the session to guest mode

    Returns:
    Takes the user to the home page with guest access
    """
    vacation_controller.set_guest_session()
    return render_template('home.html', Authenticated=True, Registered=True)


@main_routes.route('/Logout', methods=['POST'])
def Logout():
    """ Log out the current user

    Returns:
    Takes the user back to the login page
    """
    vacation_controller.logout()
    return render_template('home.html', Authenticated=False, Registered=True)


@main_routes.route('/SignUp', methods=['POST'])
def SignUp():
    """ Register a new user by adding their info to the database

    Returns:
    str: Take the user to the home page after successful signup
    """
    user_data = {
        'username': request.form.get('usernameSignUp'),
        'password': request.form.get('passwordSignUp')
    }
    sign_up = vacation_controller.sign_up_user(user_data)
    if "error" in sign_up:
        return render_template('home.html', title=HOME_TITLE, ErrorMessageSignUp=sign_up["error"])
    return render_template('home.html', title=HOME_TITLE)


@main_routes.route('/trip_generator', methods=['POST'])
def generate_trip():
    """ Generate a vacation plan based on user input using LLM

    Returns:
    Load home page with generated vacation plan, or an error message if failure
    """
    trip_details = {
        'userName': session.get('user_name'),
        'beginDate': request.form.get('dDate'),
        'endDate': request.form.get('rDate'),
        'departureCity': request.form.get('inputCity'),
        'location': request.form.get('tripLocation'),
        'tripTheam': request.form.get('tripTheme'),
        'budget': request.form.get('tripBudget'),
        'flying': 'noFlying' in request.form,
        'familyFriendly': 'familyFriendly' in request.form,
        'disabilityFriendly': 'disabilityFriendly' in request.form,
        'groupDiscount': 'groupDiscount' in request.form,
    }
    
    vacation_plan = vacation_controller.generate_trip_plan(trip_details)
    if "error" in vacation_plan:
        return render_template('home.html', title=HOME_TITLE, Authenticated=True, Registered=True, error=vacation_plan["error"])

    return render_template('home.html', title=HOME_TITLE, Authenticated=True, Registered=True, vacation_plan=vacation_plan["plan"])


@main_routes.route('/displayUserQueries', methods=['POST'])
def displayUserQueries():
    """ Retrieve and display users previous trip queries

    Returns:
    Load home page with a table of previous trip settings
    """
    user_id = session.get('user_id')
    trips = vacation_controller.get_user_queries(user_id)
    return render_template('home.html', trips=trips, title=HOME_TITLE, Authenticated=True, Registered=True)


@main_routes.route('/displayUserVacationPlans', methods=['POST'])
def displayUserVacationPlans():
    """ Retrieve and display users previous vacation plans

    Returns:
    Load page with a table of previous vacation plans
    """
    user_id = session.get('user_id')
    vacations = vacation_controller.get_user_vacation_plans(user_id)
    return render_template('home.html', vacations=vacations, title=HOME_TITLE, Authenticated=True, Registered=True)


@main_routes.route('/download_pdf', methods=['GET'])
def download_pdf():
    """ Generate a PDF of the users vacation plan for downloading

    Returns:
    File: A PDF file of the vacation plan
    """
    pdf_data = vacation_controller.generate_pdf()

    if "error" in pdf_data:
        return render_template('home.html', error=pdf_data["error"], title="Vacation Planner")

    return send_file(
        pdf_data["pdf_file"],
        as_attachment=True,
        download_name=pdf_data["file_name"],
        mimetype='application/pdf'
    )
