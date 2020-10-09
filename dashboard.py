#!/usr/bin/python3
from flask import Flask, render_template, session
from remote import Remote

app=Flask(__name__)
app.secret_key = b'\xdb\x89\x11\xcb\x1e\x1f\x01#_\xff6\xa4\xb9\x1a-\x03'

@app.route('/<remote_host>/reconnect')
def reconnect(remote_host):
	remote_hosts[remote_host].connect()
	return 'reconnected'

@app.route('/')
def index():
	return render_template('index.html', machines = { host_name : list(remote.services.keys()) for host_name, remote in remote_hosts.items() })

@app.route('/remote_hosts')
def remotes():
	return { host_name : list(remote.services.keys()) for host_name, remote in remote_hosts.items()}

@app.route('/<remote_host>/<service_name>/<command>')
def command(remote_host, service_name, command):
	if command  in ['start', 'stop', 'status', 'out']:
		try:
			return { command : remote_hosts[remote_host].interact(service_name,command)}
		except BaseException as e:
			print(e)
			return 'Internal Server Error', 500
	return 'command not found', 404

@app.route('/<remote_host>/sys')
def system_remote_info(remote_host):
	try:
		return remote_hosts[remote_host].stats()
	except BaseException as e:
		print(e)
		return 'Internal Server Error', 500

remote_hosts_args = [
#				('127.0.0.1','leonardo','', False)
             ('10.6.0.41', 'training', 'e3password', True),
 		   ('10.6.0.75', 'root', 'e3password', False)
			   ]
remote_hosts = { arg[0]:Remote(*arg) for arg in remote_hosts_args }



for host in remote_hosts:
	reconnect(host)

if __name__ == '__main__':
    app.run()
