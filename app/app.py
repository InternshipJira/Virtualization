import os
from flask import Flask, jsonify, request, render_template
from datetime import datetime, timedelta, timezone
from sftp_log_reader import connect_to_mariadb, get_logs_from_db, get_raw_logs_from_db
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/get-logs', methods=['POST'])
def get_logs():
    start_dt = request.form.get('start_datetime')
    end_dt = request.form.get('end_datetime')
    
    try:
        # Convert ONLY here
        start = datetime.fromisoformat(start_dt)
        end = datetime.fromisoformat(end_dt)
    except ValueError:
        return "Invalid datetime format", 400

    db = connect_to_mariadb()
    cursor = db.cursor()

    logs = get_raw_logs_from_db(cursor, os.getenv('TABLE_NAME'), start, end)
    cursor.close()
    db.close()

    return render_template('logs.html', logs=logs)

@app.route('/signal', methods=['POST'])
def receive_signal():

    data = request.get_json()
    if data and data.get('signal'):
        # Process the signal (e.g., log it, trigger an action)
        print("Signal received:", data)
        os.system('python3 log_fetcher.py')
        os.system('python3 raw_log_fetcher.py')
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Invalid signal"}), 400
@app.route("/logs")
def show_logs():
    db = connect_to_mariadb()
    cursor = db.cursor()
    logs = get_logs_from_db(cursor)
    cursor.close()
    db.close()
    for row in logs:
        # Combine date and time into one string for plotting
        row["timestamp"] = f"{row['log_date']} {row['log_time']}"
        row["log_date"] = str(row["log_date"])
        row["log_time"] = str(row["log_time"])
    return jsonify(logs)
@app.route("/raw_logs")
def show_raw_logs():
    db = connect_to_mariadb()
    cursor = db.cursor()
    logs = get_raw_logs_from_db(cursor, os.getenv("TABLE_NAME"))
    cursor.close()
    db.close()
    for row in logs:
        # Combine date and time into one string for plotting
        row["timestamp"] = f"{row['log_date']} {row['log_time']}"
        row["log_date"] = str(row["log_date"])
        row["log_time"] = str(row["log_time"])
    return jsonify(logs)
print("Starting Flask...")
app.run(debug=True, host="0.0.0.0", port=5000)
