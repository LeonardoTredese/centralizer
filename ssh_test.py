import paramiko
import re

class remote:  
    
    def __init__(self, host, user, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname= host, username= user, password= password)
        self.services = self.getpodman()
    
    def __del__(self):
        self.client.close()
    
    def execute(self, command):
        '''This method returns the terminal output of the command as a list of lines'''
        stdin, stdout, stderr = self.client.exec_command(command,timeout=30) 
        print(stderr.read())
        return stdout.read().decode()
    
    def getprocserver(self):
        '''This method returns a list with the names of the processes within the procserver
           manage-procs util'''
        return re.findall('procserv-(.+?).service', self.execute('manage-procs --system list'))

    def getpodman(self):
        return [podmanService(line.split()[-1]) for line in self.execute('podman ps -a').splitlines()[1:]]

    def getallstatuses(self):
        for service in self.services:
            print(':'.join([service.name, self.execute(service.status())]));

    def startall(self):
        for service in self.services:
            self.execute(service.start())

    def stopall(self):
        for service in self.services:
            self.execute(service.stop())

class service:
    def __init__(self, name):
        self.name= name
    
    def start(self):
        pass

    def stop(self):
        pass

    def status(self):
        pass

class podmanService(service):
    def start(self):
        return 'podman start ' + self.name

    def stop(self):
        return 'podman stop ' + self.name

    def status(self):
        return 'podman ps --all --format "{{.Status}}" --filter name=' + self.name 
        
rem1 = remote('10.6.0.41', 'training', 'e3password')
rem2 = remote('10.6.0.75', 'root', 'e3password')
print(rem2.getpodman())
print(rem1.getprocserver())

rem2.getallstatuses()
rem2.startall()
rem2.getallstatuses()
rem2.stopall()
rem2.getallstatuses()
