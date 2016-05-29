#!/usr/bin/env python2

""" DNS Resolver

This module contains a class for resolving hostnames. You will have to implement
things in this module. This resolver will be both used by the DNS client and the
DNS server, but with a different list of servers.
"""

import socket

from dns.classes import Class
from dns.types import Type

import dns.cache
import dns.message
import dns.rcodes

class Resolver(object):
    """ DNS resolver """
    
    def __init__(self, caching, ttl):
        """ Initialize the resolver
        
        Args:
            caching (bool): caching is enabled if True
            ttl (int): ttl of cache entries (if > 0)
        """
        self.caching = caching
        self.ttl = ttl
        if caching:
            self.cache = dns.cache.RecordCache(60)

    def gethostbyname(self, hostname):
        """ Translate a host name to IPv4 address.

        Currently this method contains an example. You will have to replace
        this example with example with the algorithm described in section
        5.3.3 in RFC 1034.

        Args:
            hostname (str): the hostname to resolve

        Returns:
            (str, [str], [str]): (hostname, aliaslist, ipaddrlist)
        """
        
        if self.caching:
            list_of_cnames = self.cache.lookup(hostname, Type.CNAME, Class.IN)
            list_of_ips = self.cache.lookup(hostname, Type.A, Class.IN)
            if list_of_ips is not None:
                return hostname + list_of_cnames + list_of_ips
        
        # Rootservers
        hints = [
        '198.41.0.4',
        '192.228.79.201',
        '192.33.4.12',
        '199.7.91.13',
        '192.203.230.10',
        '192.5.5.241',
        '192.112.36.4',
        '198.97.190.53',
        '192.36.148.17',
        '192.58.128.30',
        '193.0.14.129',
        '199.7.83.42',
        '202.12.27.33'
        ]
        
        timeout = 2 # Time waited for a response
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        # Create query
        question = dns.message.Question(hostname, Type.ANY, Class.IN)
        header = dns.message.Header(9001, 0, 1, 0, 0, 0)
        header.qr = 0
        header.opcode = 0
        header.rd = 0
        query = dns.message.Message(header, [question])
        
        targetfound = False
        hintindex = 0
        
        while hintindex < len(hints) and not targetfound:
            print "\n\n\nindex/len: " + str(hintindex) + "/" + str(len(hints))
            currenthint = hints[hintindex]
            print "currenthint: " + currenthint
            
            try:
                # Send query
                sock.sendto(query.to_bytes(), (currenthint, 53))
                
                # Receive response
                data = sock.recv(512)
                response = dns.message.Message.from_bytes(data)
                
                if response is not None:
                    if self.caching:
                        record = response.answers + response.authorities + response.additionals
                        self.cache.add_record(record)
                    # Do something with 'if response.header.aa == 1:'?
                    print "\nanswers:"
                    for thing in response.answers:
                        if thing.type_ in [1,2,5]:
                            print Type.to_string(thing.type_)
                            print thing.name
                            print thing.rdata.data
                            print "\n!!!\nFOUND IT\n!!!"
                            targetfound = True
                    print "\nauthorities:"
                    for thing in response.authorities:
                        if thing.type_ in [1,2,5]:
                            print Type.to_string(thing.type_)
                            print thing.name
                            print thing.rdata.data
                    print "\nadditionals:"
                    for thing in response.additionals:
                        if thing.type_ in [1,2,5]:
                            print Type.to_string(thing.type_)
                            print thing.name
                            print thing.rdata.data
                            if thing.rdata.data is not None and thing.rdata.data not in hints:
                                hints.append(thing.rdata.data)
            except socket.timeout:
                print "Server timed out"
            hintindex += 1
            
        if targetfound:
            # Get data
            aliases = []
            for additional in response.additionals:
                if additional.type_ == Type.CNAME:
                    aliases.append(additional.rdata.data)
            addresses = []
            for answer in response.answers:
                if answer.type_ == Type.A:
                    addresses.append(answer.rdata.data)

            return hostname, aliases, addresses
        return hostname, [], []
