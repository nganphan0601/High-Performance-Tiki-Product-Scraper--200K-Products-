import aiohttp, asyncio

api_url = "https://api.tiki.vn/product-detail/api/v1/products/{}"
product_id = 1391347  # Example product ID

async def test_request():
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url.format(product_id)) as response:
            print(response.status)
            print(await response.text())

asyncio.run(test_request())