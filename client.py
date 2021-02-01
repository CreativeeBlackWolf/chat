# -*- coding: utf-8 -*-
import configparser
import threading
import argparse
import socket
import pickle
import sys
import os
import utilities.loggerHelper as loggerHelper
import utilities.utils as utils
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, ConditionalContainer
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import Layout, FormattedTextControl
from prompt_toolkit.application import Application, get_app
from prompt_toolkit.widgets import SearchToolbar, TextArea
from utilities.ServerOperation import ServerOperation
from prompt_toolkit.key_binding import KeyBindings
from concurrent.futures import ThreadPoolExecutor
from prompt_toolkit.history import FileHistory
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from utilities.ApplicationStates import *
from prompt_toolkit.styles import Style
from importlib import reload
from distutils import util
from time import sleep

def Main():
	app = Application(
		layout = Layout(root, focused_element = inputField),
		key_bindings = binds,
		full_screen = True,
		mouse_support = True,
		style = ApplicationStates.ApplicationStyleAsStyle()
	)
	if ApplicationStates.debugMode:
		StatusBar.SetStatusBarMessage(
			"[DEBUG]: heya there! debug mode enabled. use `/debug:list` to see commands."
		)
	ServerHandlerThread = threading.Thread(target = ServerHandler, args = [s,], daemon = True)
	ServerHandlerThread.start()
	app.run()

binds = KeyBindings()

@binds.add("c-q")
def _(event):
	inputField.buffer.document = Document(
		text = "/quit",
		cursor_position = 5
	)

@binds.add("c-l")
def _(event):
	inputField.buffer.document = Document(
		text = "/list",
		cursor_position = 5
	)

def InputHandler(buff):
	line = inputField.text
	ThreadPoolExecutor().submit(PrintToChatWindow(inputField.text))
	if line:
		if line.startswith("/"):
			c = line.split()
			command = c[0]

			if command in ["/quit", "/q"]:
				if len(c) == 2:
					if c[1] in ["-f", "--force"]:
						raise SystemExit
				if ApplicationStates.onlineStatus is False:
					raise SystemExit
				else:
					# sending leave request to channel server
					cs.send(pickle.dumps(ServerOperation("channelLeave")))

			elif command in ["/list", "/l"]:
				s.send(pickle.dumps(ServerOperation("channelList")))

			elif command in ["/join", "/j"]:
				if ApplicationStates.onlineStatus is False:
					if len(c) >= 2:
						s.send(pickle.dumps(ServerOperation("channelJoin", channelName = " ".join(c[1::]))))
					else:
						StatusBar.SetStatusBarMessage(
							"[Client]: Command wrote wrong: /join (ChannelName)"
						)
				else:
					StatusBar.SetStatusBarMessage(
						"[Client]: You can't join another channel."
					)

			elif command in ["/create", "/c"]:
				if ApplicationStates.onlineStatus is False:
					if len(c) >= 2:
						s.send(pickle.dumps(ServerOperation("channelCreate", 
							channelPassword = None, channelName = " ".join(c[1::])))
						)
					else:
						StatusBar.SetStatusBarMessage(
							"[Client]: Command wrote wrong: /create (ChannelName)"
						)
				else:
					StatusBar.SetStatusBarMessage(
						"[Client]: Can't create channel while being online (in channel)."
					)

			elif command in ["/help", "/h"]:
				if len(c) == 1:
					ThreadPoolExecutor().submit(PrintToChatWindow(ApplicationStates.GetHelp(), "Client"))
				elif len(c) == 2:
					ans = ApplicationStates.GetHelp(command = c[1])
					if not ans:
						StatusBar.SetStatusBarMessage(
							f"[Client]: help: Command '{c[1]}' is not found. Try /help"
						)
					else:
						ThreadPoolExecutor().submit(PrintToChatWindow(ans, "Client"))

			elif command in ["/users", "/u"]:
				if not ApplicationStates.onlineStatus:
					StatusBar.SetStatusBarMessage("[Client]: You're offline")
				else:
					s.send(pickle.dumps(ServerOperation("usersList")))

			# elif command.lower() in ["/startwordsgame", "/swg"]:
			# 	if not ApplicationStates.onlineStatus:
			# 		StatusBar.SetStatusBarMessage("[Client]: You're offline.")
			# 		return
			# 	soloMode = False
			# 	if len(c) == 2:
			# 		soloMode = c[1] in ["solo", "one"]
			# 	cs.send(pickle.dumps(ServerOperation("startWordsGame", soloMode = soloMode)))

			elif command.startswith(("/debug", "/d")):
				if ApplicationStates.debugMode is True:
					try:
						debug = command.split(":")[1].lower()
						if debug == "statusbar":
							if len(c) == 2:
								if c[1] == "enable":
									StatusBar.ChangeStatusBarState(True)
								elif c[1] == "disable":
									StatusBar.ChangeStatusBarState(False)
							else:
								StatusBar.SetStatusBarMessage(
									"[DEBUG]: StatusBar and what?"
								)
						elif debug == "log":
							if len(c) >= 2:
								if c[1] == "show":
									# getting latest lines from log file.
									# until scroll is not done,
									# we'll get only latest X - 3 lines of log
									# 3 (separator, input field and statusbar)
									lines, _ = utils.GetTerminalSize()
									if len(c) == 3:
										try:
											lines = int(c[2])
										except ValueError:
											StatusBar.SetStatusBarMessage(
												f"[DEBUG]: Lines argument is not an integer. Showing latest {lines - 3} lines."
											)
									t = "\n" + loggerHelper.GetLogAsString(lines)
									ThreadPoolExecutor().submit(PrintToChatWindow(t, "Client"))
								elif c[1] == "clear":
									loggerHelper.ClearLogFile()
									StatusBar.SetStatusBarMessage(
										f"[DEBUG]: Log file cleared."
									)
							else:
								StatusBar.SetStatusBarMessage(
									f"[DEBUG]: Log and what?"
								)
						elif debug == "reload":
							if c[1] in sys.modules:
								reload(sys.modules[c[1]])
								StatusBar.SetStatusBarMessage(
									f"[DEBUG]: Module {c[1]} reloaded."
								)
							else:
								StatusBar.SetStatusBarMessage(
									f"[DEBUG]: Module {c[1]} is not found or loaded."
								)
						elif debug == "list":
							if len(c) == 1:
								ThreadPoolExecutor().submit(PrintToChatWindow(
									ApplicationStates.GetHelp(debug = True), "Client")
								)
							elif len(c) == 2:
								ans = ApplicationStates.GetHelp(debug = True, command = c[1])
								if ans:
									ThreadPoolExecutor().submit(PrintToChatWindow(ans, "Client"))
								else:
									StatusBar.SetStatusBarMessage(
										f"[DEBUG]: Command {c[1]} is not found."
									)
						else:
							StatusBar.SetStatusBarMessage(
								f"[DEBUG]: Command not found: {debug}"
							)
					except IndexError:
						StatusBar.SetStatusBarMessage(
							"[DEBUG]: You haven't wrote the debug command."
						)
				else:
					StatusBar.SetStatusBarMessage(
						"[Client]: Turn on debug mode to use debug commands."
					)
		if ApplicationStates.onlineStatus is True:
			cs.send(pickle.dumps(ServerOperation("messageSend", 
				messageContent = inputField.text,
				messageAuthor = username
			)))
			chatLog.append(f"({utils.GetTime()}) [{username}] -> {inputField.text.encode('utf-8').decode('utf-8')}")
	return

