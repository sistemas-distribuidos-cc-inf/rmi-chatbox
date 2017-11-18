import sys
import Pyro4
from Pyro4 import threadutil

# the daemon is running in its own thread, to be able to deal with server
# callback messages while the main thread is processing user input.

class Chatter(object):
	def __init__(self):
		self.chatbox = Pyro4.core.Proxy('PYRONAME:chatbox')
		self.abort=0

	def message(self, nick, msg):
		if nick != self.nick:
			print('[{0}] {1}'.format(nick, msg))

	def start(self):
		self.nick = input('Choose a nickname: ').strip()
		people = self.chatbox.join(self.nick, self)
		print('Joined chatbox as %s' % self.nick)
		print('People on this chatbox: %s' % (', '.join(people)))
		print('Ready for input! Type /quit to quit')
		try:
			try:
				while not self.abort:
					line = input('> ').strip()
					if line == '/quit':
						break
					if line:
						self.chatbox.publish(self.nick, line)
			except EOFError:
				pass
		finally:
			self.chatbox.leave(self.nick)
			self.abort = 1
			self._pyroDaemon.shutdown()


class DaemonThread(threadutil.Thread):
	def __init__(self, chatter):
		threadutil.Thread.__init__(self)
		self.chatter = chatter
		self.setDaemon(True)

	def run(self):
		with Pyro4.core.Daemon() as daemon:
			daemon.register(self.chatter)
			daemon.requestLoop(lambda: not self.chatter.abort)

chatter = Chatter()
dt = DaemonThread(chatter)
dt.start()
chatter.start()
print('Exit.')