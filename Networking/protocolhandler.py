class ProtocolHandler:

	protocol = None
	protocolName = None

	def __init__(self, protocolName):
		self.protocolName = protocolName
		self.protocol = self.__importProtocol()

	def __importProtocol(self):
		title = self.protocolName.title()

		mod = self.import_item('Networking.Protocols.%s.networking' % title)

		getattr(mod, "Networking")()

	def import_item(self, name):
	    """Import and return bar given the string foo.bar."""

	    print name
	    package = '.'.join(name.split('.')[0:-1])
	    obj = name.split('.')[-1]

	    if package:
	        module = __import__(package,fromlist=[obj])
	        try:
	            pak = module.__dict__[obj]
	        except KeyError:
	            raise ImportError('No module named %s' % obj)
	        return pak
	    else:
	        return __import__(obj)