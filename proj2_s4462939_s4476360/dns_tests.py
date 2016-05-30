#!/usr/bin/env python2

import unittest
import sys
import subprocess
import dns.resolver

""" Tests for your DNS resolver and server """

portnr = 53
server = "localhost"

class TestResolver(unittest.TestCase):
    #subprocess.call("dns_client.py gaia.cs.umass.edu", shell=True)
    def test_FQDN(self):
        resolver = dns.resolver.Resolver(False, 0)
        hostname, aliases, addresses = resolver.gethostbyname("gaia.cs.umass.edu")
        self.assertEqual(addresses, ['128.119.245.12'])
        
    def test_incorrect_FQDN(self):
        resolver = dns.resolver.Resolver(False, 0)
        hostname, aliases, addresses = resolver.gethostbyname("gaia.cs.umas.edu")
        self.assertEqual(addresses, [])

class TestResolverCache(unittest.TestCase):
    pass


class TestServer(unittest.TestCase):
    pass


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="HTTP Tests")
    parser.add_argument("-s", "--server", type=str, default="localhost")
    parser.add_argument("-p", "--port", type=int, default=5001)
    args, extra = parser.parse_known_args()
    portnr = args.port
    server = args.server
    
    # Pass the extra arguments to unittest
    sys.argv[1:] = extra

    # Start test suite
    unittest.main()
