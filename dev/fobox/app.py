from slinn import ApiDispatcher, AsyncRequest, HttpResponse
from orm.postgres import Postgres
import geety
import config


dp = ApiDispatcher('localhost', prefix='fobox')
db = Postgres(
    config.DB_DSN,
    server_settings=config.DB_SETTINGS
)


@dp.get()
async def index(request: AsyncRequest):
    await request.respond(HttpResponse, 'Welcome to Fobox')
    async with await db.acquire() as conn:
        print(await conn.collections())

