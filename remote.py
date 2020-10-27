import re
import time
from redexpect            import RedExpect
from redexpect.exceptions import ExpectTimeout 
from service  import PodmanService, ProcserverService
from threading            import Lock

class Remote:
    ''' This class represents a remote hosts and keeps an ssh connection to it

        Attributes:                 
            client: Red Expect's ssh client. redexpect.RedExpect 
            lock: mutex for operations on self.client's when running on a multi threaded server. threading.Lock 
            host: ip address or hostname of the remote host. str or unicode
            user: username of the user on the remote host. str or unicode
            passw: password of the user on the remote host. str or unicode
            use_sudo: boolean indicating if you should use sudo with self.client.
            services: the dictornary that keeps track of the services available on the remote host.
    '''
    def __init__(self, hostname, username, password, use_sudo):
        ''' Inits the class fields '''
        self.client = RedExpect()
        self.lock = Lock()
        self.host = hostname
        self.user = username
        self.passw = password
        self.use_sudo = use_sudo
        self.services = dict()
    
    def __del__(self):
        ''' Exits the ssh connection on object delition ''' 
        self.client.exit()
    
    def execute(self, command):
        ''' Runs a command on the remote host
            
            Args:
                command: the command to be executed. str or unicode

            Returns:
                the output of the command as a string
        '''
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
        return out.replace(command+'\n','').strip()

    def shell_read(self, shell_command, stop_command='\x04', encoding='UTF-8', max_chars=1000):
        '''Interacts with a command that keeps tha stout open

            Args:
                shell_command: the command to be launched on the shell. str or unicode
                stop_command: what terminates shell_command. str or unicode Default Ctrl-D
                encoding: the encoding used by shell_command output. str
                max_chars: maximum chars to be read from standard output before termiating shell_command. integer

            Returns:
                the output of shell command before terminating it or before it ends to print
        '''
        self.lock.acquire()
        self.client.send(shell_command+'\n')
        previous_encoding, self.client.encoding = self.client.encoding, encoding
	# give some time to fill the buffer
        time.sleep(.1)
        out = str()
        for packet in self.client.read():
            out += packet.decode(encoding)
            if len(out) >= max_chars:
                break
	#if the  shell did not auto terminate
        if not re.search(self.client.prompt_regex, out):
            self.client.send(stop_command)
            self.client.expect(re_strings=self.client.prompt_regex)
        self.client.encoding = previous_encoding
        self.lock.release()
        return out.replace(shell_command+'\r\n','')

    def getprocserver(self):
        '''Gets manage-procs util services present on the remote host

            Returns:
                A dictionary containing the manage-procs services
                The key is the service name and the item is a podman service object

                example:
                    { 'ioc1' : <ProcserverService>, }, 'ioc2' : <ProcserverService> }
        '''
        output = dict()
        if self.check_command('manage-procs'):
            output = { line.split()[0] : ProcserverService(line.split()[0]) for line in self.execute('manage-procs status').splitlines() }
        return output 
    
    def getpodman(self):
        '''Gets podman containers present on the remote host

            Returns:
                A dictionary containing the containers 
                The key is the se name and the item is a PodmanService object

                example:
                    { 'postgresql' : <PodmanService>, }, 'archiver-appliance' : <PodmanService> }
        '''
        output = dict()
        if self.check_command('podman'):
            outcome = self.execute('podman ps -a')
            if not 'Error:' in outcome:
                output = { line.split()[-1] : PodmanService(line.split()[-1]) for line in outcome.splitlines()[1:] } 
            else:
                print('ERROR IN PODMAN: ', outcome)
        return output 

    def interact(self, name, command):
        '''Sends a command to apply to the service

            Args:
                name: the name of te service you want to interact with. str or unicode
                command: the command you want to apply to the service. str or unicode

            Returns:
                the ouput of the command

                examples:
                    True
                    False
                    'Exited(0) 10 minutes ago' 
                    'Up for 2 weeks' 
        '''
        if name in self.services:
            if command == 'start':
                return self.services[name].start(self)
            elif command == 'stop':
                return self.services[name].stop(self)
            elif command == 'status':
                return self.services[name].status(self)
            elif command == 'out':
                return self.services[name].out(self)
        return False
    
    def stats(self):
        '''Gets statistics on the remote host status
           
            Returns:
                returns a dictionary containing cpu(%) 
                and free-memory(MegaBytes) information about the host
                
                example:
                    {"cpu":"3","freemem":"42357"}   
        '''
        out = self.execute('vmstat -S M').splitlines()[-1].split()
        return {'cpu': out[-5], 'freemem': out[3] }
    
    def flush(self):
        '''Clears the client input buffer '''
        for _ in self.client.read():
            pass

    def connect(self):
        '''Connects to the remote hosts and putss the available services in self .services
            
            Returns:
                True if it was able to connect otherwhise False
        '''
        outcome = self.login(self.user, self.passw)
        if outcome:
            self.services = {**self.getpodman(), **self.getprocserver()}
        return outcome
    
    def check_command(self, command):
        '''Checks if a command is available on the remote host

            Args:
                command: the command to check the availability on the remote host. str or unicode
            
            Returns:
                True if the commmand is available else false
        ''' 
        return self.execute('whereis ' + command) != command + ':'

    def login(self, username, password):
        '''Logs in self.client in the remote host using other params, if self.use_sudo is true upgrades ssh session to super user

            Args:
                username: the name of the user that will login in the remote host. str or unicode
                password: the password used for the login and eventually the sudo upgrade. str or unicode
            Retrurns:
                True if the login and eventual upgrade where succesful else False
        '''
        outcome = False
        self.lock.acquire()
        self.client.exit()
        self.client = RedExpect()
        try:
            self.client.login(hostname= self.host, username= username, password= password, timeout=2)
            if self.use_sudo:
                self.client.sudo(password)
            outcome = True
        except ExpectTimout:
            print('[+] Connection to ', self.host ,' timedout')
        finally:
            self.lock.release()
            return outcome
