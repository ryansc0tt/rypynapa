# This script defines a simple Napster API abstraction

__config_local_filename__ = 'rypynapa_app.cfg'
__json_local_filename__ = 'rypynapa_api_2.2.json'

import datetime, json, sys
import requests

from urllib import parse

import rypynapa_api_util as util #rypynapa_api_util.py

class NapsterAPI:

	_api_json = None                    # JSON object containing API definition
	_api_key = ''                       # API key for app
	_api_version_path = ''              # default path
	_auth_token = None                  # token object retrieved during authentication
	_auth_token_exp = datetime.date.min # token object expiration

	def _auth_prompt(self): pass  # callback function to prompt for user authorization
	def _param_prompt(self): pass # callback function to prompt for query params


	def __init__(self):

		# set API key for app
		app_config = self._load_app_config(['apikey'])
		self._api_key = app_config['apikey']

		# load JSON object containing API definition
		self._load_api_json()

	def _follow_api_path(self, path_list, api_dict):
		# TODO: handle path values (e.g. Artists/Art.*), POST/PUT/DELETE items
		# (e.g. me/favories), and potential empty path after end '/'
		for api in api_dict['apis']:
			if api['path'] == path_list[0]:
				if len(path_list) > 1:
					api = self._follow_api_path(path_list[1:], api)
				if 'method' in api.keys(): # valid endpoint
					return api

		return {} #empty if not resolved

	def _load_api_json(self):

		# load json from file
		with open(__json_local_filename__, 'r') as file:
			self._api_json = json.load(file)
		
		if self._api_json == None:
			sys.exit('API definition was not loaded from file %s' % (__json_local_filename__))
		else:
			self._api_version_path = 'v%s' % (self._api_json['api_version']) #set default path

	def _load_app_config(self, config_app_options=[]):

		# required config options from file
		config_app_items = util.read_config(__config_local_filename__, 'napster_app')

		if not (
			all(option in config_app_items for option in config_app_options)):
			sys.exit('Required API options were not read from config file %s' %
				(__config_local_filename__))
		else:
			return config_app_items

	def _load_auth_token(self):

		# try stored data
		shelved_auth_token = util.unshelve_dict('auth_token')

		if len(shelved_auth_token) > 0:
			self._auth_token = shelved_auth_token['auth_token_data']
			self._auth_token_exp = shelved_auth_token['auth_token_exp']

		# prompt for username / pass and request new token
		if self._auth_token == None or self._auth_token_exp <= datetime.datetime.now():

			user_pwd = self._auth_prompt()

			if len(user_pwd) == 2:

				new_auth_token = self.request_api(path='oauth/token', params={
					'username': user_pwd[0], 'password': user_pwd[1], 'grant_type': 'password'})

				if len(new_auth_token) > 0:
					self._set_auth_token(new_auth_token)
					self._save_auth_token()

		# or refresh token as needed (~ hourly)
		elif self._auth_token_exp - datetime.datetime.now() <= datetime.timedelta(hours=23):
			
			app_config = self._load_app_config(['apisecret']) # get API secret for app

			new_auth_token = self.request_api(path='oauth/access_token', params={
				'client_id': self._api_key, 'client_secret': app_config['apisecret'],
				'response_type': 'code', 'grant_type': 'refresh_token',
				'refresh_token': self._auth_token['refresh_token']})

			if len(new_auth_token) > 0:
					self._set_auth_token(new_auth_token)
					self._save_auth_token()

		if self._auth_token == None:
			sys.exit('Could not load token for authentication')

	def _save_auth_token(self):

		util.shelve_dict('auth_token', {'auth_token_data': self._auth_token,
			'auth_token_exp': self._auth_token_exp})

	def _set_auth_token(self, auth_token):

		self._auth_token = auth_token

		self._auth_token_exp = datetime.datetime.now() + datetime.timedelta(
				seconds=auth_token['expires_in'])

	# Registers callback function to prompt for user authorization 
	def register_auth_prompt(self, func):
		self._auth_prompt = func

	# Registers callback function to prompt for query params
	def register_param_prompt(self, func):
		self._param_prompt = func

	def request_api(self, path, params={}, headers={}, auth=()):

		path_query = parse.urlsplit(path) #assume correctly formatted path/query

		# follow the requested path to get API endpoint
		request_path = path_query.path.split('/')
		requested_api = self._follow_api_path(request_path, self._api_json)
		
		if len(requested_api) < 1: #try prepending default path
			request_path.insert(0, self._api_version_path)
			requested_api = self._follow_api_path(request_path, self._api_json)

		# perform request if we have a valid endpoint
		if len(requested_api) < 1:

			sys.exit('Endpoint %s was not found in API definition loaded from file %s' % (
				path_query.path, __json_local_filename__))

		else:
			
			# handle authentication
			if requested_api['user_auth_req']:

				# load token
				if self._auth_token == None:
					self._load_auth_token()

				if self._auth_token != None:
					headers = {'Authorization': 'Bearer %s' % (self._auth_token['access_token']
						)}

			# set query params (explicit params > path/query >  user prompt)
			if 'params' in requested_api and len(params) < 1:

				if (path_query.query != ''):

					# parse params from path/query (if any)
					path_query_params = parse.parse_qs(path_query.query)

					if len(path_query_params) > 0:
						for api_param in requested_api['params']:
							if api_param in path_query_params:
								params[api_param] = path_query_params[api_param]
				else:

					# request params via user prompt
					for api_param in requested_api['params']:
						value = self._param_prompt(api_param)
						if value != '': params[api_param] = value

			# add app credentials as required
			if requested_api['app_cred_req']:

				# get API secret for app
				app_config = self._load_app_config(['apisecret'])
				auth = (self._api_key, app_config['apisecret'])

			else:

				# API key required for other requests
				params['apikey'] = self._api_key
		
			request_url = '%s/%s' % (self._api_json['uri'], '/'.join(request_path))

			print('Requesting...')
			response = requests.request(method=requested_api['method'], url=request_url,
				params=params, headers=headers, auth=auth)
			print('[%s]' % (response.url)) 

			if (response and 
				response.headers['Content-Type'] == 'application/json; charset=utf-8'):
				return response.json()
			else:
				print('API returned status code %s' % (response.status_code))
				return response.content
