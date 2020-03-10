from flask import Flask, render_template, url_for
import json 
import requests as req

app=Flask(__name__)
remotes_list= ['10.6.0.41:5000']

@app.route('/')
def hello():
	m = []
	for remote in remotes_list:
		sys_info = json.loads(req.get('/'.join(['http:/',remote,'sys'])).text)
		iocs_info = json.loads(req.get('/'.join(['http:/',remote,'list'])).text)
		m.append({'sys': sys_info, "iocs": iocs_info, 'remote_socket': remote})
	u = {
		"bootstrap_css": url_for('static', filename="bootstrap.min.css"),
		"bootstrap_js": url_for('static', filename="bootstrap.min.js"),
		"jquery_js": url_for('static', filename="jquery.min.js"),
	}
	return render_template('index.html', machines=m, urls=u)
