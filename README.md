# Distributed Key-Value Store
## M111 - Big Data
## CS2200006 - Panagiotis Ioannidis
In this programming assignment, we implement a distributed, fault-tolerant key-value store. Our data are stored using only a trie data structure, which we created it from scratch. We implement this project using python 3.8. For the communication between the broker and the servers, we used socket programming.

### Data generation
Before we start our broker-server connection, we have to generate the data that will be used on broker initialization.  
We generate the data running the following command:  

`python3.8 createData.py -k keyFile.txt -n 1000 -d 2 -l 4 -m 5`  

- -k: The file that contains the key-type pairs.
- -n: Indicates the number of the records to be generated (greater than 0).
- -d: The maximum level of nesting (greater equal to 0).
- -m: The maximum number of keys inside each value ( 0 <= m <= 20).
- -l: The maximum length of the string values (greater than 0).

### kvServer
We can start as many servers as we want! To start a server we must execute a command with the following format:  

`python3.8 kvServer.py -a 127.0.0.1 -p 9000`  

- -a: The IP address of the server.
- -p: The port of the server.

### kvBroker
We use the broker to send requests to the servers and print the results that we receive. To start a server we must execute the command with the following format:

`python3.8 kvBroker.py -s serverFile.txt -i dataToIndex.txt -k 2` 

-s: The file which contains the server's IPs and ports.  
-i: The file with the generated data.  
-k: The replication factor. This number must be greater than 0 and lower equal to the number of the available servers.  

## Requests/ Commands
Below we can see some examples that show how to execute the supported commands.
### GET  
`GET person1`  
`GET person15`  

### QUERY
`QUERY person1`  
`QUERY person1.favoriteColor`  
`QUERY person15.iban.country`

### DELETE
`QUERY person2`  
`QUERY person14`

### PUT
`PUT "personA":{"name":"Panos"}`  
`PUT personB:{"car":{"make":"VW"; "model":"Scir"} ; "country":"GR"}`  

### Assumptions
- The generated data are properly formatted and do not contain duplicate high-level keys.
- The keys and values must not contain punctuation or other symbols.
- When a PUT request is issued, the high-level key could be written both with or without double quotes, e.g. `PUT "p1": {"a":"A"}` or `PUT p1:{"a":"A"}`
