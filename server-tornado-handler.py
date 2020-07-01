import asyncio
import logging.config
import re
from typing import *

import tornado.ioloop
import tornado.web
from tornado.options import options
from tornado.web import Finish

from utils.utils import camel_to_underline

# 要有一个 handler，支持全局拦截器，支持本 handler 拦截，支持 action
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('controller')


def make_controller_name(cls_name: str):
    if cls_name != "Controller" and cls_name.endswith("Controller"):
        cls_name = cls_name.replace('Controller', '')

    return camel_to_underline(cls_name)


class Controller(tornado.web.RequestHandler):
    url_prefix = None
    __url_pattern__ = None
    controller_name = None
    action_name = None

    @classmethod
    def global_before(cls):
        pass

    @classmethod
    def set_url_prefix(cls, prefix):
        cls.url_prefix = prefix
        cls.__url_pattern__ = re.compile(cls.get_url_regex())
        if cls.controller_name is None:
            cls.controller_name = make_controller_name(cls.__name__)

    @classmethod
    def get_url_regex(cls):
        if cls.url_prefix == '/':
            return r'/'
        else:
            return rf'{cls.url_prefix}/?$|{cls.url_prefix}/(?P<action>.+)'

    def before(self):
        """
        拦截器，可以用来处理比较复杂的处理，简单的处理在全局拦截器中定义。
        明确返回 False 将结束处理，否则继续处理
        """
        logger.info("local before")

    async def prepare(self) -> Optional[Awaitable[None]]:
        action = None
        m = self.__url_pattern__.match(self.request.path)
        if (m):
            action = m.group('action')
            self.action_name = action
        if self.action_name is None:
            self.action_name = self.request.method.lower()

        # 全局拦截器
        result_global = Controller.global_before()
        if asyncio.iscoroutine(result_global):
            result_global = await result_global
        if result_global is False:
            logger.info("未通过全局拦截器处理")
            raise Finish()

        result_before = self.before()
        if asyncio.iscoroutine(result_before):
            result_before = await result_before
        if result_before is False:
            logger.info("未通过控制器拦截器处理")
            raise Finish()

        if action:
            logger.info(f"处理 action {action}")
            raise Finish()


class MainController(Controller):
    def get(self):
        logger.info("main get action")
        self.write('Hello,Controller!')


class BookController(Controller):
    def get(self):
        logger.info("book get")
        self.write("book get")

    def list(self):
        logger.info("book list")
        self.write("book list")


__controllers__: List[Controller] = []


def register_controller(prefix, controller: Controller):
    controller.set_url_prefix(prefix)
    __controllers__.append(controller)


def url_handler_list():
    return [(c.get_url_regex(), c) for c in __controllers__]


register_controller('/', MainController)
register_controller('/book', BookController)

urls = url_handler_list()

if __name__ == "__main__":
    logger.info("app start")
    options.parse_command_line()
    app = tornado.web.Application(urls, debug=True)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
