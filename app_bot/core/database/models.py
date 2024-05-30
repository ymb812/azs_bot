import logging
import pytz
from datetime import datetime
from tortoise import fields
from tortoise.models import Model

logger = logging.getLogger(__name__)


class User(Model):
    class Meta:
        table = 'users'
        ordering = ['created_at']

    user_id = fields.BigIntField(pk=True, index=True)
    username = fields.CharField(max_length=32, index=True, null=True)
    is_registered = fields.BooleanField(default=False)
    fio = fields.CharField(max_length=64, null=True)
    phone = fields.CharField(max_length=16, null=True)
    status = fields.CharField(max_length=32, null=True)  # admin
    payment_amount = fields.FloatField(default=0)
    refills_amount = fields.IntField(default=0)

    created_at = fields.DatetimeField(auto_now_add=True)
    last_activity = fields.DatetimeField(auto_now=True)

    @classmethod
    async def update_data(cls, user_id: int, username: str):
        user = await cls.filter(user_id=user_id).first()
        tz = pytz.timezone('Europe/Moscow')
        if user is None:
            user = await cls.create(
                user_id=user_id,
                username=username,
                last_activity=tz.localize(datetime.now()),
            )
        else:
            await cls.filter(user_id=user_id).update(
                username=username,
            )

        return user


class FavouriteStation(Model):
    class Meta:
        table = 'favourite_stations'

    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField('models.User', to_field='user_id')
    station = fields.ForeignKeyField('models.Station', to_field='id')


class Station(Model):
    class Meta:
        table = 'stations'

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=128, null=True)
    number = fields.CharField(max_length=64, null=True)
    region_name = fields.CharField(max_length=128, null=True)
    federal_district = fields.CharField(max_length=128, null=True)
    address = fields.CharField(max_length=256, null=True)
    status = fields.CharField(max_length=64, null=True)
    longitude = fields.CharField(max_length=32, null=True)
    latitude = fields.CharField(max_length=32, null=True)
    updated_at = fields.DatetimeField(null=True)


class Product(Model):
    class Meta:
        table = 'products'

    id = fields.BigIntField(pk=True)
    station = fields.ForeignKeyField('models.Station', to_field='id', related_name='station_product')
    code = fields.CharField(max_length=32, null=True)
    name = fields.CharField(max_length=32, null=True)
    price = fields.FloatField(null=True)
    date = fields.DatetimeField(null=True)


class Order(Model):
    class Meta:
        table = 'orders'

    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField('models.User', to_field='user_id')
    station = fields.ForeignKeyField('models.Station', to_field='id')
    product = fields.ForeignKeyField('models.Product', to_field='id')
    amount = fields.FloatField()
    total_price = fields.FloatField()
    is_paid = fields.BooleanField(default=False)  # auto or via manager

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class SupportRequest(Model):
    class Meta:
        table = 'support_requests'

    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField('models.User', to_field='user_id')
    text = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)


class Dispatcher(Model):
    class Meta:
        table = 'mailings'
        ordering = ['send_at']

    id = fields.BigIntField(pk=True)
    post = fields.ForeignKeyField('models.Post', to_field='id')
    is_registered_meditation = fields.BooleanField(default=False)
    is_registered_days = fields.BooleanField(default=False)
    is_for_all_users = fields.BooleanField(default=False)
    user = fields.ForeignKeyField('models.User', to_field='user_id', null=True)
    send_at = fields.DatetimeField()


class Post(Model):
    class Meta:
        table = 'static_content'

    id = fields.BigIntField(pk=True)
    text = fields.TextField(null=True)
    photo_file_id = fields.CharField(max_length=256, null=True)
    video_file_id = fields.CharField(max_length=256, null=True)
    video_note_id = fields.CharField(max_length=256, null=True)
    document_file_id = fields.CharField(max_length=256, null=True)
    sticker_file_id = fields.CharField(max_length=256, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


    @classmethod
    async def get_posts_by_scenario(cls, scenario_id: int):
        return await cls.filter(id=scenario_id).all()


class MailingLog(Model):
    class Meta:
        table = 'mailings_logs'

    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField('models.User', to_field='user_id')
    is_sent = fields.BooleanField()
    created_at = fields.DatetimeField(auto_now_add=True)


class Settings(Model):
    class Meta:
        table = 'settings'

    id = fields.BigIntField(pk=True)
    card_data = fields.CharField(max_length=128)
    discount_percent = fields.FloatField(default=0)
