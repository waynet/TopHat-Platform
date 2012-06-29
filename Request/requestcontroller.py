from requesterrors import RequestError
from request import Request

class RequestController:

	opcode = 0
	uri = None
	data = {}
	response = None

	def __init__(self, opcode, uri, data=None):
		self.opcode = opcode
		self.uri = uri

		self.data = {}
		if data is not None: 
			self.data = data

	def run(self):
		"""
			Runs the request
		"""
		try:
			request = self.__importRequest(self.uri)

			try:
				if self.opcode == 0:
					response = request.get()
				elif self.opcode == 1:
					response = request.post(self.data)
				elif self.opcode == 2:
					response = request.put(self.data)
				elif self.opcode == 3:
					response = request.delete()

				print response.code
				print response.data

				self.response = response
			except RequestError as e:
				print "Request Failed"

		except LookupError as e:
			print "The requested URL does not exist. uri = %s " % self.uri

	def __importRequest(self, uri):
		"""
			Given the URI it attempts to return an instance of the request class that handles that URI

			Arguements:
				uri - universal resource locator (eg. "/users/")

			Raises:
				LookupError: no mapping in config file
				ImportError: couldn't import the request file
				TypeError: if the loaded class is not a request object

		"""
		# get the request to load from the matching uri in the config
		request = self.__findRequest(uri)

		# import the request and create an instance of it
		modulename = "Request.Requests.%s" % request.lower()

		module = __import__(modulename, fromlist=[request])

		requestObject = getattr(module, request)()

		if not isinstance(requestObject, Request):
			raise TypeError("The mapping didn't load a Request object, it loaded a %s" % str(type(requestObject)))

		return requestObject

	def __findRequest(self, uri):
		"""
			Searches the config resources list to find the correct mapping of URI to Request class

			Arguements:
				uri

			Raises:
				LookupError - no resource/request mapping found in the config file
		"""
		from Common.config import TopHatConfig

		for entry in TopHatConfig.getKey("resources"):
			if entry[0] == uri:
				return entry[1]

		raise LookupError("No request/resource mappping found in the config file for URI %s" % uri)