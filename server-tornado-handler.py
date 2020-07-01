import asyncio
import logging.config
import re
from typing import *

import tornado.ioloop
import tornado.web
from tornado.options import options
from tornado.web import HTTPError

from utils.utils import camel_to_underline

# 要有一个 handler，支持全局拦截器，支持本 handler 拦截，支持 action
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('controller')


def make_controller_name(cls_name: str):
    if cls_name != "Controller" and cls_name.endswith("Controller"):
        cls_name = cls_name.replace('Controller', '')

    return camel_to_underline(cls_name)


class Controller(tornado.web.RequestHandler):
    """控制器，增加拦截器和 action 支持"""
    url_prefix = None
    url_pattern = None
    controller_name = None
    global_before = None  # 全局拦截器，控制权限等。一个函数，参数为控制器实例，明确返回 False 将结束后续处理。

    @classmethod
    def set_url_prefix(cls, prefix):
        """注册控制器的时候调用，也在这个时候初始化一些属性"""
        cls.url_prefix = prefix
        cls.url_pattern = re.compile(rf'{cls.url_prefix}/?$|{cls.url_prefix}/(?P<action>.+)')
        if cls.controller_name is None:
            cls.controller_name = make_controller_name(cls.__name__)

    @classmethod
    def get_url_regex(cls):
        """获取 url 表达式，根据 prefix 做了正则处理"""
        if cls.url_prefix == '/':
            return r'/'
        else:
            return rf'{cls.url_prefix}/?$|{cls.url_prefix}/.+'  # 这里不能有捕获组，否则方法定义的是时候要有参数

    def before(self) -> Optional[Awaitable[None]]:
        """
        拦截器，可以用来处理比较复杂的处理，简单的处理在全局拦截器中定义。
        明确返回 False 将结束处理，否则继续处理
        """
        pass

    async def prepare(self) -> Optional[Awaitable[None]]:
        # 查找 action，设置 action name
        action = None
        self.action_name = None
        m = self.url_pattern.match(self.request.path)
        if m:
            action = m.groupdict().get('action')
            self.action_name = action
        if self.action_name is None:
            self.action_name = self.request.method.lower()

        # 全局拦截器
        result_global = Controller.global_before(self)
        if asyncio.iscoroutine(result_global):
            result_global = await result_global
        if result_global is False:
            logger.info("未通过全局拦截器处理")
            self.finish()
            self._finished = True

        # 控制器拦截器
        result_before = self.before()
        if asyncio.iscoroutine(result_before):
            result_before = await result_before
        if result_before is False:
            logger.info("未通过控制器拦截器处理")
            self.finish()
            self._finished = True

        # 执行 action，如果有的话，并结束处理
        if action:
            logger.info(f"处理 action {action}")
            method = getattr(self, action, None)
            if method:
                result_of_action = method()
                if asyncio.iscoroutine(result_of_action):
                    await result_of_action
                self.finish()
                self._finished = True
            else:
                raise HTTPError(404)


class MainController(Controller):
    """首页"""

    def get(self):
        logger.info("main get action")
        self.write('Hello,Controller!')


class BookController(Controller):
    """书"""

    async def before(self) -> Optional[Awaitable[None]]:
        logger.info("before of book and async")
        return False

    def get(self):
        logger.info("book get")
        self.write("book get")

    def list(self):
        logger.info("book list")
        self.write("book list")


# 保存控制器
__controllers__: List[Controller] = []


# 注册控制器
def register_controller(prefix, controller: Controller):
    controller.set_url_prefix(prefix)
    __controllers__.append(controller)


# 生成 urls 列表，主要用在 application 初始化
def url_handler_list():
    return [(c.get_url_regex(), c) for c in __controllers__]


# 全局拦截器
def before(controller: Controller):
    logger.info(f"Global Before @ {controller.controller_name} {controller.action_name}")


# 应用初始化
Controller.global_before = before
register_controller('/', MainController)
register_controller('/book', BookController)
urls = url_handler_list()

if __name__ == "__main__":
    logger.info("app start")
    options.parse_command_line()
    app = tornado.web.Application(urls, debug=True)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
