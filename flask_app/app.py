from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['JWT_SECRET_KEY'] = 'vinit'  # Change this to a random secret key
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'db1'

mysql = MySQL(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Initialize JWT extension
jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            return jsonify({"msg": "Username already exists"}), 400

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "User registered successfully"}), 201

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json.get('username')  # Assuming request data is JSON
        password = request.json.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):
            expires = datetime.timedelta(days=1)
            access_token = create_access_token(identity=username, expires_delta=expires)
            return redirect(url_for('upload_file'))  # Redirect to upload page after successful login
        else:
            return jsonify({"msg": "Invalid username or password"}), 401

    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
@jwt_required()
def upload():
    # current_user = get_jwt_identity()

    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"msg": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"msg": "No selected file"}), 400
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({"filename": filename}), 200
        return jsonify({"msg": "File type not allowed"}), 400

    # GET method for retrieving the upload form
    return render_template('upload.html')
@app.route('/')
def display():
    return render_template('display.html')

if __name__ == '__main__':
    app.run(debug=True)
