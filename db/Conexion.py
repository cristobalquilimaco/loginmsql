import mysql.connector

conexion = mysql.connector.connect(
    user = "root",
    password = "1234",
    host = "localhost",
    database = "users_db",
    port = "3306"
)

print("Conection is succesfully")

cursor = conexion.cursor(dictionary=True)