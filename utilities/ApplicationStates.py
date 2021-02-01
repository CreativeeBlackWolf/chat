from prompt_toolkit.styles import Style

class ApplicationStates:
	# boolean values
	onlineStatus = False
	debugMode = False
	
	# commands and other dicts
	debugCommands = {
		"log": ["Log commands -> /debug:log <Command>",
			{
				"show": "Show log file -> /debug:log show [Lines]",
				"clear": "Clear log file -> /debug:log clear"
			}
		],
		"statusbar": ["StatusBar commands -> /debug:statusbar <Command>",
			{
				"enable": "Enable status bar -> /debug:statusbar enable",
				"disable": "Disable status bar -> /debug:statusbar disable",
			}
		],
		"reload": "Reload module -> /debug:reload <ModuleName>",
		"list": "Show full debug commands list -> /debug:list"
	}

	commandList = {
		"help": "Show this message -> /help, /h [Command]",
		"create": "Create the channel -> /create, /c (ChannelName)",
		"join": "Join to an existing channel -> /join, /j (ChannelName)",
		"quit": "Quit the channel/program -> /quit, /q [-f, --force]",
		"list": "Show list of all active channels -> /list, /l",
		# "startwordsgame": "Start playing the words game (even w/ yourself!) (W I P, do not try!)-> /startwordsgame | /swg [Solo]"
	}

	applicationStyle = {
		# style for input
		"input_field": "#FF0066",           # text
		"input_field.username": "#FFFF00",
		"input_field.sign": "#0FF531",
		# to-do
		"output_field.username": "bg:#FFFFFF #666666",
		"output_field.message": "#FFFFFF",
		# style for status bar
		"status_bar": "#FFFFFF"
	}


	@staticmethod
	def GetHelp(command = None, debug = False) -> str:
		if not debug:
			if command:
				if command in ApplicationStates.commandList:
					return f"{command}: {ApplicationStates.commandList[command]}"
				return False
			t = "\n"
			for k in ApplicationStates.commandList.keys():
				t += f"|{k}: {ApplicationStates.commandList[k]}\n"
		
		else:
			if command:
				if command in ApplicationStates.debugCommands:
					if type(ApplicationStates.debugCommands[command]) == list:
						com = ApplicationStates.debugCommands[command]
						t = f"|{command}: {com[0]}"
						for i in enumerate(com[1].keys()):
							t += f"{'|->' if i[0] < len(com[1]) - 1 else '`->'} {command}/{i[1]}: {com[1][i[1]]}\n"
						return t
					return f"{command}: {ApplicationStates.debugCommands[command]}"
				return False
			t = "\n"
			for k in ApplicationStates.debugCommands.keys():
				com = k
				desc = ApplicationStates.debugCommands[k]
				if type(desc) == list:
					t += f"|{com}: {desc[0]}\n"
					for xk in enumerate(desc[1].keys()):
						t += f"{'|->' if xk[0] < len(desc[1]) - 1 else '`->'} {com}/{xk[1]}: {desc[1][xk[1]]}\n"
				else:
					t += f"|{com}: {desc}\n"
		return t

	@staticmethod
	def ApplicationStyleAsStyle() -> Style:
		return Style.from_dict(ApplicationStates.applicationStyle)

class StatusBar:
	message = "Hello there!"
	showStatusBar = True

	onlineColor = "bg:#00ff26 #ffffff"  # green color
	offlineColor = "bg:#7700ff #ffffff" # red color 

	@staticmethod
	def SetStatusBarMessage(text) -> None:
		StatusBar.message = text

	@staticmethod
	def GetStatusBarMessage() -> str:
		return StatusBar.message

	@staticmethod
	def ChangeStatusBarState(state = True) -> None:
		StatusBar.showStatusBar = state
		stateString = "enabled." if state else "disabled... uh..."
		StatusBar.SetStatusBarMessage(
			f"[Client]: Status bar {stateString}"
		)
