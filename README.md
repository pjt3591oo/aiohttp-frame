
# aiohttp Framework 뼈대
- python에서는 다양한 서버프레임 워크가 존재한다.
- aiohttp는 가벼우면서 빠르게 짤 수 있다.
- node.js의 express framework처럼 기본 구조를 잡아주는 것을 찾지 못하여 기본 뼈대를 만들었다.


## 서버를 시작하기 앞서 설치해야할 모듈
- aiohttp라는 프레임워크를 사용할거이기 때문에 `aiohttp`라는 모듈을 설치를 해준다.
- 또한 `ayncio` 모듈도 설치를 해준다.
- 로그를 찍기 위해 `logging` 모듈도 설치해준다.
- DB 모듈은 개인 성향에 맞추어서 설치를 해준다.
(orm을 쓸경우 `sqlalchemy`가 대표적이고 row query를 쓴다면 `pymysql`이나 `MySQLdb`가 대표적이다.)


### 모듈설치
#### Windows or Linux
```
pip install aiohttp # pip3 install aiohttp
```
```
pip install asyncio # pip3 install aiohttp
```


### 서버시작
```
python app.py
```
해당 소스코드를 그대로 실행을 할 경우 8282포트로 설정이 되어있다. port는 app.py에서 **__init__** 함수내부의 `host`와 `port`를 수정을 해주면 된다. 수정 해주면 된다.


### app.py의 init함수

```.py
def __init__(loop):

    app = web.Application(loop=loop)

    host = "0.0.0.0"
    port = 8282

    setup_route(app) # 라우팅 설정
    setup_middlewares(app) # 비들웨어 설정

    return app, host, port # app, host, port 반환
```

host를 0.0.0.0으로 하여 모든 IP로부터 접속을 허용을 해준다.


### 라우팅 설정 `routes.py`

- 각 요청에 따른 처리를 만들어 준다.

```.py
def setup_route(app):
    app.router.add_get('/recommend/{userKey}/{productKey}', recommend)
    app.router.add_get('/test', test)
```
- 해당 url의 자리를 {}감싼 변수 명으로 받는다.(`rq.match_info.get("userKey")`)
- 해당 함수를 app에서 호출을 해주면 된다.


### 실제 로직이 처리되는 부분

- 각 요청에 맞추어서 아래처럼 작성을 해주면 된다.
- 각 API마다 등록을 시켜준다.

```.py
@asyncio.coroutine
def recommend(request):
    userKey =  request.match_info.get("userKey") or 'x'
    productKey =  request.match_info.get("productKey") or 'x'

    size = str(test_module(userInfo, productInfo))

    return  web.Response(text= size)
```
해당 함수는 실제 서버 로직이 실행되는 부분이다. 라우팅에서 설정해준 패스로 접속할 떄 해당 로직을 호출을 한다.

> 개인 성향에 따라서 실제 로직이 처리되는 부분과 라우팅을 나눠도 되고 안나눠도 된다. 또한 API가 늘어날수록 API 종류에 따라서 routes파일을 나누는게 좋다.
node.js에서는 디렉토리를 모듈로 가져오면 해당 디렉토리내의 index.js를 자동으로 가져오는데 python에서는 이점이 조금 다르다.

### 미들웨어 처리

- 미들웨어란 실제 로직부분이 아닌 로직이 처리된기 전, 후의 공통적으로 처리가 된느 부분을 말한다.
- 해당 프레임에서는 404, 500, 200가 됬을때 로그를 남기는 기능만 구현을 하였다.

 ```.py
 #잘못요청
 async def handle_404(request, response):
     user = request.match_info.get("userKey") or 'x'
     product = request.match_info.get("productKey") or 'x'

     error_log(user, product, "404")

     raise web.HTTPNotFound()
 ```

 ```.py
 async def handle_500(request, response):
     user = request.match_info.get("userKey") or 'x'
     product = request.match_info.get("productKey") or 'x'

     critical_log(user,product,"500")

     return response
 ```

 ```.py
 #성공적으로 처리
 async def handle_200(request, response):
     user = request.match_info.get("userKey") or 'x'
     product = request.match_info.get("productKey") or 'x'
     recommend = response.text or 'x'

     success_log(user, product, recommend)

     return response
 ```

- 각각 응답 코드에 따른 후 처리를 만들었다.
- 이제 이것을 app.middlewares에 등록을 시켜준다.

### 미들웨어등록

```.py
def error_pages(overrides):
    async def middleware(app, handler):
        async def middleware_handler(request):
            try:
                response = await handler(request)
                override = overrides.get(response.status)
                if override is None:
                    return response
                else:
                    return await override(request, response)
            except web.HTTPException as ex:
                override = overrides.get(ex.status)
                if override is None:
                    raise
                else:
                    return await override(request, ex)
        return middleware_handler
    return middleware


def setup_middlewares(app):
    error_middleware = error_pages({404: handle_404,
                                    500: handle_500,
                                    200: handle_200
                                    })
    app.middlewares.append(error_middleware)
```

error_pages에 응답코드를 키값으로 해당 함수를 매핑을 시켜서 인자로 넘겨준다.
app.middlewares에 error_pages의 받환값을 넣어준다.
app파일에서 setup_middlewares에 app인자를 넘겨주어서 호출을 해준다.

### app.py
- 미들웨어, 라우팅을 app에서 설정을 해준다.
- 해당 모듈들을 불러와서 호출해주기만 해면 된다. web.Application(loop=loop)을 인자로 넘겨준다.

```.py
import asyncio
import logging

from aiohttp import web
from routes import setup_route as setup_route
from middleware import setup_middlewares


def __init__(loop):

    app = web.Application(loop=loop)

    host = "localhost"
    port = 8282

    setup_route(app)
    setup_middlewares(app)

    return app, host, port


def main():
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app, host, port = __init__(loop)

    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    print('server on')
    main()
```