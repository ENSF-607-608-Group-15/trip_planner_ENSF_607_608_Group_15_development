import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

class DatabaseConnection:
    """
    Represents a connection to the database
    """
    def __init__(self):
        """
        Initialize the database connection using environment variables
        """
        try:
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT')
            db_name = os.getenv("DB_NAME")

            # Ensure all required environment variables are set
            if not all([db_user, db_password, db_host, db_name]):
                raise ValueError("Database connection details are incomplete. Check environment variables.")

            # Format the connection string and create the engine
            connection_string = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
            self.engine = create_engine(connection_string)
            print("Database connection established successfully.")

        except SQLAlchemyError as e:
            print(f"Error creating database engine: {e}")
            self.engine = None
        except ValueError as e:
            print(f"Environment configuration error: {e}")
            self.engine = None

    def get_engine(self):
        """
        Retrieve the database engine.

        Returns:
            Engine: The SQLAlchemy engine instance if available; otherwise, None.
        """
        if self.engine is None:
            print("Engine not available. Check database connection.")
        return self.engine
    