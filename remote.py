import redexpect
import re
from service import PodmanService, ProcserverService

class Remote: 
	def __init__(self, host, user, password):
		self.client = redexpect.RedExpect()
		self.client.login(hostname= host, username= user, password= password)
		if user is not 'root':
			self.client.sudo(password)
		self.services = { **self.getpodman(), **self.getprocserver()}

	def __del__(self):
		self.client.exit()

	def getprocserver(self):
		'''This method returns a list with the names of the processes within the procserver manage-procs util'''
		return { name:ProcserverService(name) for name in re.findall('procserv-(.+?).service', self.client.command('manage-procs --system list --all'))}
	
	def getpodman(self):
		return {line.split()[-1]:PodmanService(line.split()[-1]) for line in self.client.command('podman ps -a').splitlines()[1:]}
		
	def getallstatuses(self):
		for name, service in self.services.items():
			print(':'.join([name, service.status(self.client)]));

	def startall(self):
		for service in self.services.values():
			print(service.start(self.client))

	def stopall(self):
		for service in self.services.values():
			print(service.stop(self.client))
	
	def start_service(self, name):
		return self.services[name].start(self.client)
	
	def stop_service(self, name):
		return self.services[name].stop(self.client)
	
	def status_service(self, name):
		return self.services[name].status(self.client)
