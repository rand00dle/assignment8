import socket

# get port number from user
server_port = int(input("Enter port number: "))

# TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket.bind(('', server_port)) # bind the socket to the provided ip adress and port number
    server_socket.listen(5) # listens for incoming connections
    
    print(f"Server is listening on port {server_port}")
    
    while True:
        incoming_socket, incoming_address = server_socket.accept()
        print(f"Connection from {incoming_address}")
        
        try:
            while True:
                message = incoming_socket.recv(1024) # receive the data from the client
        
                if not message:
                    print(f"Client at {incoming_address} has disconnected")
                    break
        
                decoded_message = message.decode('utf-8')
                print(f"Message from client: {decoded_message}")
                response = decoded_message.upper()
                incoming_socket.send(response.encode('utf-8')) # respond to client with data
        except Exception as e:
            print(f"Error during communication with client: {e}")
        finally:
            incoming_socket.close() # closes the connection with the client
except Exception as e:
    print(f"Error: {e}")
finally:
    server_socket.close()
    