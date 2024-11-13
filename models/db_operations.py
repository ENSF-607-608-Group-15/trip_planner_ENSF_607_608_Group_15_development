from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import markdown

class DatabaseOperations:
    """
    Represents the operations that can be performed on the database
    """
    def __init__(self, engine):
        """
        Initialize the database operations using the engine
        """
        self.engine = engine

    def execute_query(self, query_string):
        """ Execute a SQL query

        Parameters:
        query_string (str): SQL query to execute

        Returns:
        Query result or None if execution fails.
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query_string))
                return result
        except SQLAlchemyError as e:
            print(f"Query execution error: {e}")
            return None

    def call_procedure(self, procedure_string, params=None):
        """ Execute a stored procedure with or without parameters

        Parameters:
        insert_string (str): SQL command string
        params (dict): Dictionary of parameters
        """
        try:
            with self.engine.connect() as connection:
                with connection.begin() as transaction:
                    if params is None:
                        result = connection.execute(text(procedure_string))
                    else:
                        result = connection.execute(text(procedure_string).bindparams(**params))
                if result.returns_rows:
                    return [dict(row) for row in result]
                else:
                    return {"status": "Procedure executed successfully"}
        except SQLAlchemyError as e:
            print(f"Procedure execution error: {e}")
            return None
        
    def load_queries_dicts_from_db(self, user_id):
        """ Load the list of queries for a user

        Parameters:
        user_id (int): ID of the user

        Returns:
        list: List of dictionaries for user queries
        """
        result = self.execute_query(f"SELECT * FROM queries WHERE userId = {user_id} ORDER BY queryId DESC")
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
        result = self.execute_query(f"SELECT * FROM chatgptresponses WHERE userId = {user_id} ORDER BY chatGPTresponsesId DESC LIMIT 1")
        responses = []
        for row in result:
            response_dic = {'id': row[0],
                            'userId': row[1],
                            'prompt': row[2],
                            'response': markdown.markdown(row[3]),
                            }
            responses.append(response_dic)
        return responses
