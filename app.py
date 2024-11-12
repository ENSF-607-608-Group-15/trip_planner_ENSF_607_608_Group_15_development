from flask import Flask
from routes.main_routes import main_routes
from models.db_connection import DatabaseConnection
from models.db_operations import DatabaseOperations
from models.vacation_model import VacationModel
from controllers.vacation_controller import VacationController

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "vacationplan"

    db_connection = DatabaseConnection()
    db_operations = DatabaseOperations(db_connection.get_engine())
    vacation_model = VacationModel(db_operations)
    vacation_controller = VacationController(vacation_model)

    # Register routes
    app.register_blueprint(main_routes)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)
