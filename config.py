from configparser import ConfigParser
from os import listdir
from os.path import isdir, expanduser, isfile, join



def get_configuration(directory= expanduser("~/.centralizer/config/")):
    '''Prepares a parser with all the config files contained in a directory

        Args:
            directory: the directory where the configuration files are stored. str or unicode, default: ~/.centralizer/config/

        Returns:
            A parser that contains all the file in the given directory. ConfigParser
    '''
    parser = ConfigParser()
    print(directory)
    if not isdir(directory):
        print('[+] This is not a directory: ', directory)
        print('[+] Not importing anything')
    else:    
        for configFile in listdir(directory):
            configFile = join(directory, configFile)
            if isfile(configFile):
                parser.read(configFile)
    return parser

def extract_args(parser):
    '''Extracts the information to build remotes from a given parser

        Args:
            parser: the parser with configuration file information. ConfigParser

        Returns:
            a list of tuples with the following stucture (name_of_the_remote,
                                                            hostname,
                                                            username,
                                                            password,
                                                            use_sudo)
    '''
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
