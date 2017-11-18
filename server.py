import Pyro4

class ChatBox(object):
	def __init__(self):
		self.users = []	# registered users [user --> (nick, client callback)]
		self.nicks = []	# all registered nicks on this server

	def getNicks(self):
		return self.nicks

	def join(self, nick, callback):
		if not nick:
			raise ValueError('Invalid nickname')
		if nick in self.nicks:
			raise ValueError('This nickname is already in use')
		self.users.append((nick, callback))
		self.nicks.append(nick)
		callback._pyroOneway.add('jobdone')	# make sure clients transfer control back to the server, non blocking call
		print("%s JOINED" % nick)
		self.publish('SERVER', '** '+nick+' joined **')
		return [n for (n, c) in self.users]	# return all nicks in this server

	def leave(self, nick):
		for(n, c) in self.users:
			if n == nick:
				self.users.remove((n, c))
				break
		self.publish('SERVER', '** '+nick+' left **')
		self.nicks.remove(nick)
		print("%s LEFT" % nick)

	def publish(self, nick, msg):
		for(n, c) in self.users[:]:	# use a copy of the list --> [:]
			try:
				c.message(nick, msg)
			except Pyro4.errors.ConnectionClosedError:
				# connection dropped, remove the listener if it's still there
				# check for existance because other thread may have killed it already
				if(n, c) in self.users:
					self.users.remove((n, c))
					print('Remove dead listener %s %s' % (n, c))

with Pyro4.core.Daemon() as daemon:
	with Pyro4.naming.locateNS() as ns:
		uri = daemon.register(ChatBox())
		ns.register("chatbox", uri)
		# enter the service loop
		print('Chatbox open.')
		daemon.requestLoop()