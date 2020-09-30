import re
from redexpect            import RedExpect
from redexpect.exceptions import ExpectTimeout 
from service              import PodmanService, ProcserverService
from threading            import Lock

class Remote:
	def __init__(self, hostname, username, password):
		self.client = RedExpect()
		self.lock = Lock()
		self.host = hostname
		self.user = username
		self.passw = password
		self.services = dict()
	
	def __del__(self):
		self.client.exit()
	
	def execute(self, command):
		# prevent race conditions
		self.lock.acquire()
		out = self.client.command(command, timeout=30)
		self.lock.release()
		
		# delete carriage returns
		for i in range(len(command)//60, 0, -1):
			out = out[:i*60] +  out[i*60+1:]
		out = out.replace(command+'\n','').strip()
		return out 

	def getprocserver(self):
		'''This method returns a list with the names of the processes within the procserver manage-procs util'''
		if not self.check_command('manage-procs'):
			return {}
		return { name : ProcserverService(name) for name in re.findall('procserv-(.+?).service', self.execute('manage-procs --system list --all')) }
	
	def getpodman(self):
		if not self.check_command('podman'):
			return {}
		return { line.split()[-1] : PodmanService(line.split()[-1]) for line in self.execute('podman ps -a').splitlines()[1:] }

	def start_service(self, name):
		return self.services[name].start(self)
	
	def stop_service(self, name):
		return self.services[name].stop(self)
	
	def status_service(self, name):
		return self.services[name].status(self)
	
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
		self.lock.release()
