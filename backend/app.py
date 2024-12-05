from flask import Flask, jsonify
from flask_socketio import SocketIO
import usb.core
import usb.util
import threading
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# Global variable to store connected USB devices
connected_devices = {}


def detect_usb_changes():
    """Background thread to detect USB events."""
    global connected_devices
    while True:
        devices = list(usb.core.find(find_all=True))
        current_device_ids = {dev.idVendor: dev.idProduct for dev in devices}

        # Check for new devices
        for dev in devices:
            dev_info = {
                "idVendor": dev.idVendor,
                "idProduct": dev.idProduct,
                "manufacturer": usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else "Unknown",
                "product": usb.util.get_string(dev, dev.iProduct) if dev.iProduct else "Unknown",
                "serial_number": usb.util.get_string(dev, dev.iSerialNumber) if dev.iSerialNumber else "Unknown",
            }

            if (dev.idVendor, dev.idProduct) not in connected_devices:
                connected_devices[(dev.idVendor, dev.idProduct)] = dev_info
                socketio.emit("usb_event", {"event": "connected", "device": dev_info})

        # Check for removed devices
        removed_devices = [
            key for key in connected_devices.keys()
            if key not in current_device_ids
        ]
        for key in removed_devices:
            removed_device = connected_devices.pop(key)
            socketio.emit("usb_event", {"event": "removed", "device": removed_device})

        time.sleep(1)


@app.route("/api/usb_devices", methods=["GET"])
def get_usb_devices():
    """API to return current USB devices."""
    return jsonify(list(connected_devices.values()))


if __name__ == "__main__":
    # Start USB monitoring in a separate thread
    thread = threading.Thread(target=detect_usb_changes, daemon=True)
    thread.start()

    # Run the Flask app
    socketio.run(app, debug=True)
