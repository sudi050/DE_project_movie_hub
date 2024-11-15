# config_db_admin.py
import os
import psycopg2
from flask import Flask, g

# PostgreSQL connection details
db_name = "movies_de_database"
db_user = "postgres"
db_password = "qwertyuiop"
db_host = "localhost"
db_port = "5432"

# Flask app setup
server = Flask(__name__)
server.secret_key = os.urandom(24)


# Database connection setup
def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
    return g.db


@server.teardown_appcontext
def close_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()
