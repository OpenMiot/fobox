from slinn import ApiDispatcher, AsyncRequest, HttpResponse

dp = ApiDispatcher()

# Write your code down here
@dp.get()
async def index(request: AsyncRequest):
    await request.respond(HttpResponse, 'Hello, World!')
