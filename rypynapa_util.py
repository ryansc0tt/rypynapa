# This script defines utility functions

import json

# Save given JSON-serializeable [json_data] to given [filename: str]
# Returns True on completion
def save_json(filename, json_data):
	with open (filename, 'wt') as file:
		json.dump(json_data, file)
	return True