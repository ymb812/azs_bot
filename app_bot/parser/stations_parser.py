import logging
import asyncio
from aiohttp import ClientSession, BasicAuth
from settings import settings
from core.database.models import Station, StationProduct
from parser.validators import StationData, ProductData

logger = logging.getLogger(__name__)


class StationsParser:
    @classmethod
    async def azs_parser(cls):
        async with ClientSession() as session:
            try:
                response = await session.get(
                    url=settings.all_stations_route,
                    auth=BasicAuth(settings.api_login, settings.api_password.get_secret_value())
                )
                stations = await response.json()

                tasks = []
                for station in stations:
                    station_data = StationData(**station)
                    task = cls.update_station(station_data)
                    tasks.append(task)

                await asyncio.gather(*tasks)

            except Exception as e:
                logger.error('Failed to fetch or update stations', exc_info=e)


    @staticmethod
    async def update_station(station_data: StationData):
        try:
            await Station.update_or_create(
                id=station_data.id,
                defaults={
                    'name': station_data.name,
                    'number': station_data.number,
                    'region_name': station_data.region_name,
                    'federal_district': station_data.federal_district,
                    'address': station_data.address,
                    'status': station_data.status,
                    'longitude': station_data.longitude,
                    'latitude': station_data.latitude,
                    'updated_at': station_data.updated_at
                }
            )
        except Exception as e:
            logger.error(f'Failed to update station: {station_data}', exc_info=e)

    @classmethod
    async def products_parser(cls, group_of_stations_ids: list[int]):
        async with ClientSession() as session:
            async with session.post(
                    url=settings.prices_route,
                    auth=BasicAuth(settings.api_login, settings.api_password.get_secret_value()),
                    json=group_of_stations_ids,
            ) as response:
                products = await response.json()

                tasks = []
                try:
                    for product in products:
                        product_data = ProductData(**product)
                        task = cls.update_product(product_data)
                        tasks.append(task)

                    await asyncio.gather(*tasks)

                except Exception as e:
                    logger.critical(f'Product info cannot be updated with response: {await response.text()}',
                                    exc_info=e)

    @staticmethod
    async def update_product(product_data: ProductData):
        try:
            await StationProduct.update_or_create(
                station_id=product_data.station_id,
                product_code=product_data.product_code,
                defaults={
                    'product_name': product_data.product_name,
                    'price': product_data.price,
                    'date': product_data.date
                },
            )
        except Exception as e:
            logger.error(f'Failed to update product: {product_data}', exc_info=e)
