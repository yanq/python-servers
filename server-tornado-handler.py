import re
from typing import *

import tornado.ioloop
import tornado.web
import tornado.web
from tornado import httputil
from tornado.options import options


# 要有一个 handler，支持全局拦截器，支持本 handler 拦截，支持 action


class Controller(tornado.web.RequestHandler):
    url_prefix = ''
    controller_name = ''
    action_name = ''
    __url_pattern__ = None

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        self.controller_name = self.__class__.__name__.lower()
        self.__url_pattern__ = re.compile(self.get_url_regex())
        super().__init__(application, request, **kwargs)

    # def before(self):
    #     """
    #     拦截器，可以用来处理比较复杂的处理，简单的处理在全局拦截器中定义。
    #     明确返回 False 将结束处理，否则继续处理
    #     """
    #     pass
    #
    # async def prepare(self) -> Optional[Awaitable[None]]:
    #     self.action_name = self.__url_pattern__.match(self.request.path).group('action')
    #     if self.action_name is None:
    #         self.action_name = self.request.method.lower()
    #
    #     # 全局拦截器
    #     global_interceptor = self.application.before
    #     if global_interceptor:
    #         result = global_interceptor()
    #     if asyncio.iscoroutine(result):
    #         result = await result
    #     if result is False:
    #         self.finish()
    #         return
    #
    #     if self.before():
    #         self.finish()
    #
    @classmethod
    def get_url_regex(cls):
        return rf'{cls.url_prefix}/?$|{cls.controller_name}/(?P<action>.*)'


# __controllers__: List[Controller] = []
#
#
# def register_controller(prefix, controller: Controller):
#     controller.url_prefix = prefix
#     __controllers__.append(controller)
#
#
# def url_handler_list():
#     return [(c.get_url_regex(), c) for c in __controllers__]
#

class MainHandler(Controller):
    def get(self):
        self.write('Hello,Controller!')


# register_controller('/', MainHandler)
# urls = url_handler_list()

if __name__ == "__main__":
    options.parse_command_line()
    app = tornado.web.Application([(r'/', MainHandler)], debug=True)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
