import socket

valid_queries = [
    "What is the average moisture inside my kitchen fridge in the past three hours?",
    "What is the average water consumption per cycle in my smart dishwasher?",
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
]

def display_valid_queries():
    print("Sorry, this query cannot be processed. Please try one of the following:")
    for query in valid_queries:
        print(f" - {query}")

# user inputs ip address and port number
ip_addr = input("Enter IP address: ")
server_port = int(input("Enter port number: "))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip_addr, server_port))

try:
    while True:
        # user inputs message
        message = input("Enter your query: ")
        
        if message.lower() == "exit":
            break
        
        if message in valid_queries:
            # sends query to be encoded
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024) # gets the response from other user
            print("Server replied:", response.decode('utf-8'))  # displays message from the other user
        else:
            # Display error mesage for invalid queries
            display_valid_queries()
            
except Exception as e:
    print(f"Error: {e}") # error handling
finally:
    client_socket.close() # terminate connection with server