from slinn import ApiDispatcher, AsyncRequest, HttpResponse, Storage, HttpRedirect, HttpRender, IMiddleware, HttpJSONResponse, ProjectAPI
from slinn.utils import optional
from . import app
from .db_init import gapp, fobox_db
from core.middlewares import AuthMiddleware
import functools
import json
import urllib.parse
import geety as G


dp = ApiDispatcher('localhost', prefix='fobox')
views = Storage('views', package=__package__)
components = Storage('Components', package=__package__)
palletes = Storage('Palletes')
site_app = Storage('app')


class AdminOnly(IMiddleware):
    def __init__(self):
        super().__init__()

    def __call__(self, func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if 'user' not in kwargs:
                return 401
            if kwargs['user'].role != 2:
                return 404
            return await optional(func, *args, **kwargs)

        return wrapper


def reload_components():
    gapp.components = {}
    for component_file in components.listdir('.'):
        if components.isfile(component_file):
            with components(component_file, 'r') as component:
                gapp.load(component)


@dp.get()
@AuthMiddleware(fobox_db)
@AdminOnly()
async def index(request: AsyncRequest, user: dict):
    reload_components()
    with views('index.view.xml', 'r', 'utf-8') as view:
        page = gapp.new_page(view)
        page.set_entry_point('View')
        await request.respond(HttpResponse, await page.html(context={
            'USER': user
        }), content_type='text/html; charset=utf-8')

@dp.get('editor')
@AuthMiddleware(fobox_db)
@AdminOnly()
async def editor(request: AsyncRequest, user: dict):
    reload_components()
    with views('editor.view.xml', 'r', 'utf-8') as view:
        page = gapp.new_page(view)
        page.set_entry_point('View')
        await request.respond(HttpResponse, await page.html(context={
            'COMPONENTS': [
                {
                    'name': key
                } for key in gapp.components
            ],
            'USER': user
        }), content_type='text/html; charset=utf-8')

@dp.get('palletes')
@AuthMiddleware(fobox_db, api=True)
@AdminOnly()
async def get_palletes(request: AsyncRequest, user: dict):
    if not palletes.isfile('palletes.json'):
        with palletes('palletes.json', 'w') as f:
            json.dump({
                'palletes': []
            }, f, ensure_ascii=False, indent=4)
    await request.respond(HttpRender, 'palletes.json', storage=palletes)

@dp.get('palletes/<str path>')
@AuthMiddleware(fobox_db, api=True)
@AdminOnly()
async def get_pallete(request: AsyncRequest, user: dict, path: str):
    if not palletes.isdir(path):
        return 404
    result = {
        'components': []
    }
    for component in palletes.listdir(path):
        with palletes(path + '/' + component, 'r') as f:
            #component = G.xml_parser.parse_component(f)
            #print(component)
            component = f.read()
            component = ''.join([line.strip()+'\n' for line in component.split('\n')])
            result['components'].append(component)
    await request.respond(HttpJSONResponse, **result)

@dp.post('saveView')
@AuthMiddleware(fobox_db, api=True)
@AdminOnly()
async def save_view(request: AsyncRequest, user: dict):
    xml = await request.body.get()
    with site_app('views/test.view.xml', 'wb') as f:
        f.write(xml)
    await request.respond(HttpJSONResponse, status='ok')

@dp.get('loadView')
@AuthMiddleware(fobox_db, api=True)
@AdminOnly()
async def load_view(request: AsyncRequest, user: dict):
    if site_app.isfile('views/test.view.xml'):
        await request.respond(HttpRender, 'views/test.view.xml', storage=site_app)
    else:
        return 404

@dp.get('ping')
async def ping(request: AsyncRequest):
    async with await fobox_db.acquire() as conn:
        await conn.collections()
    await request.respond(HttpResponse, 'pong')


dp  .static('/styles/root.css', HttpRender, 'styles/root.css', storage=views)\
    .static('/scripts/editor/canvas.js', HttpRender, 'scripts/editor/canvas.js', storage=views)\
    .static('/scripts/editor/component.js', HttpRender, 'scripts/editor/component.js', storage=views)\
    .static('/scripts/editor/contextmenu.js', HttpRender, 'scripts/editor/contextmenu.js', storage=views)\
    .static('/scripts/editor/misc.js', HttpRender, 'scripts/editor/misc.js', storage=views)\
    .static('/scripts/editor/pallete.js', HttpRender, 'scripts/editor/pallete.js', storage=views)\
    .static('/scripts/editor/parser.js', HttpRender, 'scripts/editor/parser.js', storage=views)\
    .static('/scripts/editor/properties.js', HttpRender, 'scripts/editor/properties.js', storage=views)\
    .static('/scripts/editor/property.js', HttpRender, 'scripts/editor/property.js', storage=views)\
    .static('/scripts/editor/trash.js', HttpRender, 'scripts/editor/trash.js', storage=views)\
    .static('/styles/editor/canvas.css', HttpRender, 'styles/editor/canvas.css', storage=views)\
    .static('/styles/editor/component.css', HttpRender, 'styles/editor/component.css', storage=views)\
    .static('/styles/editor/contextmenu.css', HttpRender, 'styles/editor/contextmenu.css', storage=views)\
    .static('/styles/editor/pallete.css', HttpRender, 'styles/editor/pallete.css', storage=views)\
    .static('/styles/editor/properties.css', HttpRender, 'styles/editor/properties.css', storage=views)\
    .static('/styles/editor/root.css', HttpRender, 'styles/editor/root.css', storage=views)\
    .static('/styles/editor/trash.css', HttpRender, 'styles/editor/trash.css', storage=views)\
    .static('/scripts/editor.js', HttpRender, 'scripts/editor.js', storage=views)
