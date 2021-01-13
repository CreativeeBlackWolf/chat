import json

class ClientOperation:
	def __init__(self, type, **kwargs):
		self.type = type
		
		if self.type == "messageArrived":
			# both str instances, content and author of the message
			self.content = kwargs["messageContent"]
			self.author = kwargs["messageAuthor"]
		
		elif self.type == "channelLeave":
			pass

		elif self.type == "requireUsername":
			pass

		elif self.type == "channelCreateInfo":
			# str instance, answer of the server (can be anything)
			self.answer = kwargs["answer"]
		
		elif self.type == "channelJoinInfo":
			# str instance, channel port, can be 404 (not found) or 500 (server error)
			self.port = kwargs["port"]
			# str instance, channel name, can be None
			self.channelName = None if self.port in ["404", "500"] else kwargs["channelName"]
		
		elif self.type == "channelInfo":
			# str instance, but can be None
			self.port = kwargs["port"]
		
		elif self.type == "channelList":
			# dict instance (str actually, but dumped from dict)
			# {"channelName": "port"}
			self.channels = json.loads(kwargs["channels"])
