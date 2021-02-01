import utilities.GamesUtilities as GameUtils
import threading
import logging
import socket
import pickle
import select
import queue
import json
from utilities.ClientOperation import ClientOperation
from utilities.loggerHelper import SERVER_LOG_FILE

logging.basicConfig(level = logging.DEBUG,
	format = "[%(asctime)s] -> [%(threadName)s/%(levelname)s] in function %(funcName)s: %(message)s",
	datefmt = "%d/%b/%y | %H:%M:%S",
	handlers = [
		logging.FileHandler(SERVER_LOG_FILE, encoding = "utf-8"),
		logging.StreamHandler()
	]
)

event = threading.Event()
channels = {}

def Main():
	q = queue.Queue() # creating queue for ports
	for i in range(2728, 2770):
		q.put(i)

	logging.info("Starting Handler")
	Handler(q)

def Handler(queue):
	PORT = 2727    # 27
	BUFFER = 4096
	SOCKETS = []

	ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	ssock.bind(('', PORT))
	ssock.listen(5)
	SOCKETS.append(ssock)
	logging.info("Started Server Handler")

	workingHandler = True
	while workingHandler:
		event.wait(0.01)
		rtr, _, _ = select.select(SOCKETS, [], [], 0)
		for client in rtr:
			if client == ssock:
				sfd, address = ssock.accept()
				SOCKETS.append(sfd)
				logging.info(f"New client has arrived to party! {address}")
			else:
				try:
					# message is utils.ServerOperation class (type, **kwargs)
					data = client.recv(BUFFER)
					if data:
						message = pickle.loads(data)
						
						if message.type == "channelCreate":
							if message.channelName in channels:
								client.send(
									pickle.dumps(ClientOperation(
										"channelCreateInfo",
										answer = "Exist"
										)
									))
							else:
								channelPort = queue.get()
								thread = threading.Thread(target = ChannelServer, 
									args = (channelPort, queue, channels, message.channelName), daemon = True) 
								if not queue.empty():
									channels[message.channelName] = {"port": channelPort, "usersAmount": 0}
									thread.start()
									logging.info(
										f"Started {thread} for channel {message.channelName} ({channelPort})"
									)
									client.send(pickle.dumps(
										ClientOperation(
											"channelCreateInfo",
											answer = message.channelName
											)
										))
								else:
									client.send(pickle.dumps(
										ClientOperation(
											"channelCreateInfo",
											answer = "Busy"
											)
										))
						
						elif message.type == "channelJoin":
							try:
								port = channels[message.channelName]["port"]
								client.send(pickle.dumps(ClientOperation("channelJoinInfo", port = str(port),
									channelName = message.channelName)))
							except KeyError:
								client.send(pickle.dumps(ClientOperation("channelJoinInfo", port = "404")))
							except Exception:
								logging.exception("OOPSIE! Some troubles with joining channel:\n")
								client.send(pickle.dumps(ClientOperation("channelJoinInfo", port = "500")))
						
						elif message.type == "channelList":
							client.send(pickle.dumps(
								ClientOperation("channelList", channels = json.dumps(channels))))
						else:
							# client wrote message, probably
							pass
					else:
						logging.info(f"Removing some socket cause it's broken or exited client program.")
						SOCKETS.remove(client)
				except ConnectionResetError:
					logging.warning(f"Some client exited program.")
					SOCKETS.remove(client)
				except Exception:
					logging.exception("uh-oh?\n")
					SOCKETS.remove(client)

def ChannelServer(PORT, portQueue, channels, name):

	BUFFER = 4096
	SOCKETS = []
	USERNAMES = {}

	# --- words game vars ---
	# gameStatus = False
	# usedWords = []
	# solo = False
	# gameQuery = queue.Queue()
	# turn = ""
	# lastWord = ""
	# wordsCounter = 0


	ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	ssock.bind(('', PORT))
	ssock.listen(10)
	SOCKETS.append(ssock)
	logging.info(f"Channel on port {PORT} started.")
	working = True
	while working:
		event.wait(0.01)
		rtr, _, _ = select.select(SOCKETS, [], [], 0)
		channels[name]["usersAmount"] = len(USERNAMES)
		for client in rtr:
			if client == ssock:
				# accepting a new client
				sfd, address = ssock.accept()
				SOCKETS.append(sfd)
				logging.info(f"Client {address} has connected to channel {name}:{PORT}")
				sfd.send(pickle.dumps(ClientOperation("requestUsername")))
			else:
				try:
					data = client.recv(BUFFER)
					if data:
						message = pickle.loads(data)
						clientIP = client.getpeername()[0]

						# if client wrote something, broadcast it to others
						if message.type == "messageSend":
							# client command
							if message.content.startswith("/"):
								continue

							Broadcast(SOCKETS, ssock, client, message.author, message.content)
							
						elif message.type == "usersList":
							client.send(pickle.dumps(ClientOperation("usersList")))

						elif message.type == "usernameGet":
							USERNAMES[str(clientIP)] = str(message.username)

						# if client decided to leave from channel, remove it from clients list 
						elif message.type == "channelLeave":
							logging.info(f"Client ({clientIP}) sended leave request")
							client.send(pickle.dumps(ClientOperation("channelLeave")))
							
							try:
								del USERNAMES[str(clientIP)]
							except KeyError:
								logging.error("clientIP %s is not found in USERNAMES", clientIP)
							finally:
								SOCKETS.remove(client)	
					else:
						logging.info(f"Broken socket on port {PORT}. Removin' it")
						SOCKETS.remove(client)

				except ConnectionResetError:
					logging.warning("Probably broken socket. Removin' it")
					SOCKETS.remove(client)
				except Exception:
					logging.exception("uh-oh?")
					SOCKETS.remove(client)
				finally:
					# closing channel if it's empty
					if len(SOCKETS) <= 1:
						logging.info(f"Channel {name} is empty. Closing it.")
						working = False

	logging.info(f"Quitting thread for port {PORT}.")
	portQueue.put(PORT)
	channels.pop(name, None)
	ssock.close()
	return

def Broadcast(SOCKETS: list, serverSocket, authorSocket, author: str, data: str) -> None:
	"""
		broadcast message to all connected clients in channel
	"""
	for socket in SOCKETS:
		try:
			# checking socket to send data only to peer
			if socket != serverSocket and socket != authorSocket:
				socket.send(pickle.dumps(ClientOperation("messageArrived", 
					messageAuthor = author, messageContent = data))
				)
		except Exception:
			logging.exception("uh-oh?")
			socket.close()
			if socket in SOCKETS:
				SOCKETS.remove(socket)

if __name__ == '__main__':
	Main()
