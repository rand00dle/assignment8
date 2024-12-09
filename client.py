import socket

# Define valid queries
valid_queries = {
    "1": "What is the average moisture inside my kitchen fridge in the past three hours?",
    "2": "What is the average water consumption per cycle in my smart dishwasher?",
    "3": "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
}

def display_menu():
    """Display the menu of valid queries."""
    print("\nSelect a query:")
    for i, query in valid_queries.items():
        print(f"{i}. {query}")
    print("4. Exit")

# User inputs IP address and port number
ip_addr = input("Enter IP address: ")
server_port = int(input("Enter port number: "))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip_addr, server_port))

try:
    while True:
        # Display menu to the user
        display_menu()
        choice = input("\nEnter your choice (1-4): ").strip()

        # Handle valid choices
        if choice == "4":  # Exit option
            print("Exiting...")
            client_socket.send(choice.encode('utf-8'))
            break

        # Validate user input
        if choice not in valid_queries:
            print(
                "Sorry, this query cannot be processed. "
                "Please try one of the following:\n" +
                "\n".join(f"{key}. {query}" for key, query in valid_queries.items())
            )
            continue

        # Send the valid query to the server
        client_socket.send(choice.encode('utf-8'))

# Receive and display the server's response
        response = client_socket.recv(1024).decode('utf-8')
        print("\nServer replied:")
        print(response)
        print()  # Add blank line for better readability

except Exception as e:
    print(f"Error: {e}")  # Error handling
finally:
    client_socket.close()  # Terminate connection with server
