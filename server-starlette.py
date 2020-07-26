import uvicorn as uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route


async def homepage(request):
    return PlainTextResponse('Hello，Starlette   ！')


app = Starlette(debug=True, routes=[Route('/', homepage), ])

# uvicorn "server-starletter:app"  --reload  # log 信息有着色
# uvicorn "server-starletter:app"  --reload --log-config=logging.conf --log-level=debug  #这样反而不打印最开始的信息了
if __name__ == "__main__":
    # uvicorn.run("server-starlette:app",reload=True)  # 这样就可以重载了
    uvicorn.run(app)
