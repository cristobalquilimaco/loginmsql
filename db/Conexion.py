import mysql.connector
from mysql.connector import Error

def conexion():
    return mysql.connector.connect(
        user = "root",
        password = "1234",
        host = "localhost",
        database = "users_db",
        port = "3306"
)
    
conn = conexion()
cursor = conn.cursor(dictionary=True)