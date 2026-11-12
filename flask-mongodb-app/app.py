from datetime import datetime
import os
from urllib.parse import quote_plus
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)


# Connects to MongoDB using environment credentials or default connection URI
def create_mongo_client():
  direct_uri = os.environ.get("MONGODB_URI")
  if direct_uri:
    return MongoClient(direct_uri, serverSelectionTimeoutMS=5000)

  username = os.environ.get("MONGO_USERNAME")
  password = os.environ.get("MONGO_PASSWORD")
  host = os.environ.get("MONGO_HOST", "localhost")
  port = os.environ.get("MONGO_PORT", "27017")
  db_name = os.environ.get("MONGO_DB", "flask_db")
  auth_source = os.environ.get("MONGO_AUTH_SOURCE", "admin")

  if username and password:
    user_esc = quote_plus(username)
    pass_esc = quote_plus(password)
    uri = f"mongodb://{user_esc}:{pass_esc}@{host}:{port}/{db_name}?authSource={auth_source}"
  else:
    uri = f"mongodb://{host}:{port}/{db_name}"

  return MongoClient(uri, serverSelectionTimeoutMS=5000)


client = create_mongo_client()
db_name = os.environ.get("MONGO_DB", "flask_db")
db = client[db_name]
collection = db.data


# Returns a welcome message with the current server timestamp
@app.route("/")
def index():
  return f"Welcome to the Flask app! The current time is: {datetime.now()}"


# Inserts JSON payload into MongoDB on POST and retrieves all documents on GET
@app.route("/data", methods=["GET", "POST"])
def data():
  if request.method == "POST":
    payload = request.get_json()
    if payload is None:
      return (
          jsonify(
              {"error": "Invalid or missing JSON payload in request body"}
          ),
          400,
      )
    collection.insert_one(payload)
    return jsonify({"status": "Data inserted"}), 201

  elif request.method == "GET":
    data_records = list(collection.find({}, {"_id": 0}))
    return jsonify(data_records), 200


# Checks application health and MongoDB connectivity by sending a ping command
@app.route("/health", methods=["GET"])
def health():
  try:
    client.admin.command("ping")
    return (
        jsonify({
            "status": "healthy",
            "database": "connected",
            "time": datetime.now().isoformat(),
        }),
        200,
    )
  except Exception as exc:
    return (
        jsonify({
            "status": "degraded",
            "database": "disconnected",
            "error": str(exc),
        }),
        500,
    )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
