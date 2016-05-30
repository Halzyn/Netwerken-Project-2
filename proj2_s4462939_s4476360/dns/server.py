#!/usr/bin/env python2

""" A recursive DNS server

This module provides a recursive DNS server. You will have to implement this
server using the algorithm described in section 4.3.2 of RFC 1034.
"""

import socket
from threading import Thread


class RequestHandler(Thread):
    """ A handler for requests to the DNS server """

    def __init__(self, data, addr, s):
        """ Initialize the handler thread """
        super().__init__()
        self.daemon = True
        self.data = data
        self.addr = addr
        self.s = s
        
    def run(self):
        """ Run the handler thread """
        dnsrequest = Message.from_bytes(self.data)
        resolver = Resolver(True, self.ttl)
        answers = []
        authorities = []
        additionals = []
        for question in dnsrequest.questions:
            if dnsrequest.qclass == 1: # IN
                if dnsrequest.qtype == 1: # A
                    if dnsrequest.header.rd == 1: # recursive
                        hostname, aliases, addresses = resolver.gethostbyname(dnsrequest.qname)
                        for address in addresses:
                            answers.append(ResourceRecord(dnsrequest.qname, 1, 1, self.ttl, ARecordData(address)))
        header = Header(dnsrequest.header.ident, 0, 0, len(answers), len(authorities), len(additionals))
        dnsresponse = Message(header, [], answers, authorities, additionals)
        
        self.s.sendto(dnsresponse.to_bytes(), self.addr)
                


class Server(object):
    """ A recursive DNS server """

    def __init__(self, port, caching, ttl):
        """ Initialize the server
        
        Args:
            port (int): port that server is listening on
            caching (bool): server uses resolver with caching if true
            ttl (int): ttl for records (if > 0) of cache
        """
        self.caching = caching
        self.ttl = ttl
        self.port = port
        self.done = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def serve(self):
        """ Start serving request """
        self.s.bind(('', self.port))
        while not self.done:
            data, addr = self.s.recvfrom(1024)
            handler = RequestHandler(data, addr, s)
            handler.start()

    def shutdown(self):
        """ Shutdown the server """
        self.s.close() # also performs shutdown()
        self.done = True