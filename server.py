

import aiohttp
import asyncio
import sys
import re
import json
import time

KEY = "your key here"
SERVER = "Goloman"
loop = None
file = None

talks_with = {
	"Goloman": ["Hands", "Holiday", "Wilkes"],
	"Hands": ["Wilkes", "Goloman"],
	"Holiday": ["Welsh", "Wilkes", "Goloman"],
	"Welsh": ["Holiday"],
	"Wilkes": ["Goloman", "Hands", "Holiday"]
}

# on lnxsrv06
ports = {
	"Goloman": 11580,
	"Hands": 11581,
	"Holiday": 11582,
	"Welsh": 11583,
	"Wilkes": 11584
}

# used to store IAMAT information
# form: user_id -> [AT_message, coordinate_string, time_string]
cache = {}

async def fetch(session, url):
	async with session.get(url) as response:
		return await response.json()

async def getPlaces(location, radius, num):
	async with aiohttp.ClientSession() as session:
		m = re.match(r"^([+-]\d+\.\d+)([+-]\d+\.\d+)$", location)
		if m == None:
			return ""
		location = m.group(1) + "," + m.group(2)
		URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=" + KEY
		u = URL + "&location=" + location + "&radius=" + radius
		res = await fetch(session, u)
		# only get number of results requested
		res['results'] = res['results'][:num]
		# google places uses indent of 3
		json_str = json.dumps(res, indent=3)
		# replace newlines with single newline, strip newlines from end
		json_str = re.sub('\n+', '\n', json_str).strip()
		return json_str + "\n\n"

async def client_parse(message, writer, current_time):
	global SERVER
	# compile bc will use a lot
	integer = re.compile(r"^\d+$")
	rtime = re.compile(r"^\d+.\d+$")
	coord = re.compile(r"^([+-]\d+\.\d+)([+-]\d+\.\d+)$")
	timediff = re.compile(r"^[+-]\d+\.\d+")

	write_to_file("INPUT: " + message)
	whitespace = ["\t", "\n", "\r", "\f", "\v"]
	san = message
	for char in whitespace:
		san = san.replace(char, " ")
	san = san.split()
	if len(san) == 0:
		return
	elif san[0] == "WHATSAT":
		if (len(san) != 4) or (integer.match(san[2]) == None) or (integer.match(san[3]) == None):
			await bad_request(message, writer)
		else:
			place = san[1]
			radius = san[2] + "000"
			num = int(san[3])
			if (num < 0) or (num > 20) or (int(san[2]) < 0) or (int(san[2]) > 50):
				await bad_request(message, writer)
			else:
				if (place in cache):
					write_to_file("OUTPUT (to client): %s" % cache[place][0])
					await send_message(cache[place][0], writer)
					location = cache[place][1]
					j = await getPlaces(location, radius, num)
					await send_message(j, writer)
					write_to_file("OUTPUT (to client): %s" % j)

				else:
					await bad_request(message, writer)

	elif san[0] == "AT":
		if (len(san) != 6) or (timediff.match(san[2]) == None) or (coord.match(san[4]) == None) or (rtime.match(san[5]) == None):
			await bad_request(message, writer)
		else:
			place = san[3]
			t = san[5]
			if (place not in cache) or ((cache[place][2] != t) and (float(cache[place][2]) <= float(t))):
				# only send and store if newer than what already has
				location = san[4]
				cache[place] = [message, location, t]
				await propagate(message)

	elif san[0] == "IAMAT":
		if (len(san) != 4) or (coord.match(san[2]) == None) or (rtime.match(san[3]) == None):
			await bad_request(message, writer)
		else:
			t = san[3]
			location = san[2]
			place = san[1]
			at = createAT(SERVER, current_time, t, place, location)
			await send_message(at, writer)
			write_to_file("OUTPUT (to client): %s" % at)
			if (place not in cache) or ((cache[place][2] != t) and (float(cache[place][2]) <= float(t))):
				# only send and store if newer than what already has
				cache[place] = [at, location, t]
				await propagate(at)
	else:
		await bad_request(message, writer)

async def propagate(message):
	global loop
	global SERVER
	for server in talks_with[SERVER]:
		try:
			reader, writer = await asyncio.open_connection('127.0.0.1', port=ports[server], loop=loop)
			write_to_file("Connected to %s\n" % server)
			await send_message(message, writer)
			write_to_file("OUTPUT (to server): %s" % message)
			write_to_file("Disconnected from %s\n" % server)
		except:
			write_to_file("Could not connect to %s\n" % server)

async def send_message(message, writer):
	writer.write(message.encode())
	await writer.drain()


def createAT(server, current_time, new_time, place, location):
	td = current_time - float(new_time)
	plus = "" if td < 0 else "+"
	return "AT %s %s%f %s %s %s\n" % (server, plus, td, place, location, new_time)

async def bad_request(message, writer):
	await send_message("? " + message, writer)
	write_to_file("OUTPUT (to client): ? " + message)


async def connection_handler(reader, writer):
	# get all that you can (Note to self: while true does not work here)
	while not reader.at_eof():
		data = await reader.readline()
		message = data.decode()
		await client_parse(message, writer, time.time())

def write_to_file(message):
	global file
	try:
		file.write(message)
	except:
		print("Error: error writing to file")

def main():
	global SERVER
	global file
	global loop

	if len(sys.argv) != 2:
		sys.exit("usage error: server.py [Goloman|Hands|Holiday|Welsh|Wilkes]")
	if sys.argv[1] not in {"Goloman", "Hands", "Holiday", "Welsh", "Wilkes"}:
		sys.exit("usage error: server.py [Goloman|Hands|Holiday|Welsh|Wilkes]")

	SERVER = sys.argv[1]
	file = open("%s.txt" % SERVER, 'w+')
	# code from TA
	loop = asyncio.get_event_loop()
	server = asyncio.start_server(connection_handler, host='127.0.0.1', port=ports[SERVER], loop=loop)
	server_loop = loop.run_until_complete(server)
	loop.run_forever()
	file.close()

	

if __name__ == "__main__":
	main()