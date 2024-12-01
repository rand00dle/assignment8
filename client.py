import socket

# user inputs ip address and port number
ip_addr = input("Enter IP address: ")
server_port = int(input("Enter port number: "))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip_addr, server_port))

try:
    while True:
        # user inputs message
        message = input("Enter your message: ")
        
        if message.lower() == "exit":
            break
        
        # sends message to be encoded
        client_socket.send(message.encode('utf-8'))
        response = client_socket.recv(1024) # gets the response from other user
        print("Server replied:", response.decode('utf-8'))  # displays message from the other user
except Exception as e:
    print(f"Error: {e}") # error handling
finally:
    client_socket.close() # terminate connection with server