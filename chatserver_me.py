from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from string import punctuation

class ChatProtocol(LineReceiver):
	def __init__(self,factory):
		self.factory=factory
		self.name = None
		self.state = "REGISTER"

	def connectionMade(self):
		self.sendLine("Give your name to register it")

	def connectionLost(self,reason):
		if self.name in self.factory.users:
			del self.factory.users[self.name]
			self.broadCastMessage("%s has left the chat room" % (self.name,))

	def lineReceived(self,line):
		if self.state == "REGISTER":
			print(line)
			self.handle_REGISTER(line)
		else:
			self.handle_CHAT(line)

	def handle_REGISTER(self,name):
		if name in self.factory.users:
			self.sendLine("Name already used")
			return 
		self.sendLine("Welcome to the chat room!")
		self.sendLine("Type a message to broadcast to the entire room, To talk to a single person, the syntax is '<name>:<message>'")
		self.broadCastMessage("%s	 has just joined!Say hi!" % (name))
		self.name = name
		self.factory.users[self.name] = self
		self.state = "CHAT"

	def parse_message(self,message):
		return message.split(":")


	def handle_CHAT(self,line):
		parsed_message = self.parse_message(line)
		if len(parsed_message) == 2: #send to specific user
			to_send = parsed_message[0]
			if to_send not in self.factory.users:
				self.sendLine("User not registed with us")
				return 
			if to_send == self.name:
				return 
			message = parsed_message[1] 
			message = "<%s> %s" % (self.name,message)
			self.factory.users[to_send].sendLine(message)

		elif len(parsed_message) == 1: #broadcast it to entire chat group
			message = parsed_message[0]
			message = "<%s> %s" % (self.name,message)
			self.broadCastMessage(message)
		else:
			self.sendLine("Illegal message format")
			return 

	def broadCastMessage(self,message):
		for name,conn in self.factory.users.items():
			if conn != self:
				conn.sendLine(message)

class ChatFactory(Factory):
	def __init__(self):
		self.users = {}
		self.server_name = "Org_1"

	def buildProtocol(self,addr):
		return ChatProtocol(self)

	def clientConnectionFailed(self,connector,reason):
		return "Client conn failed: %s",reason.getErrorMessage()

	def clientConnectionLost(self,connector,reason):
		return "Client conn lost: %s",reason.getErrorMessage()

reactor.listenTCP(8000,ChatFactory())
reactor.run()