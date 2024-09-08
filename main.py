from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_session import Session
from datetime import datetime
import mysql.connector
from mysql.connector import Error
app = Flask(__name__)
cors = CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'bobDylan'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost", 
            user="root",
            password="Four.Dain.80",
            database="iotCapteurPlante"
        )
        return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

@app.route('/api/v1/create_data', methods=['POST'])
def set_data():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        data = request.get_json()
        soilmoisturepercent = data.get('soilmoisturepercent')
        soilmoistureValue = data.get('soilMoistureValue')
        temperature = data.get('temperature')
        pressure = data.get('pressure')
        humidity = data.get('humidity')
        light = data.get('light')
        cursor.execute("INSERT INTO sensorcapteur (soilMoisturePercent, soilMoistureValue, temperature, pressure, humidity, isLight) VALUES (%s, %s, %s, %s, %s, %s)", (soilmoisturepercent, soilmoistureValue, temperature, pressure, humidity, light))
        connection.commit()
        cursor.close()
        connection.close()
        print("Données reçues : ", data)
        return jsonify({"message": "Reception de la data confirmé"}), 200
    else:
        return jsonify({"message": "Erreur de connexion"}), 500

@app.route('/api/v1/user/signup', methods=['POST'])
def signup():
    data_sign = request.get_json()
    lastname = data_sign.get('lastname')
    firstname = data_sign.get('firstname')
    email = data_sign.get('email')
    passwordHash = bcrypt.generate_password_hash(data_sign.get('password')).decode('utf8')
    password = passwordHash
    isHouse = data_sign.get('isHouse')
    isApartment = data_sign.get('isApartment')
    cursor.execute("INSERT INTO usersensor (lastname, firstname, email, password, isHouse, isApartment) VALUES (%s, %s, %s, %s, %s, %s)", (lastname, firstname, email, password, isHouse, isApartment))
    conn.commit()
    print("Utilisateur créé : ", data_sign) 
    return jsonify({"message": "Inscription réussie"}), 201

@app.route('/api/v1/user/login', methods=['POST'])
def login():
    data_login = request.get_json()
    email = data_login.get('email')
    password = data_login.get('password')
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT lastname, firstname, email, password FROM usersensor WHERE email=%s", (email,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        if row and bcrypt.check_password_hash(row['password'], password):
            session['user'] = row['email']
            return jsonify({"message": "Connexion réussie", 'lastname': row['lastname']}), 202
        else:
            return jsonify({"message": "Erreur de connexion"}), 401
        
       
    else:
        return jsonify({"message": "Erreur de connexion"}), 500
@app.route('/api/v1/user/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/v1/user/info', methods=['GET'])
def userInfo():
    user_email = session.get('user')
    if user_email:
        connection = create_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usersensor WHERE email=%s", (user_email,))
            row = cursor.fetchone()
            cursor.close()
            connection.close()
            if row:
                return jsonify({
                    "id": row['id'],
                    "lastname": row['lastname'],
                    "firstname": row['firstname'],
                    "email": row['email'],
                    "isHouse": row['isHouse'],
                    "isApartment": row['isApartment'],
                    "idSensor": row['idSensor'],
                }), 200
            return jsonify({'message': 'No data'})
        return jsonify({"message": "Erreur de connexion"}), 500
    return jsonify({"message": "Unauthorized"}), 401

@app.route('/api/v1/getAllDataSensor', methods=['GET'])
def get_data():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sensorcapteur")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        data = []
        for row in rows:
            data.append({
                "id": row['id'],
                "soilMoisturePercent": row['soilMoisturePercent'],
                "soilMoistureValue": row['soilMoistureValue'],
                "temperature": row['temperature'],
                "pressure": row['pressure'],
                "humidity": row['humidity'],
                "isLight": row['isLight'],
                "created_at": datetime.strftime(row['created_at'], "%d-%m-%Y")
            })
        return jsonify(data), 200
    else:
        return jsonify({"message": "Erreur de connexion"}), 500

@app.route('/api/v1/getLastDataSensor', methods=['GET'])
def get_last_data():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, soilMoisturePercent, soilMoistureValue, temperature, pressure, humidity, isLight, created_at FROM sensorcapteur ORDER BY id DESC LIMIT 1")
        last_row = cursor.fetchone()
        cursor.close()
        connection.close()
        data = []
        if last_row:
            data.append({
                "id": last_row['id'],
                "soilMoisturePercent": last_row['soilMoisturePercent'],
                "soilMoistureValue": last_row['soilMoistureValue'],
                "temperature": last_row['temperature'],
                "pressure": last_row['pressure'],
                "humidity": last_row['humidity'],
                "isLight": last_row['isLight'],
                "created_at": datetime.strftime(last_row['created_at'], "%d-%m-%Y")
            })
            return jsonify(data), 200
        else:
            return jsonify({"message": "Aucune donnée disponible"}), 404
    else:
        return jsonify({"message": "Erreur de connexion"}), 500

if __name__ == "__main__":
    app.run(host='192.168.1.239', port=5000, debug=True)
    ##app.run(debug=True)