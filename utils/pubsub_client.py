import sys
import redis
import socket

from twisted.python import log
from twisted.internet import reactor

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol

channel_name = None
REDIS_OBJ = redis.StrictRedis(db=9)
PUBSUB = REDIS_OBJ.pubsub()


class PubSubClient1(WampClientProtocol):

    def onSessionOpen(self):
        self.subscribe(channel_name, self.onSimpleEvent)
        self.sendSimpleEvent()

    def onSimpleEvent(self, topicUri, event):
        print "Event", topicUri, event

    def sendSimpleEvent(self):
        for i in PUBSUB.listen():
            if i['data'] == 'EOM':
                PUBSUB.unsubscribe(channel_name)
            else:
                print "Printing Redis Data: ", i
                print "Channel to publish to: ", channel_name
                self.publish(channel_name, i['data'])
                reactor.callLater(2, self.sendSimpleEvent)
                break
        #reactor.callLater(2, self.sendSimpleEvent)

if __name__ == '__main__':

    log.startLogging(sys.stdout)
    #debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
    debug = True
    if len(sys.argv) > 1:
        channel_name = "notifications:%s:%s" % (sys.argv[1], sys.argv[2])
    else:
        channel_name = "notifications:all"

    PUBSUB.subscribe(channel_name)
    #factory = WampClientFactory("ws://localhost:9000", debugWamp=debug)
    factory = ""
    host_name = socket.gethostname()
    if host_name == 'ip-172-31-29-49':
        print "Running WS as oposod.com"
        factory = WampClientFactory("ws://oposod.com:9000", debugWamp=None)
    else:
        print "Running WS as localhost"
        factory = WampClientFactory("ws://localhost:9000", debugWamp=debug)
    factory.protocol = PubSubClient1

    connectWS(factory)

    reactor.run()
