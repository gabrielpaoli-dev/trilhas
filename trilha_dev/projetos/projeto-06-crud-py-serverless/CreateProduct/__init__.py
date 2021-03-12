import logging
import urllib
from sqlalchemy import Float, String, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import azure.functions as func

Model = declarative_base(name='Model')

class Product(Model):
    __tablename__ = "product"

    name = Column(String, primary_key=True)
    description = Column(String, nullable=False, default="No description")
    price = Column(Float(7,2), nullable=False)

    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price
    
    @property
    def serialize(self):
        return {
       	    'name': self.name,
            'description': self.description,
            'price': float(self.price)
        }

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        driver = "{ODBC Driver 17 for SQL Server}"
        server = "kumulus-paoli.database.windows.net"
        database = "test_database"
        user = "login"
        password = "Password123"
        conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
        Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

        params = urllib.parse.quote_plus(conn)
        conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(params)
        engine = create_engine(conn_str, echo=False)
        Model.metadata.create_all(engine)
        session = Session(engine)
    except:
        return func.HttpResponse("Failed to connect")

    name = req.params.get('name')
    name = name.upper()
    description = req.params.get('description')
    price = req.params.get('price')
    try:
        price = float(price)
    except:
        return func.HttpResponse("Wrong price :(")
    if not name or not description or not price:
        return func.HttpResponse("Not enough stuff :(")

    if session.query(Product).filter(Product.name == name).first() is not None:
        return func.HttpResponse("Name already exists :(")
    else:
        try:
            new_product = Product(name = name, description = description, price = price)
            session.add(new_product)
            session.commit()
        except:
            return func.HttpResponse(":(")
            
    return func.HttpResponse("Product created :)")