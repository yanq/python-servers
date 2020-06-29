import tornado.ioloop
import tornado.web
import tornado.web
from tornado.options import options


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<a href="%s">link to story X</a>' % self.reverse_url("story", "1"))


class StoryHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, story_id):
        self.write("this is story %s" % story_id)


if __name__ == "__main__":
    options.parse_command_line()
    app = tornado.web.Application([
        tornado.web.url(r"/", MainHandler),
        tornado.web.url(r"/story/?$|/story/([0-9]+)", StoryHandler, dict(db='mongo-x'), name="story")
    ], debug=True)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
