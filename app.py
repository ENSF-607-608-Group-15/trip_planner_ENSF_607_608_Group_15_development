from flask import Flask, g
from routes.main_routes import main_routes
from models.db_connection import DatabaseConnection
from models.db_operations import DatabaseOperations
from models.vacation_model import VacationModel
from controllers.vacation_controller import VacationController


def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask app: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "vacationplan"

    # Initialize and store database connection in the app context
    db_connection = DatabaseConnection()
    app.config['DB_ENGINE'] = db_connection.get_engine()

    # Register routes
    app.register_blueprint(main_routes)

    return app


app = create_app()


@app.before_request
def setup_db_connection():
    """
    Set up the database operations and vacation controller before each request.

    This function initializes the DatabaseOperations and VacationController
    objects and stores them in the Flask 'g' object for use during the request.
    """
    if 'db_operations' not in g:
        g.db_operations = DatabaseOperations(app.config['DB_ENGINE'])
    if 'vacation_controller' not in g:
        vacation_model = VacationModel(g.db_operations)
        g.vacation_controller = VacationController(vacation_model)


@app.teardown_appcontext
def close_connection(exception):
    """
    Clean up and dispose of the database engine after the application context ends.

    Args:
        exception (Exception): An exception that occurred during the request, if any.
    """
    db_engine = app.config.get('DB_ENGINE')
    if db_engine:
        db_engine.dispose()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)
