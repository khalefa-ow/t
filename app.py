import boto3
import uuid
from flask import Flask, request, jsonify, render_template
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Flask Setup
app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)

# AWS DynamoDB Client
dynamodb = boto3.resource("dynamodb", region_name="your-region")  # Replace with your AWS region
users_table = dynamodb.Table("Users")

# Helper: Check if user exists
def get_user(email):
    response = users_table.get_item(Key={"email": email})
    return response.get("Item")

# Signup Endpoint
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]
    password = data["password"]

    if get_user(email):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    users_table.put_item(Item={"email": email, "password": hashed_password, "user_id": str(uuid.uuid4())})

    return jsonify({"message": "User signed up successfully!"}), 201

# Login Endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    user = get_user(email)
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful!", "user_id": user["user_id"]}), 200

# Serve HTML Form
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
