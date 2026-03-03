import asyncio
import sys

sys.path.append('c:\\Users\\Lenovo\\OneDrive\\Documents\\GitHub\\NeuroNav\\backend')

from models import RouteRequest, Coordinate, SensoryProfile
from main import get_route

async def main():
    req = RouteRequest(
        origin=Coordinate(lat=1.3048, lng=103.8318),
        destination=Coordinate(lat=1.2834, lng=103.8607),
        mode='foot',
        profile=SensoryProfile()
    )
    try:
        response = await get_route(req)
        print(f'Successfully returned Response with {len(response.routes)} routes')
        print(f'Cat 1: {response.routes[0].category}')
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
