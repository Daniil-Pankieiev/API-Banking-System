from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_swagger_ui import get_swaggerui_blueprint
import bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# Configure rate limiting
limiter = Limiter(
    get_remote_address, app=app, default_limits=["200 per day", "50 per hour"]
)

# Configure logging
logging.basicConfig(filename="transactions.log", level=logging.INFO)

### Swagger specific ###
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Simple Banking System API"}
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### End Swagger specific ###

# In-memory data structure to store account information
accounts = {}
account_id_counter = 1


@app.route("/create_account", methods=["POST"])
@limiter.limit("5 per minute")
def create_account():
    global account_id_counter
    data = request.json
    username = data.get("username")
    password = data.get("password")
    initial_balance = data.get("initial_balance", 0.0)
    currency = data.get("currency", "USD")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    usernames = [account_info["username"] for account_info in accounts.values()]

    if username in usernames:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    account_id = account_id_counter
    account_id_counter += 1
    accounts[account_id] = {
        "password": hashed_password,
        "username": username,
        "balance": initial_balance,
        "currency": currency,
    }

    return (
        jsonify(
            {"account_id": account_id, "balance": initial_balance, "currency": currency}
        ),
        201,
    )


@app.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    for account_id, account_info in accounts.items():
        if account_info["username"] == username:
            if bcrypt.checkpw(password.encode("utf-8"), account_info["password"]):
                access_token = create_access_token(identity=account_id)
                return jsonify(access_token=access_token), 200

    return jsonify({"error": "Bad username or password"}), 401


@app.route("/deposit", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def deposit():
    data = request.json
    amount = data.get("amount")
    account_id = get_jwt_identity()

    if account_id not in accounts:
        return jsonify({"error": "Account not found"}), 404

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    accounts[account_id]["balance"] += amount
    logging.info(f"Deposit: Account {account_id}, Amount {amount}")
    return (
        jsonify({"account_id": account_id, "balance": accounts[account_id]["balance"]}),
        200,
    )


@app.route("/withdraw", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def withdraw():
    data = request.json
    amount = data.get("amount")
    account_id = get_jwt_identity()

    if account_id not in accounts:
        return jsonify({"error": "Account not found"}), 404

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    if accounts[account_id]["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    accounts[account_id]["balance"] -= amount
    logging.info(f"Withdraw: Account {account_id}, Amount {amount}")
    return (
        jsonify({"account_id": account_id, "balance": accounts[account_id]["balance"]}),
        200,
    )


@app.route("/transfer", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def transfer():
    data = request.json
    to_account_id = data.get("to_account_id")
    amount = data.get("amount")
    from_account_id = get_jwt_identity()

    if from_account_id not in accounts or to_account_id not in accounts:
        return jsonify({"error": "Account not found"}), 404

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    if accounts[from_account_id]["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    accounts[from_account_id]["balance"] -= amount
    accounts[to_account_id]["balance"] += amount
    logging.info(
        f"Transfer: From Account {from_account_id}, To Account {to_account_id}, Amount {amount}"
    )
    return (
        jsonify(
            {
                "from_account_id": from_account_id,
                "to_account_id": to_account_id,
                "from_balance": accounts[from_account_id]["balance"],
                "to_balance": accounts[to_account_id]["balance"],
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True)
