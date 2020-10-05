import re
import time
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
		self.flush()
		try:
			out = self.client.command(command, timeout=5)
		finally:
			self.lock.release()
		# delete carriage returns from command in prompt 
		for i in range(len(command)//60, 0, -1):
			out = out[:i*60] +  out[i*60+1:]
		out = out.replace(command+'\n','').strip()
		return out 

	def shell_read(self, shell_command, stop_command='\x04', encoding='UTF-8', max_chars=1000):
		self.lock.acquire()
		self.client.send(shell_command+'\n')
		previous_encoding, self.client.encoding = self.client.encoding, encoding
		time.sleep(.1)
		out = str()
		for packet in self.client.read():
			out += packet.decode(encoding)
			if len(out) >= max_chars:
				break
		self.client.send(stop_command)
		self.client.expect(re_strings=self.client.prompt_regex)
		self.client.encoding = previous_encoding
		self.lock.release()
		return out.replace(shell_command+'\r\n','')

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
		elif command == 'out':
			return self.services[name].out(self)
		else:
			return False
	
	def stats(self):
		out = self.execute('vmstat -S M').splitlines()[-1].split()
		return {'cpu': out[-5], 'freemem': out[3] }
	
	def flush(self):
		for _ in self.client.read():
			pass
	
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
