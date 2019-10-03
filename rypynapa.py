# This script implements a light wrapper of the Napster API with command-line interface

import click

import rypynapa_util as util #rypynapa_util.py

from rypynapa_api_2_2 import NapsterAPI #rypynapa_api_2.2.py

_napster_api = NapsterAPI() #API object

# Initiate interface, process input [path: str] (submit API request), and display response
# Optionally save response to [archive: str] file instead
@click.command()
@click.option('-p', '--path', prompt='Path', help='request/path?params')
@click.option('-a', '--archive', prompt=False, help='file to save response .json')
def click_cmd(path, archive):

	response_content = _napster_api.request_api(path)

	if archive == None or type(response_content) != dict:
		print('Response content:\n%s' % (response_content))
	else:
		# filename provided and JSON (presumably) returned
		if util.save_json(archive, response_content):
			print('Response content archived to %s' % (archive))

# Request user authorization using click.prompt()
# Returns (user, pwd) as str tuple
def click_prompt_auth():
	user = click.prompt('User authentication required\nUsername')
	pwd = click.prompt('Password', hide_input=True)
	return(user, pwd)

# Request query [param: str] using click.prompt()
# Returns param_val as str
def click_prompt_param(param):
	param_val = click.prompt('%s' % (param),
		prompt_suffix='? ', default='', show_default=False)
	return param_val

if __name__ == "__main__":
	_napster_api.register_auth_prompt(click_prompt_auth)
	_napster_api.register_param_prompt(click_prompt_param)
	click_cmd()
