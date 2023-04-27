# Simple-File-Transfer-Application
README
Name: Eashan Sapre UNI: es4069
This is a network program that allows clients and servers to interact using commands. The program has two modes of operation: server mode and client mode.
Instructions:
Install the requirements using pip install -r requirements.txt
Open terminal or command prompt at the folder in which the FileApp.py file is located. FileApp.py - Main python program file to run as client or server.
Util.py - utility file containing variable names
Run the below commands to start a server or client respectively.
The server and client can be started using the command line arguments "-s" and "-c" respectively.
FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port
Eg. python3 Network.py -c sam 127.0.0.1 4000 2100 3100
Registration
The client can successfully register with an available username using the program. Upon successful registration, the client's local table is initialized. However, if the requested username is already taken by another client, the server rejects the request.
Eg. (base) bravo99@Saps-MacBook-Air client_1 % python3 FileApp.py -c joey 127.0.0.1 4000 5100 4100 >>> Welcome, You are registered.
  python3 FileApp.py -s 4000
 >>>setdir ./
>>>offer pqr.txt abc.txt
 >>> Client Table Updated
Eg. (base) bravo99@Saps-MacBook-Air 4111_file_transfer_socket_programming_project % Running on IP:127.0.0.1
Running on port:4000
File Offering
The "setdir" command works as stated in the specification. The "offer" command will fail with an appropriate error message if no "setdir" command has succeeded.
>>> Successfully set <./> as the directory for searching offered files.
>>>offer abc.txt
File Listing
The program can correctly list file offerings using the table with proper formatting. It will display a proper message when no files are being offered, and the file is updated when the client table is updated.
>>>list
File | Name | IP | Port
(‘abc.txt', 'joey', '127.0.0.1', 4100) ('mcq.txt', 'sam', '127.0.0.1', 3100)
File Transfer

Clients can successfully request and receive a file offered by another client using request command.>>> request filename client_name
>>>request abc.txt joey De-Registration
The "dereg" command de-registers the client without exiting the client program.
