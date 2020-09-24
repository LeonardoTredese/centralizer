import redexpect
import re
from service import PodmanService, ProcserverService
from threading import Lock

class Remote: 
	def __init__(self, host, user, password):
		self.client = redexpect.RedExpect()
		self.lock = Lock()
		self.client.login(hostname= host, username= user, password= password)
		if user is not 'root':
			self.client.sudo(password)
		self.services = { **self.getpodman(), **self.getprocserver()}
	
	def execute(self, command):
		# prevent race conditions
		self.lock.acquire()
		out = self.client.command(command)
		self.lock.release()
		
		# delete carriage returns
		for i in range(len(command)//60, 0, -1):
			out = out[:i*60] +  out[i*60+1:]
		out = out.replace(command+'\n','').strip()
		return out 

	def __del__(self):
		self.client.exit()

	def getprocserver(self):
		'''This method returns a list with the names of the processes within the procserver manage-procs util'''
		return { name:ProcserverService(name) for name in re.findall('procserv-(.+?).service', self.execute('manage-procs --system list --all'))}
	
	def getpodman(self):
		return {line.split()[-1]:PodmanService(line.split()[-1]) for line in self.execute('podman ps -a').splitlines()[1:]}

	def getallstatuses(self):
		for name, service in self.services.items():
			print(':'.join([name, service.status(self)]));

	def startall(self):
		for service in self.services.values():
			print(service.start(self))

	def stopall(self):
		for service in self.services.values():
			print(service.stop(self))
	
	def start_service(self, name):
		return self.services[name].start(self)
	
	def stop_service(self, name):
		return self.services[name].stop(self)
	
	def status_service(self, name):
		return self.services[name].status(self)
	
	def stats(self):
		out = self.execute('vmstat -S M').splitlines()[-1].split()
		return {'cpu': out[-5], 'freemem': out[3] }

