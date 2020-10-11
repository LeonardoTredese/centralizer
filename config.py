from configparser import ConfigParser
from os import listdir
from os.path import isfile, join



def get_configuration(directory= "/home/leonardo/centralizer/configs"):
	parser = ConfigParser()
	for configFile in listdir(directory):
		configFile = join(directory, configFile)
		if isfile(configFile):
			parser.read(configFile)
	return parser

def extract_args(parser):
	arguments = list()
	for name in parser.sections():
		config = parser[name]
		if 'hostname' in config and 'username' in config and 'password' in config:
			arguments.append((name, 
							  config['hostname'],
							  config['username'],  
							  config['password'], 
							  config.get('use_sudo', 'no') == 'yes'))
	return arguments
