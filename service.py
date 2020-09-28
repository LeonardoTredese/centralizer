class Service:
	def __init__(self, name):
		self.name= name
    
	def start(self, remote):
		pass

	def stop(self, remote):
		pass

	def status(self, remote):
		pass

	def out(self, remote):
		pass

class PodmanService(Service):
	def start(self, remote):
		return self.name in remote.execute('podman start ' + self.name)

	def stop(self, remote):
		out = remote.execute('podman stop ' + self.name) 
		try:
			int(out, 16)
		except ValueError:
			return False
		return len(out) is 64

	def status(self, remote):
		return remote.execute('podman ps -a --format "{{.Status}}" --sort names -f name=' + self.name).splitlines()[0]

class ProcserverService(Service):
    def start(self, remote):
        return remote.execute('manage-procs --system start ' + self.name) is ''

    def stop(self, remote):
        return remote.execute('manage-procs --system stop ' + self.name) is ''

    def status(self, remote):
        return remote.execute('manage-procs --system status | grep ' + self.name).split()[1]
 
