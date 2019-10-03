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

# Save given [data: dict] to persistent file [name: str] using shelve()
def shelve_dict(name, data=None):

	if data is None: data = {} # default arg

	if len(data) > 0:
		with shelve.open(name) as db:
			db[name] = data
			db.close()

# Retrieve data from persistent file [name: str] using shelve()
# Returns data (expected as dict)
def unshelve_dict(name):

	data = {}
	db = shelve.open(name)

	try:
		data = db[name]
	finally:
		db.close()

	return data
