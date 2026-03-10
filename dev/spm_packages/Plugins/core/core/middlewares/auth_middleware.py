from slinn import IMiddleware, HttpRedirect, AsyncRequest
from slinn.utils import optional
from orm import PoolProtocol
import functools
import urllib.parse


async def get_user(request: AsyncRequest, fobox_db: PoolProtocol):
    token = request.args.get('token', '') or \
            request.cookies.get('Token', '') or \
            (
                request.headers['Authorization'].removeprefix('Bearer ')
                if 'Authorization' in request.headers.keys() else ''
            )
    if not token:
        return None
    async with await fobox_db.acquire() as conn:
        session = await conn._fobox_active_sessions.find_one({
            'token': token
        })
        if not session:
            return None
        return await conn._fobox_users.find_one({
            'id': session['user_id']
        })


class AuthMiddleware(IMiddleware):
    def __init__(self, fobox_db: PoolProtocol, *, api: bool=False):
        super().__init__()
        self.fobox_db = fobox_db
        self.api = api

    def __call__(self, func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            user = await get_user(kwargs['request'], self.fobox_db)
            if not user:
                if self.api:
                    return 401
                return HttpRedirect(f'/auth?redirect_uri={urllib.parse.quote(kwargs['request'].full_link)}')
            return await optional(func, *args, **(kwargs|{'user': user}))

        return wrapper