#!/usr/bin/env python

from twisted.internet import ssl, reactor, protocol
from twisted.protocols.basic import LineReceiver

'''

  This program is in the early stages.

  This is the node configuration server.
  Look in ssl_client.lua to learn how this will be used.
  
  This program needs to be combined with dns_sd.py

  The idea is that the node configuration server
  will be controlled by a web interface, and to allow
  that, it needs to act as a web server as well.

  Rhodey is currently working on the web gui.

'''

class ChainedOpenSSLContextFactory(ssl.DefaultOpenSSLContextFactory):
    def __init__(self, privateKeyFileName, certificateChainFileName,
                 sslmethod=ssl.SSL.TLSv1_METHOD):
        """
        @param privateKeyFileName: Name of a file containing a private key
        @param certificateChainFileName: Name of a file containing a certificate chain
        @param sslmethod: The SSL method to use
        """
        self.privateKeyFileName = privateKeyFileName
        self.certificateChainFileName = certificateChainFileName
        self.sslmethod = sslmethod
        self.cacheContext()
    
    def cacheContext(self):
        ctx = ssl.SSL.Context(self.sslmethod)
        ctx.use_certificate_chain_file(self.certificateChainFileName)
        ctx.use_privatekey_file(self.privateKeyFileName)
        self._context = ctx


class NodeConfig(LineReceiver):
    """Node Configurator protocol"""
    delimiter = "\n"

    def sendConfigCommand(self):

        self.sendLine("CONFIG:1")
        self.sendLine("FILE:0003:foo:fee77fce8a77d5c5bc8948693d48f75f:0000000000000015")
        self.transport.write("this is a hest\n")

    def connectionMade(self):
        print "Got connection!"

    def lineReceived(self, line):
        if line == "GIMME_CONFIG":
            self.sendConfigCommand()
        else:
            print "Unknown request: " + line
            print "Client disconnected"
            self.transport.loseConnection()


    def rawDataReceived(self, data):
        "As soon as any data is received, write it back."
        self.transport.write(data)


def start():

    port = 8000

    factory = protocol.Factory()
    factory.protocol = NodeConfig
    reactor.listenSSL(port, factory,
                      ChainedOpenSSLContextFactory(
            privateKeyFileName="certs/nodeconf.key",
            certificateChainFileName="certs/nodeconf_chain.crt", 
            sslmethod = ssl.SSL.TLSv1_METHOD))

    print "Listening on port " + str(port)
    reactor.run()


if __name__ == "__main__":
    start()
