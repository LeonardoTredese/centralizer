class Service:
    @staticmethod
    def execute(client, command):
        out = client.command(command)
        #delete carriage returns
        for i in range(len(command)//60, 0, -1):
            out = out[:i*60] +  out[i*60+1:]
        out = out.replace(command+'\n','').strip()
        return out 

    def __init__(self, name):
        self.name= name
    
    def start(self, client):
        pass

    def stop(self, client):
         pass

    def status(self, client):
        pass

class PodmanService(Service):
	def start(self, client):
		return self.name in Service.execute(client,'podman start ' + self.name)

	def stop(self, client):
		out = Service.execute(client,'podman stop ' + self.name) 
		try:
			int(out, 16)
		except ValueError:
			return False
		return len(out) is 64

	def status(self, client):
		#if a container name is the prefix of another container name it will return both of them  
		return Service.execute(client,'podman ps -a --format "{{.Status}}" -f name=' + self.name)

class ProcserverService(Service):
    def start(self, client):
        return Service.execute(client,'manage-procs --system start ' + self.name) is ''

    def stop(self, client):
        return Service.execute(client,'manage-procs --system stop ' + self.name) is ''

    def status(self, client):
        return Service.execute(client,'manage-procs --system status | grep ' + self.name)
 
