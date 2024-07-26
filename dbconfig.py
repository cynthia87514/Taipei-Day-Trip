import mysql.connector
from mysql.connector import pooling
from dotenv import dotenv_values

secrets = dotenv_values(".env")

cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=32,
    pool_reset_session=True,
	host="db",
    user=secrets["MYSQL_USER"],
    password=secrets["MYSQL_PASSWORD"],
    database=secrets["MYSQL_DATABASE"],
)

def get_db_connection():
	con = cnxpool.get_connection()
	if con.is_connected():
		print("Successfully connected to MySQL database.")
		cursor = con.cursor(dictionary = True)
		return con, cursor
	else:
		print("Failed to connect to MySQL database.")