def ChannelHandler(channelSocket, channelName, port):
	logger.info("Started channel handler.")
	global chatLog
	chatLog = []
	while True:
		rawChannel = channelSocket.recv(4096)
		if rawChannel:
			message = pickle.loads(rawChannel)
			with ThreadPoolExecutor() as cex:
				
				if message.type == "requestUsername":
					channelSocket.send(pickle.dumps(ServerOperation("usernameGet", username = username)))
				
				elif message.type == "usersList":
					cex.submit(PrintToChatWindow(message.users))

				elif message.type == "messageArrived":
					cex.submit(PrintToChatWindow(message.content, message.author))
					chatLog.append(f"({utils.GetTime()}) [{message.author}] -> {message.content}")
				
				elif message.type == "channelLeave":
					channelSocket.close()
					ApplicationStates.onlineStatus = False
					path = utils.WriteChatLogFile(CHATLOG_PATH, channelName, port, chatLog)
					logger.info(f"Log file writed to {path}")
					logger.info("Leaving channel thread.")
					StatusBar.SetStatusBarMessage(
						"[Client]: Left from the channel."
					)
					return
				
				else:
					logger.warning(f"Got unexpected message type: {message.type}")
		else:
			logger.warning("Channel connection lost.")
			ApplicationStates.onlineStatus = False
			return

