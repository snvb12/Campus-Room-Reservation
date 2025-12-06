from flask import Flask, request, jsonify
from flask_cors import CORS

class Reservation:
    def __init__(self, room_number, date, time, reserved_by):
        self.room_number = room_number
        self.date = date
        self.time = time
        self.reserved_by = reserved_by

class Room:
    def __init__(self, room_number):
        self.room_number = room_number
        self.reservations = []

    def add_reservation(self, reservation):
        self.reservations.append(reservation)

class SpecialRoom(Room):
    def __init__(self, room_number, equipment):
        super().__init__(room_number)
        self.equipment = equipment

    def add_reservation(self, reservation):
        print("Special room reservation added!")  
        super().add_reservation(reservation)

class System:
    def __init__(self):
        self.rooms = {
            "Room 101": Room("Room 101"),
            "Room 102": Room("Room 102"),
            "Computer Lab A": SpecialRoom("Computer Lab A", "Computers"),
            "AVR Hall": Room("AVR Hall")
        }

    def make_reservation(self, room_number, date, time, reserved_by):

        if room_number not in self.rooms:
            return False, "Room does not exist."

        room = self.rooms[room_number]
        reservation = Reservation(room_number, date, time, reserved_by)
        room.add_reservation(reservation)
        return True, "Reservation saved!"

app = Flask(__name__)
CORS(app)
system = System()

@app.get("/")
def home():
    return "Reservation backend is running. Use POST /reserve or GET /reservations."

@app.post("/reserve")
def reserve():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid JSON body", "details": str(e)}), 400

    # required fields
    required = ["name", "room", "date", "time"]
    missing = [f for f in required if f not in data or data.get(f) == ""]
    if missing:
        return jsonify({"success": False, "error": "Missing fields", "missing": missing}), 400

    name = data["name"]
    room = data["room"]
    date = data["date"]
    time = data["time"]

    success, message = system.make_reservation(room, date, time, name)
    if not success:
        return jsonify({"success": False, "error": message}), 400

    return jsonify({"success": True, "message": message, "data": {"name": name, "room": room, "date": date, "time": time}}), 201

@app.get("/reservations")
def get_reservations():
    all_res = []
    for room in system.rooms.values():
        for r in room.reservations:
            all_res.append({
                "room": r.room_number,
                "name": r.reserved_by,
                "date": r.date,
                "time": r.time
            })
    return jsonify(all_res)

if __name__ == "__main__":
    print("Starting server on http://127.0.0.1:5000")
    app.run(port=5000)
