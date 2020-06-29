import tornado.ioloop
import tornado.web
from tornado.options import options


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie('name'):
            self.set_secure_cookie('name', 'yan')
        self.write("Hello Tornado !")


if __name__ == "__main__":
    options.parse_command_line()
    app = tornado.web.Application([(r"/", MainHandler), ], debug=True, cookie_secret="ANBHLLJKJIOLKJLKJLKJHGIU(OJBG")
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
