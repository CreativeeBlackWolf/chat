class ServerOperation:
	def __init__(self, type, **kwargs):
		self.type = type
		if self.type == "channelCreate":
			self.channelName = kwargs["channelName"]
			self.channelPassword = kwargs["channelPassword"] or None
		
		elif self.type == "channelJoin":
			# str instance
			self.channelName = kwargs["channelName"]
		
		elif self.type == "channelLeave":
			pass
		
		elif self.type == "channelList":
			pass
		
		elif self.type == "messageSend":
			# both str instances, content and author of the message
			self.content = kwargs["messageContent"]
			self.author = kwargs["messageAuthor"]
		
		elif self.type == "usernameGet":
			# str, user name
			self.username = kwargs["username"]

		elif self.type == "startWordsGame":
			self.soloMode = kwargs["soloMode"]