def ServerHandler(serverSocket):
	while True:
		rawServer = serverSocket.recv(4096) # receiving raw server message
		# check if server is good
		if rawServer:
			message = pickle.loads(rawServer) # convert message into utils.ClientOperation class
			with ThreadPoolExecutor() as ex:
				if message.type == "channelList":
					channelsList = message.channels
					if channelsList:
						t = "\n"
						for k in channelsList.keys():
							t += f"|{k} -- Port: {channelsList[k]['port']} -- Users in room: {channelsList[k]['usersAmount']}\n"
						ex.submit(PrintToChatWindow(t, "Server"))
					else:
						ex.submit(PrintToChatWindow("There are no channels avavible.", "Server"))
				elif message.type == "channelJoinInfo":
					if message.port == "404":
						StatusBar.SetStatusBarMessage(
							"[Server]: Channel is not found."
						)
						continue
					if message.port == "500":
						StatusBar.SetStatusBarMessage(
							"[Server]: i'm fucked up. Sorry."
						)
						continue
					try:
						logger.info(f"Connecting to channel with port {message.port}...")
						global cs
						cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						cs.connect((address, int(message.port)))
						logger.info("Connected. Starting ChannelHandler thread.")
						ChannelHandlerThread = threading.Thread(target = ChannelHandler, 
							args = [cs, message.channelName, message.port,], daemon = True)
						ChannelHandlerThread.start()
						ApplicationStates.onlineStatus = True
						logger.info("Switched online status to True")
						StatusBar.SetStatusBarMessage(
							"[Server]: Successfully joined channel. Happy chatting!"
						)
					except Exception:
						StatusBar.SetStatusBarMessage(
							"[Client]: An error has occured while trying to connect to channel. It's logged, if what."
						)
						logger.exception("An error has occured while trying to connect to channel.")
				elif message.type == "channelCreateInfo":
					if message.answer == "Exist":
						StatusBar.SetStatusBarMessage(
							"[Server]: Channel with this name already exist. Try another or check channel list."
						)
					elif message.answer == "Busy":
						StatusBar.SetStatusBarMessage(
							"[Server]: All ports are busy"
						)
					else:
						StatusBar.SetStatusBarMessage(
							f"[Server]: Channel [{message.answer}] opened!"
						)
						serverSocket.send(pickle.dumps(ServerOperation("channelJoin", channelName = message.answer)))				
				else:
					logger.warning(f"Got unexpected message type: {message.type}")
		else:
			StatusBar.SetStatusBarMessage(
				"[Client]: Server is not avavible. Exiting chat program."
			)
			sleep(2)
			logger.error("Server is not avavible. Exiting chat program... cya~")
			get_app().exit()

def PrintToChatWindow(content, author = "You") -> bool:
	with threading.Lock():
		text = f"[{author}]: {content}\n"
		toPrint = outputField.text + text
		outputField.buffer.document = Document(
			text = toPrint,
			cursor_position = len(toPrint)
		)
		return True

def UpdateOnlineStatus():
	# green color of onlineStatusBar if online, else purple
	onlineStatusBar.style = StatusBar.onlineColor if ApplicationStates.onlineStatus else StatusBar.offlineColor
	return " <Online> " if ApplicationStates.onlineStatus is True else " <Offline> "

# reading client.cfg file
cfg = configparser.ConfigParser()
cfg.read("client.cfg")

CHATLOG_PATH = cfg.get("Paths", "chatlog_path", fallback = "./logs/chat")

#creating logger via loggerHelper.py
logger = loggerHelper.GetLogger("Client")

username = cfg.get("Client", "username", fallback = None)
if not username:
	username = input("Before we start, enter your username > ")
	cfg.set("Client", "username", username)
	logger.info(f"Writed username ({username}) to config file.")
	with open("client.cfg", "w") as f:
		cfg.write(f)

# reading connection info
address = cfg.get("Client", "address", fallback = "localhost")
serverPort = cfg.getint("Client", "port", fallback = 2727)

# connecting to server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((address, serverPort))

# --------- fRoNt EnD ---------
outputField = TextArea(
	style = "class:output_field",
	scrollbar = True,
	focusable = False
)

inputPrompt = [
	("class:input_field.username", f"[{username}]"),
	("class:input_field.sign", ":>"),
]

inputFieldPrompt = FormattedTextControl(
	text = inputPrompt,
	style = "class:input_field",
	focusable = False,
)

inputField = TextArea(
	height = 1,
	multiline = False,
	wrap_lines = False,
	accept_handler = InputHandler
)

onlineStatusBar = FormattedTextControl(UpdateOnlineStatus,
	style = "bg:#7700ff #ffffff",
	focusable = False
)

root = HSplit([
	outputField,                                       # text area for messages
	Window(height = 1, char = "─", style = "#37fc00"), # separator
	VSplit([                                           # input field
		Window(inputFieldPrompt, width = len(inputPrompt[0][1]) + len(inputPrompt[1][1]) + 1),
		inputField
	]),
	ConditionalContainer(                              # status bar
		content = VSplit(
			[
				Window(FormattedTextControl(StatusBar.GetStatusBarMessage, 
					style = "class:status_bar")),
				Window(onlineStatusBar, width = 12)
			],
			height = 1
		),
		filter = Condition(lambda: StatusBar.showStatusBar)
	)
])
# --------- fRoNt EnD ---------

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "bAsiC chat client on python.")
	parser.add_argument("--debug", nargs = "?", const = True, default = False, 
		help = "Activate debug mode.", 
		type = lambda x: bool(util.strtobool(x)))
	args = parser.parse_args()
	ApplicationStates.debugMode = args.debug

	Main()
