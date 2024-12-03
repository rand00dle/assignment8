import socket
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from collections import defaultdict


# Helper Functions
def fetch_data_from_mongo(db, collection_name, query):
    """Generic function to fetch data from MongoDB based on a query."""
    collection = db[collection_name]
    return list(collection.find(query))


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


    print(f"Current time (UTC): {current_time}")
    print(f"Three hours ago (UTC): {three_hours_ago}")

    # Query using the 'time' field
    query = {
        "time": {"$gte": three_hours_ago},
        "payload.SmartFridgeMoistureMeter": {"$exists": True}
     }


    print(f"Executing query: {query}")
    results = list(db["Table1_virtual"].find(query))
    print(f"Matching documents: {len(results)}")
    doc_count = db["Table1_virtual"].count_documents(query)
    if doc_count == 0:
       return "No moisture data available in the past three hours."


    # Extract and process moisture values
    moisture_values = []
    for record in results:
        if "payload" in record:
           if "SmartFridgeMoistureMeter" in record["payload"]:
              moisture_values.append(float(record["payload"]["SmartFridgeMoistureMeter"]))
           if "SmartFridge2MoistureMeter" in record["payload"]:
              moisture_values.append(float(record["payload"]["SmartFridge2MoistureMeter"]))


    if moisture_values:
        avg_moisture = sum(moisture_values) / len(moisture_values)
        return f"Average moisture in the past 3 hours: {avg_moisture:.2f}% RH"
    else:
        return "No moisture data available for SmartFridge in the past 3 hours."


def get_dishwasher_water_avg(db):
    """Calculate the average water consumption per cycle for the Dishwasher."""
    query = {"payload.DishwasherMoistureMeter": {"$exists": True}}
    results = fetch_data_from_mongo(db, "Table1_virtual", query)

    # Print document count for debugging
    print(f"Number of matching documents: {len(results)}")

    water_values = [
        float(record["payload"]["DishwasherMoistureMeter"])
        for record in results
        if "payload" in record and "DishwasherMoistureMeter" in record["payload"]
    ]

    avg_water = calculate_average(water_values)

    if avg_water is not None:
        return f"Average water consumption per cycle: {avg_water:.2f} gallons"
    return "No water consumption data available for Dishwasher."


def get_top_electricity_consumer(db):
    """Identify the device with the highest electricity consumption."""
    pst = pytz.timezone('US/Pacific')
    current_time = datetime.now(pst)
    three_hours_ago = current_time - timedelta(hours=3)

    VOLTAGE = 120  # Voltage in volts
    TIME_HOURS = 3  # Time in hours

    # Query for documents within the past three hours and relevant fields
    query = {
        "time": {"$gte": three_hours_ago},
        "$or": [
            {"payload.SmartFridgeAmmeter": {"$exists": True}},
            {"payload.SmartFridge2Ammeter": {"$exists": True}},
            {"payload.DishwasherAmmeter": {"$exists": True}}
        ]
    }

    # Helper function to calculate electricity consumption
    def calculate_consumption(ammeter_value):
        return ammeter_value * VOLTAGE * TIME_HOURS / 1000

    # Use defaultdict to simplify aggregation
    device_consumptions = defaultdict(float)

    # Fetch matching documents and process them
    results = db["Table1_virtual"].find(query)
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

    # Determine the device with the highest consumption
    if device_consumptions:
        highest_device = max(device_consumptions, key=device_consumptions.get)
        highest_value = device_consumptions[highest_device]
        breakdown = "\n".join(f"{device}: {value:.2f} kWh" for device, value in device_consumptions.items())
        return (
            f"Device Breakdown:\n{breakdown}\n\n"
            f"Top Consumer: {highest_device} with {highest_value:.2f} kWh"
        )
    else:
        return "No electricity consumption data found."




# Server Code
def start_server():
    """Start the TCP server and handle client queries."""
    client = MongoClient("mongodb+srv://ramon:assign8@cluster0.2rxmm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["test"]
    devices_collection = db["Table1_metadata"] # Collection for metadata
    data_collection = db["Table1_virtual"] #Collection for IoT Data


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
                message = client_socket.recv(1024)
                if not message:
                    print("Client disconnected.")
                    break

                query = message.decode().strip()
                print(f"Received query: {query}")

                # Handle specific queries
                if query == "What is the average moisture inside my kitchen fridge in the past three hours?":
                    response = get_moisture_average(db)
                elif query == "What is the average water consumption per cycle in my smart dishwasher?":
                    response = get_dishwasher_water_avg(db)
                elif query == "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?":
                    response = get_top_electricity_consumer(db)
                else:
                    response = "Invalid query. Please try a valid query."

                client_socket.send(response.encode())

            client_socket.close()
            print("Connection closed with client.")
        except Exception as e:
            print(f"Error handling the client message: {e}")


if __name__ == "__main__":
    start_server()
