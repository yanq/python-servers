import tornado.ioloop
import tornado.web
import tornado.web
from tornado.options import options


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello,Tornado!')


if __name__ == "__main__":
    options.parse_command_line()
    app = tornado.web.Application([tornado.web.url(r"/", MainHandler)], debug=True)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
