from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import datetime
import mysql.connector
from mysql.connector import Error
import jwt
app = Flask(__name__)
cors = CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'bobDylan'


def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="212.227.140.50", 
            port="3306",
            user="oceance",
            password="Four.Dain.80",
            database="iot_sensorPlante"
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
        cursor.execute("INSERT INTO sensorCapteur (soilMoisturePercent, soilMoistureValue, temperature, pressure, humidity, isLight) VALUES (%s, %s, %s, %s, %s, %s)", (soilmoisturepercent, soilmoistureValue, temperature, pressure, humidity, light))
        connection.commit()
        cursor.close()
        connection.close()
        print("Données reçues : ", data)
        return jsonify({"message": "Reception de la data confirmé"}), 200
    else:
        return jsonify({"message": "Erreur de connexion"}), 500

@app.route('/api/v1/user/signup', methods=['POST'])
def signup():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        data_sign = request.get_json()
        lastname = data_sign.get('lastname')
        firstname = data_sign.get('firstname')
        email = data_sign.get('email')
        passwordHash = bcrypt.generate_password_hash(data_sign.get('password')).decode('utf8')
        password = passwordHash
        isHouse = data_sign.get('isHouse')
        isApartment = data_sign.get('isApartment')
        cursor.execute("INSERT INTO userSensor (lastname, firstname, email, password, isHouse, isApartment) VALUES (%s, %s, %s, %s, %s, %s)", (lastname, firstname, email, password, isHouse, isApartment))
        connection.commit()
        cursor.close()
        connection.close()
        token = jwt.encode({
            'user': lastname,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token}), 201
    else:
        return jsonify({"message": "Erreur d'inscription"}), 500

@app.route('/api/v1/user/login', methods=['POST'])
def login():
    data_login = request.get_json()
    email = data_login.get('email')
    password = data_login.get('password')
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT lastname, firstname, email, password FROM userSensor WHERE email=%s", (email,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        if row and bcrypt.check_password_hash(row['password'], password):
            token = jwt.encode({
                'user': row['lastname'] + row['firstname'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }, app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({'token': token}), 202
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
            cursor.execute("SELECT * FROM userSensor WHERE email=%s", (user_email,))
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

@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token manquant!'}), 403

    try:
        # Décoder le token
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return jsonify({'message': f'Bienvenue {data["user"]}!'})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expiré!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token invalide!'}), 401




@app.route('/api/v1/getAllDataSensor', methods=['GET'])
def get_data():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sensorCapteur")
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
                "created_at": datetime.datetime.strftime(row['created_at'], "%d-%m-%Y"),
                "time_at": datetime.datetime.strftime(row['created_at'], "%H h %M")
            })
        return jsonify(data), 200
    else:
        return jsonify({"message": "Erreur de connexion"}), 500

@app.route('/api/v1/getLastDataSensor', methods=['GET'])
def get_last_data():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, soilMoisturePercent, soilMoistureValue, temperature, pressure, humidity, isLight, created_at FROM sensorCapteur ORDER BY id DESC LIMIT 1")
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
                "created_at": datetime.datetime.strftime(last_row['created_at'], "%d-%m-%Y"),
                "time_at": datetime.datetime.strftime(last_row['created_at'], "%H h %M")
            })
            return jsonify(data), 200
        else:
            return jsonify({"message": "Aucune donnée disponible"}), 404
    else:
        return jsonify({"message": "Erreur de connexion"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    ##app.run(debug=True)