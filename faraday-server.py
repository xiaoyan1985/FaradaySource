#!/usr/bin/env python2.7
# Faraday Penetration Test IDE
# Copyright (C) 2016  Infobyte LLC (http://www.infobytesec.com/)
# See the file 'doc/LICENSE' for the license information

import os
import argparse
import functools
import server.config
import twisted.web

from twisted.internet import ssl, reactor, error
from twisted.protocols.tls import TLSMemoryBIOFactory
from twisted.web import proxy


class HTTPProxyClient(proxy.ProxyClient):
    def connectionLost(self, reason):
        if not reason.check(error.ConnectionClosed):
            # XXX(mrocha): Better logging!
            print "ERROR:", reason.value
        return proxy.ProxyClient.connectionLost(self, reason)


class HTTPProxyClientFactory(proxy.ProxyClientFactory):
    protocol=HTTPProxyClient


class HTTPProxyResource(proxy.ReverseProxyResource):
    def __init__(self, host, port, path='', reactor=reactor, ssl_enabled=False):
        proxy.ReverseProxyResource.__init__(self, host, port, path, reactor)
        self.__ssl_enabled = ssl_enabled

    def proxyClientFactoryClass(self, *args, **kwargs):
        """
        Overwrites proxyClientFactoryClass to add a TLS wrapper to all
        connections generated by ReverseProxyResource protocol factory
        if enabled.
        """
        client_factory = HTTPProxyClientFactory(*args, **kwargs)
        
        if self.__ssl_enabled:
            with open(server.config.ssl.certificate) as cert_file:
                cert = ssl.Certificate.loadPEM(cert_file.read())

            # TLSMemoryBIOFactory is the wrapper that takes TLS options and
            # the wrapped factory to add TLS to connections
            return TLSMemoryBIOFactory(
                ssl.optionsForClientTLS(self.host.decode('ascii'), cert),
                isClient=True, wrappedFactory=client_factory)
        else:
            return client_factory
    
    def getChild(self, path, request):
        """
        Keeps the implementation of this class throughout the path
        hierarchy
        """
        child = proxy.ReverseProxyResource.getChild(self, path, request)
        return HTTPProxyResource(
            child.host, child.port, child.path, child.reactor,
            ssl_enabled=self.__ssl_enabled)


class FaradayServer(object):
    def __init__(self, enable_ssl=False):
        self.__ssl_enabled = enable_ssl
        self.__config_server()
        self.__config_couchdb_conn()
        self.__build_server_tree()
    
    def __config_server(self):
        self.__bind_address = server.config.faraday_server.bind_address
        self.__listen_port = int(server.config.faraday_server.port)

    def __config_couchdb_conn(self):
        self.__couchdb_host = server.config.couchdb.host

        if self.__ssl_enabled:
            self.__couchdb_port = int(server.config.couchdb.ssl_port)
            ssl_context = self.__load_ssl_certs()
            self.__listen_func = functools.partial(reactor.listenSSL,
                                                   contextFactory=ssl_context)
        else:
            self.__couchdb_port = int(server.config.couchdb.port)
            self.__listen_func = reactor.listenTCP

    def __load_ssl_certs(self):
        certs = (server.config.ssl.keyfile, server.config.ssl.certificate)
        if not all(certs):
            # XXX(mrocha): Better logging!
            print "SSL certificates not set"
            exit(1)
        return ssl.DefaultOpenSSLContextFactory(*certs)

    def __build_server_tree(self):
        self.__root_resource = self.__build_proxy_resource()

    def __build_proxy_resource(self):
        return HTTPProxyResource(
            self.__couchdb_host,
            self.__couchdb_port,
            ssl_enabled=self.__ssl_enabled)

    def run(self):
        site = twisted.web.server.Site(self.__root_resource)
        self.__listen_func(
            self.__listen_port, site,
            interface=self.__bind_address)
        reactor.run()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ssl', action='store_true', help='Enable HTTPS')
    return parser.parse_args()

def main():
    cli_arguments = parse_arguments()
    server = FaradayServer(enable_ssl=cli_arguments.ssl)
    server.run()
    
if __name__ == '__main__':
    main()

