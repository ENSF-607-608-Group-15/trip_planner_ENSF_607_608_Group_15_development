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

        
    def load_queries_dicts_from_db(self):
        with self.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM queries"))
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
                            'flying': row[8],
                            'familyFriendly': row[9],
                            'disabilityFriednly': row[10],
                            'pdfOutput': row[11],
                            'groupDiscount': row[12],
                            }
                queries.append(query_dic)
            return queries

#db1 = database()

#queries = db1.load_queries_dicts_from_db()
#print(queries)

