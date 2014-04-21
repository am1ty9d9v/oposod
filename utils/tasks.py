import sys
import redis
import socket

from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor

from autobahn.websocket import listenWS, connectWS
from autobahn.wamp import WampServerFactory, WampServerProtocol, \
    WampClientProtocol, WampClientFactory

channel_name = None
REDIS_OBJ = redis.StrictRedis(db=10)
PUBSUB = REDIS_OBJ.pubsub()


class PubSubServer1(WampServerProtocol):

    def onSessionOpen(self):
        self.registerForPubSub("notifications:", prefixMatch=True)
        self.registerForPubSub("notifications:all")


def runwamp(logfile=None, debug=True):
    if logfile is None:
        log.startLogging(sys.stdout)

    '''
    factory = WampServerFactory("ws://%s:9000" % socket.gethostname(),
                                debugWamp=debug)
    '''

    factory = ""
    host_name = socket.gethostname()
    if host_name == 'ip-172-31-29-49':
        factory = WampServerFactory("ws://oposod.com:9000", debugWamp=None)
    else:
        factory = WampServerFactory("ws://localhost:9000", debugWamp=debug)
    factory.protocol = PubSubServer1
    factory.setProtocolOptions(allowHixie76=True)
    listenWS(factory)

    webdir = File(".")
    web = Site(webdir)
    reactor.listenTCP(9090, web)

    reactor.run()


class PubSubClient1(WampClientProtocol):

    def onSessionOpen(self):
        self.subscribe(channel_name, self.onSimpleEvent)
        self.sendSimpleEvent()

    def onSimpleEvent(self, topicUri, event):
        print "Event", topicUri, event

    # This is supposed to run forever unless interrupted...
    def sendSimpleEvent(self):
        for i in PUBSUB.listen():
            if i['data'] == 'EOM':
                PUBSUB.unsubscribe(channel_name)
            else:
                #print "Printing Redis Data: ", i
                #print "Channel to publish to: ", channel_name
                self.publish(channel_name, i['data'])
                reactor.callLater(1, self.sendSimpleEvent)
                break


def publisher(c_name="all", debug=True):
    log.startLogging(sys.stdout)
    if c_name != "all":
        channel_name = "notifications:%s" % c_name
    else:
        channel_name = "notifications:all"
    #print "user name in Publisher: ", channel_name

    PUBSUB.subscribe(channel_name)

    '''
    factory = WampClientFactory("ws://%s:9000" % socket.gethostname(),
                                debugWamp=debug)
    '''

    factory = WampClientFactory("ws://localhost:9000", debugWamp=debug)
    factory.protocol = PubSubClient1
    connectWS(factory)

    reactor.run()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) > 1:
            if sys.argv[1] == "rw":
                runwamp(debug=True)
            else:
                print "running publisher"
                print "c_name: ", sys.argv[1]
                publisher(c_name=sys.argv[1])
        else:
            publisher()
