# This script defines utility functions

import shelve

from configparser import RawConfigParser

# Read given [section: str] as dictionary from local [filename: str] using RawConfigParser()
# Returns items as {option: setting} pairs, or empty dict
def read_config(filename, section):

	config = RawConfigParser()
	config_items = []
	
	if len(config.read(filename)) > 0:
		config_items = config.items(section)
	
	if len(config_items) > 0:
		return(dict(config_items))
	else:
		return {}

def shelve_dict(name, data={}):

	if len(data) > 0:
		with shelve.open(name) as db:
			db[name] = data
			db.close()

def unshelve_dict(name):

	data = {}
	db = shelve.open(name)

	try:
		data = db[name]
	finally:
		db.close()

	return data
