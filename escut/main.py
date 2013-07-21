
import tornado.ioloop
import tornado.web
from tornado.options import define, options
from tornado.httpserver import HTTPServer

import functools
import logging
import signal
import time

from escut.lock_handler import LockHandler
from lock import LockManager

import redis

define("port", default=9595, help="run on the given port", type=int)
define("redis_host", default="127.0.0.1", help="redis host")
define("redis_port", default=6379, help="redis port", type=int)
define("redis_db", default="0", help="redis db")


def log_is_ready():
    logging.info("escut daemon is ready !")


def sigterm_handler(server, loop, signum, frame):
    logging.info("SIGTERM signal catched => scheduling webserver stop...")
    loop.add_callback(functools.partial(stop_server, server, loop))


def stop_server(server, loop):
    logging.info("Stopping webserver...")
    server.stop()
    if loop:
        logging.info("Webserver stopped => scheduling main loop stop...")
        loop.add_timeout(time.time() + 5, functools.partial(stop_loop, loop))
    else:
        logging.info("Webserver stopped !")


def stop_loop(loop):
    logging.info("Stopping main loop...")
    loop.stop()
    logging.info("Main loop stopped !")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
             (r"/lock", LockHandler)
        ]
        settings = dict()
        tornado.web.Application.__init__(self, handlers, **settings)

        self.redis = redis.StrictRedis(
            host=options.redis_db,
            port=options.redis_port,
            db=options.redis_db)

        self.lock_manager = LockManager(self.redis)


def main():
    tornado.options.parse_command_line()

    server = HTTPServer(Application())
    server.listen(options.port)

    iol = tornado.ioloop.IOLoop.instance()
    iol.add_callback(log_is_ready)

    signal.signal(signal.SIGTERM, lambda s, f: sigterm_handler(server, iol, s, f))
    try:
        iol.start()
    except KeyboardInterrupt:
        stop_server(server, None)
    logging.info("escut daemon is stopped !")


if __name__ == '__main__':
    main()
