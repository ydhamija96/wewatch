from tornado.options import define, options
import tornado.ioloop
import tornado.web
import redis
import sys
from frontend.uimodules import uimodules
from controllers.home import HomeHandler
from controllers.logout import LogoutHandler
from controllers.video import (
    NewVideoHandler,
    WatchHandler,
    JoinHandler,
    WatchingWSHandler
)


class Application(tornado.web.Application):
    def __init__(self, engine, urls, app_settings):
        self._check_db(engine)
        self.db = engine
        tornado.web.Application.__init__(self, urls, **app_settings)

    def _check_db(self, engine):
        """Checks if a db connection can be made with engine, or prints error and quits."""
        try:
            ret = engine.ping()
            if(not ret):
                raise redis.exceptions.ConnectionError
        except redis.exceptions.ConnectionError:
            sys.exit("Could not make a connection to Redis. Please check if it is running, and check server_options.conf.")


if __name__ == "__main__":
    define("port", default=8888, help="listen on the given port", type=int)
    define("cookie_secret", default="secret", help="used for tornado's secure cookies", type=str)
    define("redis_host", default="localhost", help="redis server host", type=str)
    define("redis_port", default=6379, help="redis port", type=int)
    define("redis_db", default=0, help="redis db", type=int)

    options.parse_config_file("../server_options.conf")

    urls = [
        (r"/", HomeHandler),
        (r"/logout", LogoutHandler),
        (r"/add_video", NewVideoHandler),
        (r"/watch/([0-9]+)", WatchHandler),
        (r"/join/(.+)", JoinHandler),
        (r"/watching_websocket", WatchingWSHandler),
    ]

    app_settings = {
        'cookie_secret': options.cookie_secret,
        'debug': True,
        'ui_modules': uimodules,
        'xsrf_cookies': True,
        'template_path': 'frontend/templates',
        'static_path': 'frontend/static'
    }

    engine = redis.StrictRedis(host=options.redis_host, port=options.redis_port, db=options.redis_db)

    app = Application(engine, urls, app_settings)
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
