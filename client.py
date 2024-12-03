import socket

def display_menu():
    print("\nMenu:")
    print("1. What is the average moisture inside my kitchen fridge in the past three hours?")
    print("2. What is the average water consumption per cycle in my smart dishwasher?")
    print("3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?")
    print("4. Exit")

# User inputs IP address and port number
ip_addr = input("Enter IP address: ")
server_port = int(input("Enter port number: "))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip_addr, server_port))

try:
    while True:
        # Receive and display menu options from the server
        menu = client_socket.recv(1024).decode()
        print(menu)

        # Get user choice
        choice = input("Your choice: ").strip()

        if choice == "4":  # Exit option
            client_socket.send(choice.encode('utf-8'))
            print("Exiting...")
            break

        # Send the choice to the server
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
