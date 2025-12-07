from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Load reservations from file
try:
    with open("reservations.json", "r") as f:
        reservations = json.load(f)
except FileNotFoundError:
    reservations = []

@app.route("/reservations", methods=["GET"])
def get_reservations():
    return jsonify(reservations)

@app.route("/reserve", methods=["POST"])
def reserve_room():
    data = request.json

    name = data.get("name")
    room = data.get("room")
    date = data.get("date")
    time = data.get("time")

    if not name or not date or not time or not room:
        return jsonify({"error": "Missing required fields"}), 400

    # Combine date + time into one datetime object
    requested_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

    # CHECK LAST RESERVATION BY SAME NAME
    for r in reservations:
        if r["name"] == name:
            last_dt = datetime.strptime(f"{r['date']} {r['time']}", "%Y-%m-%d %H:%M")
            diff_hours = abs((requested_dt - last_dt).total_seconds()) / 3600
            if diff_hours < 5:
                return jsonify({"error": "You can only book again after 5 hours."}), 400

    # CHECK IF ROOM IS ALREADY BOOKED AT THE SAME DATE AND TIME
    for r in reservations:
        if r["room"] == room and r["date"] == date and r["time"] == time:
            return jsonify({"error": "This room is already booked at the selected time."}), 400

    # STORE THE NEW RESERVATION
    new_reservation = {
        "name": name,
        "room": room,
        "date": date,
        "time": time
    }
    reservations.append(new_reservation)

    # Save reservations to file
    with open("reservations.json", "w") as f:
        json.dump(reservations, f)

    return jsonify({
        "message": "Reservation successful!",
        "data": new_reservation
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
