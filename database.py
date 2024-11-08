import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine, text

load_dotenv()

# Create a connection to the database


class database:
    def __init__(self):
        # Read the connection string components from the .env file
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        dbname = os.getenv('DB_NAME')

        # Format the connection string
        #
        connection_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4'

        # Create the engine using the connection string
        self.engine = create_engine(connection_string)

    def query(self, query_string):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query_string))
                return result
        except:
            return False

    def insert(self, insert_string):
        try:
            with self.engine.connect() as connection:
                connection.execute(text(insert_string))
                connection.commit()
                return True
        except:
            return False

    def delete(self, delete_string):
        try:
            with self.engine.connect() as connection:
                connection.execute(text(delete_string))
                connection.commit()
                return True
        except:
            return False

    def update(self, update_string):
        try:
            with self.engine.connect() as connection:
                connection.execute(text(update_string))
                connection.commit()
                return True
        except:
            return False

    def add_user(self, name, password):
        with self.engine.connect() as connection:
            # Create a text object with the CALL statement
            call_procedure = text("CALL AddUser(:username, :password)")
            input = {"username": name, "password": password}
            # Execute the procedure with parameters
            result = connection.execute(call_procedure, input)

            # If the procedure returns any results, you can fetch them like this:
            # for row in result:
            #     print(row)

            # Commit the transaction
            connection.commit()

    def load_queries_dicts_from_db(self, user_id):
        result = self.query(f"select * from queries where userId = {user_id}")
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
        result = self.query(f"select * from chatgptresponses where userId = {user_id} LIMIT 1")
        responses = []
        for row in result:
            response_dic = {'id': row[0],
                            'userId': row[1],
                            'prompt': row[2],
                            'response': row[3].replace('<br>','\n'),
                            }
            responses.append(response_dic)
        return responses

# db1 = database()

# queries = db1.load_queries_dicts_from_db()
# print(queries)
