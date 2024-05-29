from pydantic import BaseModel, SecretStr, fields
from pydantic_settings import SettingsConfigDict


class BotSettings(BaseModel):
    bot_token: SecretStr = fields.Field(max_length=100, alias='TELEGRAM_BOT_TOKEN')
    payment_token: SecretStr = fields.Field(max_length=100, alias='TELEGRAM_PAYMENT_TOKEN')
    admin_password: SecretStr = fields.Field(max_length=100, alias='ADMIN_PASSWORD')
    admin_chat_id: str = fields.Field(alias='ADMIN_CHAT_ID')
    required_channel_id: str = fields.Field(alias='REQUIRED_CHANNEL_ID')
    welcome_post_id: int = fields.Field(alias='WELCOME_POST_ID')
    welcome_post_id_2: int = fields.Field(alias='WELCOME_POST_ID_2')
    notification_post_id: int = fields.Field(alias='NOTIFICATION_POST_ID')
    registered_post_id: int = fields.Field(alias='REGISTERED_POST_ID')
    user_agreement_post_id: str = fields.Field(alias='USER_AGREEMENT_POST_ID')
    days_post_id: int = fields.Field(alias='DAYS_POST_ID')


class APIParser(BaseModel):
    api_login: str = fields.Field(alias='API_LOGIN')
    api_password: SecretStr = fields.Field(alias='API_PASSWORD')
    all_stations_route: str = fields.Field(alias='ALL_STATIONS_ROUTE')
    prices_route: str = fields.Field(alias='PRICES_ROUTE')


class Broadcaster(BaseModel):
    mailing_batch_size: int = fields.Field(alias='MAILING_BATCH_SIZE', default=25)
    broadcaster_sleep: int = fields.Field(alias='BROADCASTER_SLEEP', default=1)
    stations_parser_hours: int = fields.Field(alias='STATIONS_PARSER_HOURS')
    stations_parser_minutes: int = fields.Field(alias='STATIONS_PARSER_MINUTES')
    products_parser_hours: int = fields.Field(alias='PRODUCTS_PARSER_HOURS')
    products_parser_minutes: int = fields.Field(alias='PRODUCTS_PARSER_MINUTES')


class AppSettings(BaseModel):
    prod_mode: bool = fields.Field(alias='PROD_MODE', default=False)
    excel_file: str = fields.Field(alias='EXCEL_FILE', default='Users stats.xlsx')


class PostgresSettings(BaseModel):
    db_user: str = fields.Field(alias='POSTGRES_USER')
    db_host: str = fields.Field(alias='POSTGRES_HOST')
    db_port: int = fields.Field(alias='POSTGRES_PORT')
    db_pass: SecretStr = fields.Field(alias='POSTGRES_PASSWORD')
    db_name: SecretStr = fields.Field(alias='POSTGRES_DATABASE')


class RedisSettings(BaseModel):
    redis_host: str = fields.Field(alias='REDIS_HOST')
    redis_port: int = fields.Field(alias='REDIS_PORT')
    redis_name: str = fields.Field(alias='REDIS_NAME')


class Settings(
    BotSettings,
    APIParser,
    AppSettings,
    PostgresSettings,
    Broadcaster,
    RedisSettings
):
    model_config = SettingsConfigDict(extra='ignore')
