import asyncio
import orm
from sanic import Sanic
from sanic.response import json

app = Sanic()


@app.listener('before_server_start')
async def setup_db(app, loop):
    app.db = await orm.setup()


@app.listener('after_server_stop')
async def close_db(app, loop):
    await app.db.close()


@app.route('/', methods=['POST'])
async def main(req):
    body = req.json
    user = await orm.task(body)
    return json(user)

if __name__ == '__main__':
    app.run(port=8000)
