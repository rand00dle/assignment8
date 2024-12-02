import socket
from pymongo import MongoClient
from datetime import datetime
import pytz  # For timezone conversions

# Helper Functions
def convert_to_rh(moisture):
    """Convert moisture readings to Relative Humidity (RH%)."""
    return moisture * 0.75  # Replace with your actual conversion formula

def convert_to_imperial(unit, value):
    """Convert metric values to imperial units."""
    conversions = {
        "liters": value * 0.264172,  # Liters to gallons
        "kwh": value * 0.293071,    # kWh to BTU
    }
    return conversions.get(unit.lower(), value)

def get_device_data_and_metadata(device_id, db):
    """Retrieve metadata and IoT data from MongoDB."""
    try:
        # Fetch metadata from Table1_metadata
        metadata = db.Table1_metadata.find_one({"device_id": device_id})
        if not metadata:
            return None, "Device metadata not found."

        # Fetch IoT data from Table1
        data = list(db.Table1.find({"payload.device_id": device_id}))
        if not data:
            return metadata, "No data found for the device."

        return metadata, data
    except Exception as e:
        return None, f"Database error: {e}"

# Server Code
def start_server():
    # Connect to MongoDB
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["test"]  # Use the 'test' database

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = int(input("Enter the port number to bind the server: "))
    try:
        print("Attempting to bind the server...")
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(1)
        print(f"Server is listening on all available IP addresses at port {port}...")
    except Exception as e:
        print(f"Error binding the server: {e}")
        return

    while True:
        try:
            print("Waiting for a client to connect...")
            client_socket, client_address = server_socket.accept()
            print(f"Connected to {client_address}")

            while True:
                message = client_socket.recv(1024)
                if not message:
                    print("Client disconnected.")
                    break

                request = message.decode().strip()
                print(f"Received request: {request}")

                # Retrieve metadata and IoT data
                metadata, result = get_device_data_and_metadata(request, db)
                if not metadata:
                    response = result  # Error message
                else:
                    timezone = pytz.timezone(metadata.get("time_zone", "UTC"))
                    processed_data = []

                    for entry in result:
                        timestamp = entry.get("payload", {}).get("timestamp")
                        value = entry.get("payload", {}).get("value", 0)

                        # Convert timestamp to specified timezone
                        if timestamp:
                            timestamp = datetime.fromisoformat(timestamp).astimezone(timezone)

                        # Perform unit conversion if needed
                        if metadata.get("unit") == "moisture":
                            value = convert_to_rh(value)

                        value = convert_to_imperial(metadata.get("unit", ""), value)
                        processed_data.append(f"{timestamp}: {value} {metadata.get('unit', '')}")

                    response = "\n".join(processed_data)

                client_socket.send(response.encode())

            client_socket.close()
            print("Connection closed with client.")
        except Exception as e:
            print(f"Error handling the client message: {e}")


if __name__ == "__main__":
    start_server()
