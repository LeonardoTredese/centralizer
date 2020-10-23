from flask import Flask, render_template
from remote import Remote
from config import get_configuration, extract_args

app = Flask(__name__)
app.secret_key = b'\xdb\x89\x11\xcb\x1e\x1f\x01#_\xff6\xa4\xb9\x1a-\x03'
app.remote_hosts = dict()

@app.before_first_request
def startup():
    ''' Tries to connect via ssh to the host(s) given in the configuration file(s)
        found in the default path (${HOME}/.centralizer/config/)
    '''
    print(get_configuration().sections())
    app.remote_hosts = { arg[0]:Remote(*arg[1:]) for arg in extract_args(get_configuration())}
    for host in app.remote_hosts:
        print('[+] Connecting to:', host)
        print('[+] ', reconnect(host))
    

@app.route('/<remote_host>/reconnect')
def reconnect(remote_host):
    ''' Reconnects to host indicated by $remote_host
        
        Args:  
            remote_host: 
                the name (chose in the configuration) of the host you want to reconnect to. str or unicode
        Returns:
            a dictionary containing the status of the operation which is connected,
            the status will be 'connected' if and only if the name of the host is
            present and the ssh reconnection was succesfull else 'failes'
            
            example:
                { 'status' : 'connected' }
    '''
    return { 'status' :'connected' if remote_host in app.remote_hosts and app.remote_hosts[remote_host].connect() else 'failed'}

@app.route('/')
def index():
    '''Creates the web interface
    
        Returns:
            the html page with the hosts. if a host is connected the page will also contain the its services
    '''
    m  = { host_name : list(remote.services.keys()) for host_name, remote in app.remote_hosts.items() }
    return render_template('index.html', machines = m)

@app.route('/<remote_host>/<service_name>/<command>')
def command(remote_host, service_name, command):
    '''Sends the command to a remote service
    
        Args:
            service_name: the name of the service you want to control. str or unicode
            remote_host: the name of the host on which the service is. str or unicode
            command: a a string between start, stop, status and out. str or unicode
        
        Returns:
            If the command, service and host are valid returns a ditionary containing the name
            of the command and its output
            
            examples:
                { 'start': True }
                { 'stop' : False }
                { 'status' : 'Up for 2 weeks' }
                { 'out' : '[10:00] [INFO] No Surprises' }
            
            If an error happens while running the command a tuple with the corrisponding error is returned
        
            examples:
                ('Internal Server Error', 500)
                ('Answer not found', 404)
    '''
    if command in ['start', 'stop', 'status', 'out'] and remote_host in app.remote_hosts:
        try:
            return { command : app.remote_hosts[remote_host].interact(service_name,command)}
        except BaseException as e:
            return 'Internal Server Error', 500
    return 'Answer not found', 404

@app.route('/<remote_host>/sys')
def system_remote_info(remote_host):
    '''Gets a remote host information about free ram and cpu usage

        Args:
            remote_host: the name of the host. str or unicode

        Returns:
            returns a dictionary containing cpu(%) 
            and free-memory(MegaBytes) information about it
           
            example:
                {"cpu":"3","freemem":"42357"}   
            
            If an error happens while running the command a tuple with the corrisponding error is returned
        
            examples:
                ('Internal Server Error', 500)
                ('Host not present', 404)
    '''
    if remote_host in app.remote_hosts:
        try:
            return app.remote_hosts[remote_host].stats()
        except BaseException as e:
    	    return 'Internal Server Error', 500
    return 'Host not present', 404

if __name__ == '__main__':
    app.run()
