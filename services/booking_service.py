from json_db import read_json, write_json

def create_booking(data):
    bookings = read_json("bookings.json")

    booking = {
        "id": len(bookings)+1,
        "name": data["name"],
        "phone": data["phone"],
        "people": data["people"],
        "date": data["date"],
        "time": data["time"],
        "status": "pending"
    }

    bookings.append(booking)
    write_json("bookings.json", bookings)

    return booking
