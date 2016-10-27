from aiohttp import web
from test_module import test_module
import asyncio


def setup_route(app):
    app.router.add_get('/recommend/{userKey}/{productKey}', recommend)
    app.router.add_get('/test', test)


def test(rq):
    return web.Response(text = 'size')


@asyncio.coroutine
def recommend(rq):
    userKey =  rq.match_info.get("userKey") or 'x'
    productKey =  rq.match_info.get("productKey") or 'x'

    size = str(test_module(userInfo, productInfo))

    return  web.Response(text= size)