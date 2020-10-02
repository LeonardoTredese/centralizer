import re
from redexpect            import RedExpect
from redexpect.exceptions import ExpectTimeout 
from service              import PodmanService, ProcserverService
from threading            import Lock

class Remote:
	def __init__(self, hostname, username, password, use_sudo):
		self.client = RedExpect()
		self.lock = Lock()
		self.host = hostname
		self.user = username
		self.passw = password
		self.use_sudo = use_sudo
		self.services = dict()
	
	def __del__(self):
		self.client.exit()
	
	def execute(self, command):
		# prevent race conditions
		self.lock.acquire()
		out = self.client.command(command, timeout=30)
		self.lock.release()
		# delete carriage returns from command in prompt 
		for i in range(len(command)//60, 0, -1):
			out = out[:i*60] +  out[i*60+1:]
		out = out.replace(command+'\n','').strip()
		return out 

	def getprocserver(self):
		'''This method returns a list with the names of the processes within the procserver manage-procs util'''
		if not self.check_command('manage-procs'):
			return {}
		return { line.split()[0] : ProcserverService(line.split()[0]) for line in self.execute('manage-procs status').splitlines() }
	
	def getpodman(self):
		if not self.check_command('podman'):
			return {}
		out = self.execute('podman ps -a')
		if 'Error:' in out:
			print('ERROR IN PODMAN: ', out)
			return {}
		return { line.split()[-1] : PodmanService(line.split()[-1]) for line in out.splitlines()[1:] }

	def interact(self, name, command):
		if   command == 'start':
			return self.services[name].start(self)
		elif command == 'stop':
			return self.services[name].stop(self)
		elif command == 'status':
			return self.services[name].status(self)
		else:
			return False
	
	def stats(self):
		out = self.execute('vmstat -S M').splitlines()[-1].split()
		return {'cpu': out[-5], 'freemem': out[3] }
	
	def connect(self):
		self.login(self.user, self.passw)
		self.services = {**self.getpodman(), **self.getprocserver()}

	def check_command(self, command):
		return self.execute('whereis ' + command) != command + ':'
	
	def login(self, username, password):
		self.lock.acquire()
		self.client.exit()
		self.client = RedExpect()
		self.client.login(hostname= self.host, username= username, password= password)
		if self.use_sudo:
			self.client.sudo(password)
		self.lock.release()
