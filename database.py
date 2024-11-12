import os
from dotenv import load_dotenv
import markdown
import sqlalchemy
from sqlalchemy import create_engine, text

load_dotenv()


class database:
    def __init__(self):
        """
        Initialize the database connection using environment variables
        """
        # Read the connection string components from the .env file
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        dbname = os.getenv('DB_NAME')

        # Format the connection string
        connection_string = f'mysql+pymysql://{user}:{
            password}@{host}:{port}/{dbname}?charset=utf8mb4'

        # Create the engine using the connection string
        self.engine = create_engine(connection_string)

    def query(self, query_string):
        """ Execute an SQL query

        Parameters:
        query_string (str): SQL query to execute

        Returns:
        Query result or False if execution fails.
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query_string))
                return result
        except:
            return False

    def callprocedure(self, insert_string):
        """ Execute a stored procedure without parameters

        Parameters:
        insert_string (str): SQL command string
        """
        try:
            with self.engine.connect() as connection:
                with connection.begin() as transaction:
                    connection.execute(text(insert_string))
        except Exception as e:
            print(f"Error: {e}")

    def callprocedure_param(self, insert_string, params):
        """ Execute a stored procedure with parameters

        Parameters:
        insert_string (str): SQL command string
        params (dict): Dictionary of parameters
        """
        try:
            with self.engine.connect() as connection:
                with connection.begin() as transaction:
                    connection.execute(
                        text(insert_string).bindparams(**params))
        except Exception as e:
            print(f"Error: {e}")

    def load_queries_dicts_from_db(self, user_id):
        """ Load the list of queries for a user

        Parameters:
        user_id (int): ID of the user

        Returns:
        list: List of dictionaries for user queries
        """
        result = self.query(
            f"SELECT * FROM queries WHERE userId = {user_id} ORDER BY queryId DESC")
        queries = []
        for row in result:
            query_dic = {'id': row[0],
                         'userId': row[1],
                         'beginDate': row[2],
                         'endDate': row[3],
                         'depatureCity': row[4],
                         'tripTheam': row[5],
                         'location': row[6],
                         'budget': row[7],
                         'noFlying': row[8],
                         'familyFriendly': row[9],
                         'disabilityFriednly': row[10],
                         'groupDiscount': row[11]
                         }
            queries.append(query_dic)
        return queries

    def load_response_dicts_from_db(self, user_id):
        """ Load the list of responses for a user

        Parameters:
        user_id (int): ID of the user

        Returns:
        list: List of dictionaries for LLM responses
        """
        result = self.query(f"SELECT * FROM chatgptresponses WHERE userId = {
                            user_id} ORDER BY chatGPTresponsesId DESC LIMIT 1")
        responses = []
        for row in result:
            response_dic = {'id': row[0],
                            'userId': row[1],
                            'prompt': row[2],
                            'response': markdown.markdown(row[3].replace('<br>', '\n')),
                            }
            responses.append(response_dic)
        return responses
