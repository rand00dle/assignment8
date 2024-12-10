Ramon Quintana, 
Randolf Pangilin Jr,
Group #16
# assignment8

To run the server:
```
python server.py
```
then asks you to enter a port number:
```
ex. Enter the port number to bind the server: 2040
```

To run the client:
```
python client.py
```
then asks you to input an IP address and port number:
```
ex.
Enter IP address: 127.0.0.1 
Enter port number: 2040
```

Once connected, you're able to input one of the three queries or exit with values from (1-4)

The database is connected with our connection string:
```
client = MongoClient("mongodb+srv://ramon:assign8@cluster0.2rxmm.mongodb.net/ retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
```
