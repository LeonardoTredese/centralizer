class Service:
    ''' A class that symbolically rapresents a generic kind of service

        Attributes:
            nams: the name associated to the service
    '''
    def __init__(self, name):
        '''Basic initializer with the services name'''
	self.name= name

    def start(self, remote):
        '''Starts the service
            
            Args:
                remote: the remote host where this service is present. Remote

            Returns:
                the outcome of the operation as a boolean
        '''
	pass

    def stop(self, remote):
        '''Stops the service
            
            Args:
                remote: the remote host where this service is present. Remote

            Returns:
                the outcome of the operation as a boolean
	'''
        pass

    def status(self, remote):
        '''Gets the status of the service 
            
            Args:
                remote: the remote host where this service is present. Remote

            Returns:
                the status of the operation in form of a string
	'''
	pass

    def out(self, remote):
        '''Gets some lines of the output of the Service 

            Args:
                remote: the remote host where this service is present. Remote

            Returns:
                a string rapresenting some line of the service output
        '''
	pass

class PodmanService(Service):
    '''An implementation of Service class specific to control podman containers
    '''
    def start(self, remote):
        '''See Service'''
	return self.name in remote.execute('podman start ' + self.name)

    def stop(self, remote):
        '''See Service'''
	out = remote.execute('podman stop ' + self.name) 
	try:
	    int(out, 16)
	except ValueError:
	    return False
	return len(out) == 64

    def status(self, remote):
        '''See Service'''
	return remote.execute('podman ps -a --format "{{.Status}}" --sort names -f name=' + self.name).splitlines()[0]
	
    def out(self, remote):
        '''See Service

            The output comes from the logs which are persistent
        '''
        return remote.execute('podman logs --tail=20 ' + self.name)

class ProcserverService(Service):
    '''An implementation of Service class specific to control procserver instances
    '''
    def start(self, remote):
        '''See Service'''
	return remote.execute('manage-procs start ' + self.name) == ''
    
    def stop(self, remote):
        '''See Service'''
	return remote.execute('manage-procs stop ' + self.name) == ''

    def status(self, remote):
        '''See Service'''
	return remote.execute('manage-procs status | grep ' + self.name).split()[1]

    def out(self, remote):
        '''See Service

            The output comes directly from the shell, so if the shell does not output anything 
            it will be empty
        '''
	return remote.shell_read('manage-procs attach ' + self.name, encoding='latin1') 
