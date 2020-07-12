import uvicorn as uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route


async def homepage(request):
    return PlainTextResponse('Hello，Starlette！')


app = Starlette(debug=True, routes=[Route('/', homepage), ])

if __name__ == "__main__":
    uvicorn.run(app)
