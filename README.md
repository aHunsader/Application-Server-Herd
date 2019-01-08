# Application-Server-Herd

server.py
The purpose of this project was to create 5 python servers that would communicate with each other via asynchronous TCP connections. These connections are used to propagate a user's location data from one server to the rest of the servers. This allows locations to be queried from many servers, thus reducing the load on any one server.

One can send an IAMAT message to update a user's location within the servers, or a WHATSAT command to get places closest to the user's location (using Google Places Nearby Search API). AT commands are used for server communication. This is detailed in report.pdf.

test.py
simplistic tests to test the servers propagation.

start.sh
bash script to start all servers and return their processes' corresponding PIDs.

report.pdf
Report detailing the asyncio library of Python and its potential use in application server herds.

