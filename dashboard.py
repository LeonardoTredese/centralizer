#!/usr/bin/python3
from flask import Flask, render_template, url_for
from remote import Remote

app=Flask(__name__)
remotes_list = [
               ('10.6.0.41', 'training', 'e3password'),
			   ('10.6.0.75', 'root', 'e3password')
			  ]
remotes_list = { arg[0]:Remote(*arg) for arg in remotes_list}

@app.route('/')
def hello():
	return {'remotes': list(remotes_list.keys())}

@app.route('/<remote_host>/<service_name>/start')
def start_service(remote_host, service_name):
	return { service_name: remotes_list[remote_host].start_service(service_name)}

@app.route('/<remote_host>/<service_name>/stop')
def stop_service(remote_host, service_name):
	return { service_name: remotes_list[remote_host].stop_service(service_name)}

@app.route('/<remote_host>/<service_name>/status')
def status_service(remote_host, service_name):
	return { service_name: remotes_list[remote_host].status_service(service_name)}

@app.route('/<remote_host>/list')
def list_remote_services(remote_host):
	return { 'services': list(remotes_list[remote_host].services.keys())}

@app.route('/<remote_host>/sys')
def system_remote_info(remote_host):
	return remotes_list[remote_host].stats()

if __name__ == '__main__':
    app.run()
