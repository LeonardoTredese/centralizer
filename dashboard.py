from flask import Flask, render_template
from remote import Remote
from config import get_configuration, extract_args

app = Flask(__name__)
app.secret_key = b'\xdb\x89\x11\xcb\x1e\x1f\x01#_\xff6\xa4\xb9\x1a-\x03'
app.remote_hosts = dict()

@app.before_first_request
def startup():
    print(get_configuration().sections())
    app.remote_hosts = { arg[0]:Remote(*arg[1:]) for arg in extract_args(get_configuration())}
    for host in app.remote_hosts:
        print('[+] Connecting to:', host)
        reconnect(host)

    

@app.route('/<remote_host>/reconnect')
def reconnect(remote_host):
	app.remote_hosts[remote_host].connect()
	return 'reconnected'

@app.route('/')
def index():
	return render_template('index.html', machines = { host_name : list(remote.services.keys()) for host_name, remote in app.remote_hosts.items() })

@app.route('/<remote_host>/<service_name>/<command>')
def command(remote_host, service_name, command):
	if command in ['start', 'stop', 'status', 'out']:
		try:
			return { command : app.remote_hosts[remote_host].interact(service_name,command)}
		except BaseException as e:
			print(e)
			return 'Internal Server Error', 500
	return 'command not found', 404

@app.route('/<remote_host>/sys')
def system_remote_info(remote_host):
	try:
		return app.remote_hosts[remote_host].stats()
	except BaseException as e:
		print(e)
		return 'Internal Server Error', 500


if __name__ == '__main__':
    app.run()
