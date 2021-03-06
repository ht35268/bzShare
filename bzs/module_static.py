
import re
import tornado

from . import const
from . import utils

class StaticHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'HEAD']

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, file_path):
        """/static/PATH"""
        file_path = './static/' + file_path
        # In case it does not exist.
        try:
            future = tornado.concurrent.Future()
            def get_file_data_async():
                file_data = utils.get_static_data(file_path)
                future.set_result(file_data)
            tornado.ioloop.IOLoop.instance().add_callback(get_file_data_async)
            file_data = yield future
        except Exception:
            raise tornado.web.HTTPError(404)

        # File actually exists, sending data
        self.set_status(200, "OK")
        self._headers = tornado.httputil.HTTPHeaders()
        self.add_header('Cache-Control', 'max-age=0')
        self.add_header('Connection', 'close')
        self.set_header('Content-Type', utils.guess_mime_type(file_path))
        self.add_header('Content-Length', str(len(file_data)))

        # Push result to client in one blob
        self.write(file_data)
        self.flush()
        self.finish()
        return self

    head=get
    pass
