#!/usr/bin/env python2
#encoding=utf8

"""A cache for resource records

This module contains a class which implements a cache for DNS resource records,
you still have to do most of the implementation. The module also provides a
class and a function for converting ResourceRecords from and to JSON strings.
It is highly recommended to use these.
"""

import json
import sys
import time

from dns.resource import ResourceRecord, RecordData
from dns.types import Type
from dns.classes import Class


class ResourceEncoder(json.JSONEncoder):
    """ Convert ResourceRecord to JSON
    
    Usage:
        string = json.dumps(records, cls=ResourceEncoder, indent=4)
    """
    def default(self, obj):
        if isinstance(obj, ResourceRecord):
            return {
                "name": obj.name,
                "type": Type.to_string(obj.type_),
                "class": Class.to_string(obj.class_),
                "ttl": obj.ttl,
                "rdata": obj.rdata.data
			"time_saved": obj.time_saved
            }
        return json.JSONEncoder.default(self, obj)


def resource_from_json(dct):
    """ Convert JSON object to ResourceRecord
    
    Usage:
        records = json.loads(string, object_hook=resource_from_json)
    """
    name = dct["name"]
    type_ = Type.from_string(dct["type"])
    class_ = Class.from_string(dct["class"])
    ttl = dct["ttl"]
    rdata = RecordData.create(type_, dct["rdata"])
	time_saved = dct["time_saved"]
    return ResourceRecord(name, type_, class_, ttl, rdata)


class RecordCache(object):
    """ Cache for ResourceRecords """
	
    CACHE_FILE = 'cache'
	
    def __init__(self):
        """ Initialize the RecordCache
        
        Args:
            ttl (int): TTL of cached entries (if > 0)
        """
        reload(sys)
        sys.setdefaultencoding('utf8')
        self.records = []
        self.read_cache_file()
		
	def __del__(self):
		self.write_cache_file()
	
    def lookup(self, dname, type_, class_):
        """ Lookup resource records in cache

        Lookup for the resource records for a domain name with a specific type
        and class.
        
        Args:
            dname (str): domain name
            type_ (Type): type
            class_ (Class): class
        """
        for record in self.records:
			if (record.name == dname and record.type_ == type_ and record.class_ == class_):
				return record
    
	"""def update():
	current_time = int(time.time())
		for record in self.records:
			if (record.time_saved + record.ttl < current_time):
				self.records.remove(record)""" #This was meant for TTL but it ended up not working.
	
    def add_record(self, record):
        """ Add a new Record to the cache
        
        Args:
            record (ResourceRecord): the record added to the cache
        """
        self.records.append(record)
    
    def read_cache_file(self):
        """ Read the cache file from disk """
        try:
            with open(self.CACHE_FILE, 'r+') as json_data:
                self.records = json.loads(json_data.read().decode('utf-8', 'ignore').encode('utf-8'), object_hook=resource_from_json) #Converting JSON to ResourceRecord
        except IOError:
                print "can't open file"

    def write_cache_file(self):
        """ Write the cache file to disk """
        with open(self.CACHE_FILE, 'w+') as json_data:
            json.dump(self.records, json_data, cls=ResourceEncoder, indent=4, ensure_ascii=False) #converting ResourceRecord to JSON


