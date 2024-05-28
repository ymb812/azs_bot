import logging
import requests
from settings import settings
from core.database.models import Station
from parser.validators import StationData

logger = logging.getLogger(__name__)


class StationsParser:
    @classmethod
    async def azs_parser(cls):
        stations = requests.get(
            url=settings.all_stations_route,
            auth=(settings.api_login, settings.api_password.get_secret_value())
        ).json()

        for station in stations:
            station_data = StationData(**station)
            logger.info(station_data.model_dump_json())
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
                },
            )

            logger.info(f'id={station_data.id} updated')
