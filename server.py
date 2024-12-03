import socket
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from collections import defaultdict

# Helper Functions
def fetch_data_from_mongo(db, collection_name, query):
    """Generic function to fetch data from MongoDB based on a query."""
    collection = db[collection_name]
    results = list(collection.find(query))
    return results, len(results)  # Return both results and the document count


def calculate_average(values):
    """Calculate the average of a list of values."""
    if not values:
        return None
    return sum(values) / len(values)


def get_moisture_average(db):
    """Calculate the average moisture for the SmartFridge in the last 3 hours using the 'time' field."""
    pst = pytz.timezone('US/Pacific')
    current_time = datetime.now(pst)
    three_hours_ago = current_time - timedelta(hours=3)

    query = {
        "time": {"$gte": three_hours_ago},
        "payload.SmartFridgeMoistureMeter": {"$exists": True}
    }

    results, count = fetch_data_from_mongo(db, "Table1_virtual", query)
    if count == 0:
        return "No moisture data available in the past three hours.", count

    # Extract and process moisture values
    moisture_values = [
        float(record["payload"]["SmartFridgeMoistureMeter"])
        for record in results if "payload" in record and "SmartFridgeMoistureMeter" in record["payload"]
    ]

    avg_moisture = calculate_average(moisture_values)
    if avg_moisture is not None:
        return f"Average moisture in the past 3 hours: {avg_moisture:.2f}% RH", count
    else:
        return "No moisture data available for SmartFridge in the past three hours.", count


def get_dishwasher_water_avg(db):
    """Calculate the average water consumption per cycle for the Dishwasher."""
    query = {"payload.DishwasherMoistureMeter": {"$exists": True}}
    results, count = fetch_data_from_mongo(db, "Table1_virtual", query)

    if count == 0:
        return "No water consumption data available for Dishwasher.", count

    water_values = [
        float(record["payload"]["DishwasherMoistureMeter"])
        for record in results if "payload" in record and "DishwasherMoistureMeter" in record["payload"]
    ]

    avg_water = calculate_average(water_values)
    if avg_water is not None:
        return f"Average water consumption per cycle: {avg_water:.2f} gallons", count
    return "No water consumption data available for Dishwasher.", count


def get_top_electricity_consumer(db):
    """Identify the device with the highest electricity consumption."""
    pst = pytz.timezone('US/Pacific')
    current_time = datetime.now(pst)
    three_hours_ago = current_time - timedelta(hours=3)

    VOLTAGE = 120  # Voltage in volts
    TIME_HOURS = 3  # Time in hours

    query = {
        "time": {"$gte": three_hours_ago},
        "$or": [
            {"payload.SmartFridgeAmmeter": {"$exists": True}},
            {"payload.SmartFridge2Ammeter": {"$exists": True}},
            {"payload.DishwasherAmmeter": {"$exists": True}}
        ]
    }

    def calculate_consumption(ammeter_value):
        return ammeter_value * VOLTAGE * TIME_HOURS / 1000

    results, count = fetch_data_from_mongo(db, "Table1_virtual", query)

    if count == 0:
        return "No electricity consumption data found.", count

    device_consumptions = defaultdict(float)
    for record in results:
        payload = record.get("payload", {})
        for device, field in [
            ("SmartFridge", "SmartFridgeAmmeter"),
            ("SmartFridge2", "SmartFridge2Ammeter"),
            ("Dishwasher", "DishwasherAmmeter")
        ]:
            if field in payload:
                try:
                    device_consumptions[device] += calculate_consumption(float(payload[field]))
                except ValueError:
                    print(f"Invalid value for {field} in record: {record}")

    if device_consumptions:
        highest_device = max(device_consumptions, key=device_consumptions.get)
        highest_value = device_consumptions[highest_device]
        breakdown = "\n".join(f"{device}: {value:.2f} kWh" for device, value in device_consumptions.items())
        return (
            f"Device Breakdown:\n{breakdown}\n\n"
            f"Top Consumer: {highest_device} with {highest_value:.2f} kWh", count
        )
    else:
        return "No electricity consumption data found.", count


# Server Code
def start_server():
    """Start the TCP server and handle client queries."""
    client = MongoClient("mongodb+srv://ramon:assign8@cluster0.2rxmm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["test"]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(input("Enter the port number to bind the server: "))

    try:
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
                # Send menu options to client
                menu = (
                    "\nSelect a query:\n"
                    "1. What is the average moisture inside my kitchen fridge in the past three hours?\n"
                    "2. What is the average water consumption per cycle in my smart dishwasher?\n"
                    "3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?\n"
                    "4. Exit\n"
                    "Enter your choice (1-4): "
                )
                client_socket.send(menu.encode())
                choice = client_socket.recv(1024).decode().strip()

                if choice == "1":
                    result, count = get_moisture_average(db)
                    print(f"Client selected Query 1. Found {count} matching documents.")
                    response = result
                elif choice == "2":
                    result, count = get_dishwasher_water_avg(db)
                    print(f"Client selected Query 2. Found {count} matching documents.")
                    response = result
                elif choice == "3":
                    result, count = get_top_electricity_consumer(db)
                    print(f"Client selected Query 3. Found {count} matching documents.")
                    response = result
                elif choice == "4":
                    print("Client selected Query 4. Disconnecting.")
                    response = "Goodbye!"
                    client_socket.send(response.encode())
                    break
                else:
                    print("Client made an invalid selection.")
                    response = "Invalid choice. Please select a valid option."

                client_socket.send(response.encode())

            client_socket.close()
            print("Connection closed with client.")
        except Exception as e:
            print(f"Error handling the client message: {e}")


if __name__ == "__main__":
    start_server()
