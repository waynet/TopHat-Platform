from asyncore import dispatcher, dispatcher_with_send
from sys import exit
from threading import Thread
from Queue import Queue, Empty as QueueEmpty
from socket import AF_INET6 as ipv6, SOCK_STREAM as tcp, socket,inet_aton, error as SocketError, timeout as SocketTimeout
from Model.tophatclient import TopHatClient
class Transport(object):
		class Peer(object):
				def __init__(self, port, address):
						self.port =port
						self.host =address
		def __init__(self, socket,handle):
				#if type(socket) is not type(socket()):
				#		raise TypeError("Expected socket type got %s type instead" % type(socket))
				self.__handle = handle
				self.__sock=socket
		def write(self, data):
				try:
						self.__sock.send(data)
				except SocketError:
						return
		def loseConnection(self):
				self.__handle.close()
		def getPeer(self):
				try:
						tmp=self.__sock.getpeername()
				except SocketError:
					return None
				return Transport.Peer(tmp[1], tmp[0])



class TopHatThread(Thread):
		def __init__(self,queue,config):
				Thread.__init__(self)
				self.queue=queue
				self.config=config
				self.stop=False
				self.transport=None
		def run(self):
				while not self.stop:
						data = self.queue.get()
						from tophathttpparser import HTTPParser
						self.transport=Transport(data[0],data[2])
						if self.transport is None:
								continue
						client = TopHatClient(transport=self.transport)
						HTTPParser(data[1], client)
						request_value=-1
						if str(client.state) == 'get':
							from getrequest import getRequest
							request_value = getRequest(client, data[1])

						elif str(client.state) == 'put':
							from putrequest import putRequest
							request_value = putRequest(client, data[1], self.config.LogFile)

						elif str(client.state) == 'post':
							from postrequest import postRequest
							request_value = postRequest(client, data[1], self.config.LogFile)

						elif str(client.state) == 'delete':
							from deleterequest import deleteRequest
							request_value = deleteRequest(client,data[1])

						elif str(client.state) == 'undef' or request_value is -1:
							respondToClient(self.transport,'HTTP/1.1 400 Bad Request')
							client.transport.loseConnection()
							
						client.transport.loseConnection()
						#del client
				return

class TopHatNetwork(dispatcher):
		__workers=[]
		__sockets=[]
		def __init__(self, family, config, host=None, port=443):
				dispatcher.__init__(self)
				self.queue = Queue()
				self.port=port
				self.host=host
				self.config=config
			
				for x in range(0,config.Threads):
						self.__workers.append(TopHatThread(self.queue, self.config))
				for x in self.__workers:
						x.daemon=True
						x.start()

				if host is not None:
						try:
								inet_aton(host)
						except SocketError:
								if family is not ipv6:
										exit(1)
								else:
										pass
				self.create_socket(family, tcp)
				if host is None:
						if family is ipv6:
							self.bind(("::", port))

						else:
							self.bind(("0.0.0.0", port))
				else:
						self.bind((host, 443))
				self.set_reuse_addr()
				self.listen(5)
				return
		def handle_accept(self):
				from Encryption.sslencryption import SSLEncryption
				sock, addr = self.accept()
				sock=self.config.EncryptionMethod(sock._sock,config=self.config)
				client=ClientHandle(sock, self.queue)
				self.__sockets.append((sock,addr,client))
		def shutdown(self):
				for x in self.__workers:
						x.stop=True
						del x

				for x in self.__sockets:
						x[2].close()
						del x
				self.close()
				return



class ClientHandle(dispatcher):
		def __init__(self, sock,queue):
				self.sock=sock
				self.queue=queue
				self.sendqueue = Queue()
				dispatcher.__init__(self, sock=sock)
				return
		def handle_read(self):
				try:
						data = self.recv(10240)
				except SocketTimeout:
						pass
				if len(data) >0:
						self.queue.put((self.sock,data,self))
				return
		def handle_close(self):
		#		my = TopHatClient(transport=Transport(self.sock,self))
		#		if my in TopHatClient:
		#				my.delete()
				return self.close()
	
		def writeable(self): return True
		def readable(self): return True

def respondToClient(transport, data):
		if type(transport) is not Transport:
				raise TypeError('Expected Transport type got %s type instead' % type(transport))
		
		transport.write(data + '\r\n')
		return