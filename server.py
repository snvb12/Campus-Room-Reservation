from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

class Reservation:
    def __init__(self, name, room, date, time):
        self.__name = name
        self.__room = room
        self.__date = date
        self.__time = time

    def to_dict(self):
        return {
            "name": self.__name,
            "room": self.__room,
            "date": self.__date,
            "time": self.__time
        }

    def get_datetime(self):
        return datetime.strptime(f"{self.__date} {self.__time}", "%Y-%m-%d %H:%M")

    def get_name(self):
        return self.__name

    def get_room(self):
        return self.__room

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time


class VIPReservation(Reservation):
    def __init__(self, name, room, date, time, vip_level):
        super().__init__(name, room, date, time)
        self.vip_level = vip_level

def save_reservation(reservation_obj):
    """Works for both Reservation and VIPReservation objects."""
    return reservation_obj.to_dict()

class ReservationManager:
    def __init__(self):
        try:
            with open("reservations.json", "r") as f:
                self.reservations = json.load(f)
        except FileNotFoundError:
            self.reservations = []

    def save_to_file(self):
        with open("reservations.json", "w") as f:
            json.dump(self.reservations, f)

    def add_reservation(self, reservation_obj):
        self.reservations.append(reservation_obj.to_dict())
        self.save_to_file()

    def is_double_booking(self, room, date, time):
        for r in self.reservations:
            if r["room"] == room and r["date"] == date and r["time"] == time:
                return True
        return False

    def violates_5_hour_rule(self, name, requested_dt):
        for r in self.reservations:
            if r["name"] == name:
                last_dt = datetime.strptime(f"{r['date']} {r['time']}", "%Y-%m-%d %H:%M")
                hours = abs((requested_dt - last_dt).total_seconds()) / 3600
                if hours < 5:
                    return True
        return False

manager = ReservationManager()

@app.route("/reservations", methods=["GET"])
def get_reservations():
    return jsonify(manager.reservations)


@app.route("/reserve", methods=["POST"])
def reserve_room():
    data = request.json

    name = data.get("name")
    room = data.get("room")
    date = data.get("date")
    time = data.get("time")

    if not name or not room or not date or not time:
        return jsonify({"error": "Missing required fields"}), 400

    reservation = Reservation(name, room, date, time)
    requested_dt = reservation.get_datetime()

    if manager.violates_5_hour_rule(name, requested_dt):
        return jsonify({"error": "You can only book again after 5 hours."}), 400

    if manager.is_double_booking(room, date, time):
        return jsonify({"error": "This room is already booked at that time."}), 400

    manager.add_reservation(reservation)

    return jsonify({
        "message": "Reservation successful!",
        "data": save_reservation(reservation)
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5500)
