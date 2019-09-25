# This script implements a light wrapper of the Napster API with command-line interface

import click

from rypynapa_api_2_2 import NapsterAPI #rypynapa_api_2.2.py

_napster_api = NapsterAPI() #API object

@click.command()
@click.option('-p', '--path', prompt='Path', help='request/path?params')
def click_cmd(path):
	#TODO: add option to save response to local file ("archive")
	response_content = _napster_api.request_api(path)
	print('Response content:\n%s' % (response_content))



def click_prompt_auth():
	user = click.prompt('User authentication required\nUsername')
	pwd = click.prompt('Password', hide_input=True)
	return(user, pwd)

def click_prompt_param(param):
	param_val = click.prompt('%s' % (param),
		prompt_suffix='? ', default='', show_default=False)
	return param_val

if __name__ == "__main__":
	_napster_api.register_auth_prompt(click_prompt_auth)
	_napster_api.register_param_prompt(click_prompt_param)
	click_cmd()
