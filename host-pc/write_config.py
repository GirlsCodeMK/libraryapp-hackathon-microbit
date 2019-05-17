import configparser
config = configparser.ConfigParser()
config['DEFAULT'] = {
    'username': 'Molly',
    'token': 'e25000699092945b68e8a377ccc4635549e5851e',
    'hostname': 'localhost:8000/library/api/v1/',
    }

with open('microbit.ini', 'w') as configfile:
  config.write(configfile)