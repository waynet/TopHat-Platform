from Request.request import Request
from Request.requesterrors import NotFound, ServerError, Unauthorised, MethodNotAllowed, RequestError
from Networking.statuscodes import StatusCodes as CODE
from Model.authentication import requireapitoken

from Model.Mapper import usermapper as UM
from Model.Mapper import gamemapper as GM
from Model.Mapper import killmapper as KM
import MySQLdb as mdb

# Decorator
from Model.authentication import requireapitoken

class Kills(Request):

	''' 
		API Documentation
		Documentation for the Core Request of Games is available from the TopHat wiki at:
		http://wiki.tophat.ie/index.php?title=Core_Requests:_Kills
	'''

	def __init__(self):
		super(Kills, self).__init__()

	@requireapitoken
	def _doGet(self):
		try:
			
			KillMapper = KM.KillMapper()
			
			if self.arg is not None:
				if self.arg.isdigit():
					# Get the user by ID
					kill = KillMapper.find(self.arg)
				else:
					raise RequestError(CODE.BAD_REQUEST, "Kill must bed requested by ID")

				if kill is not None:
					return self._response(kill.dict(), CODE.OK)
				else:
					raise NotFound("This kill does not exist")
			
			else:

				offset = 0
				kills = KillMapper.findAll(offset, offset+50)

				killslist = []

				for kill in kills:
					killslist.append(kill.dict())

				killdict = {"kills":killslist, "pagination_offset":offset, "max_perpage": 50}

				return self._response(killdict, CODE.OK)

		except mdb.DatabaseError, e:
				raise ServerError("Unable to search the kill database (%s: %s)" % e.args[0], e.args[1])

		return self._response({}, CODE.UNIMPLEMENTED)

	@requireapitoken
	def _doPost(self, dataObject):
		return self._response({}, CODE.UNIMPLEMENTED)

	@requireapitoken
	def _doPut(self, dataObject):
		return self._response({}, CODE.UNIMPLEMENTED)

	@requireapitoken
	def _doDelete(self):
		return self._response({}, CODE.UNIMPLEMENTED)