from twisted.web import server, resource
from twisted.internet import reactor
from Model.jsonparser import *

def putRequest(instance, client, data):

	data = data.rstrip()
	data = data.split('\n', 1) # separate header and JSON

	try:
		data_object = JsonParser.getObject(data[1]) 
	except ValueError:
		return -1 

	header_http = ( data[0].split('\n') )[0]
	data_path = ( header_http.split() )[1]
	# TODO: auth
	# TODO: DB call
