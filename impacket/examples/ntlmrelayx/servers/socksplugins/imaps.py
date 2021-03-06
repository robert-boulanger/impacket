#!/usr/bin/env python
# Copyright (c) 2013-2017 CORE Security Technologies
#
# This software is provided under under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# A Socks Proxy for the IMAPS Protocol
#
# Author:
#  Dirk-jan Mollema (@_dirkjan) / Fox-IT (https://www.fox-it.com)
#
# Description:
#  A simple SOCKS server that proxies a connection to relayed IMAPS connections
#
# ToDo:
#
from impacket import LOG
from impacket.examples.ntlmrelayx.servers.socksplugins.imap import IMAPSocksRelay
from impacket.examples.ntlmrelayx.utils.ssl import SSLServerMixin
from OpenSSL import SSL

# Besides using this base class you need to define one global variable when
# writing a plugin:
PLUGIN_CLASS = "IMAPSSocksRelay"
EOL = '\r\n'

class IMAPSSocksRelay(SSLServerMixin, IMAPSocksRelay):
    PLUGIN_NAME = 'IMAPS Socks Plugin'
    PLUGIN_SCHEME = 'IMAPS'

    def __init__(self, targetHost, targetPort, socksSocket, activeRelays):
        IMAPSocksRelay.__init__(self, targetHost, targetPort, socksSocket, activeRelays)

    @staticmethod
    def getProtocolPort():
        return 993

    def skipAuthentication(self):
        LOG.debug('Wrapping IMAP client connection in TLS/SSL')
        self.wrapClientConnection()
        if not IMAPSocksRelay.skipAuthentication(self):
            # Shut down TLS connection
            self.socksSocket.shutdown()
            return False
        # Change our outgoing socket to the SSL object of IMAP4_SSL
        self.relaySocket = self.session.sslobj
        return True

    def tunnelConnection(self):
        keyword = ''
        tag = ''
        while True:
            try:
                data = self.socksSocket.recv(self.packetSize)
            except SSL.ZeroReturnError:
                # The SSL connection was closed, return
                return
            # Set the new keyword, unless it is false, then break out of the function
            result = self.processTunnelData(keyword, tag, data)
            if result is False:
                return
            # If its not false, it's a tuple with the keyword and tag
            keyword, tag = result
