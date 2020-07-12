import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('controller')

import asyncio
import typing

import uvicorn as uvicorn
from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response, JSONResponse
from starlette.routing import Route
from starlette.types import Scope, Receive, Send

from utils.utils import camel_to_underline


def make_controller_name(cls_name: str):
    """转换控制器名称"""
    if cls_name != "Controller" and cls_name.endswith("Controller"):
        cls_name = cls_name.replace('Controller', '')

    return camel_to_underline(cls_name)


class Controller:
    """控制器，支持拦截器和 action"""
    controller_name = None
    global_before = None  # 全局拦截器，控制权限等

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert scope["type"] == "http"
        self.scope = scope
        self.receive = receive
        self.send = send
        self.controller_name = make_controller_name(self.__class__.__name__)
        self.action_name = None

    def __await__(self) -> typing.Generator:
        return self.dispatch().__await__()

    async def dispatch(self) -> None:
        """处理请求"""
        request = Request(self.scope, receive=self.receive)

        # action
        self.action_name = request.path_params.get('action')
        status_code = 404
        if self.action_name is None:
            self.action_name = request.method.lower()
            status_code = 405
        handler = getattr(self, self.action_name, None)
        if handler is None:
            raise HTTPException(status_code=status_code)

        # 全局拦截器
        if Controller.before:
            result_before = Controller.before(request)
            if asyncio.iscoroutine(result_before):
                result_before = await result_before
            if result_before not in [True, None]:
                await self.handler_result(result_before)
                return

        # 拦截器
        result_before = self.before(request)
        if asyncio.iscoroutine(result_before):
            result_before = await result_before
        if result_before not in [True, None]:
            await self.handler_result(result_before)
            return

        is_async = asyncio.iscoroutinefunction(handler)
        if is_async:
            response = await handler(request)
        else:
            response = await run_in_threadpool(handler, request)
        await self.handler_result(response)

    async def handler_result(self, result):
        """处理 result"""
        if isinstance(result, Response):
            response = result
        elif isinstance(result, dict):
            response = JSONResponse(result)
        else:
            response = PlainTextResponse(result or 'False')

        await response(self.scope, self.receive, self.send)

    def before(self):
        """拦截器，返回 None，True 表示通过，不通过返回响应的内容。"""
        pass

    @classmethod
    def routes(cls, path: str):
        """mount 路由"""
        if path == '/':
            return [Route('/', cls)]
        return [Route(path, cls), Route(path + '/{action}', cls)]


class Home(Controller):
    def before(self, request):
        pass

    def get(self, request):
        return PlainTextResponse('Hello，Starlette ！')

    async def hi(self, request):
        return f'{request.path_params.get("action")},Starlette! @ {self.controller_name}-{self.action_name}'


app = Starlette(debug=True, routes=[*Home.routes('/a')])

if __name__ == "__main__":
    uvicorn.run(app, debug=True, log_level="debug")
