from functools import cache
from ipaddress import IPv4Address

from dotenv import find_dotenv
from pydantic import AmqpDsn, PositiveInt, PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    '''DB connection settings'''

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: PositiveInt
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @validator('SQLALCHEMY_DATABASE_URI')
    def assemble_pg_con(cls, current_value: str | None, values: dict[str, str]) -> str:
        if current_value:
            return current_value

        return str(
            PostgresDsn.build(
                scheme='postgresql+asyncpg',
                host=values['POSTGRES_HOST'],
                port=int(values['POSTGRES_PORT']),
                username=values['POSTGRES_USER'],
                password=values['POSTGRES_PASSWORD'],
                path='/' + values['POSTGRES_DB'],
            ),
        )


class GunicornSettings(BaseSettings):
    '''Gunicorn run settings'''

    HOST: IPv4Address = IPv4Address('0.0.0.0')  # noqa: S104
    PORT: PositiveInt = 5000

    GUNICORN_RELOAD: bool = False
    GUNICORN_LOG_LEVEL: str = 'info'
    GUNICORN_LOG_ACCESS: str = '-'
    GUNICORN_LOG_FORMAT: str = (
        '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
    )
    GUNICORN_LOG_ERROR: str = '-'
    GUNICORN_BIND: str | None = None
    GUNICORN_WORKERS: PositiveInt = 1
    GUNICORN_WORKER_CLASS: str = 'uvicorn.workers.UvicornWorker'
    GUNICORN_THREADS: PositiveInt = 1
    GUNICORN_KEEPALIVE: PositiveInt = 120

    @validator('GUNICORN_BIND')
    def validate_bind(cls, current_value: str | None, values: dict[str, str]) -> str:
        if current_value:
            return current_value

        return f'{values["HOST"]}:{values["PORT"]}'


class BaseRedisSettings(BaseSettings):
    '''Redis connection settings'''

    REDIS_HOST: str
    REDIS_PORT: PositiveInt | None = None
    REDIS_USER: str | None = None
    REDIS_PASSWORD: str | None = None


class AmqpSettings(BaseSettings):
    '''AMQP connection settings'''

    AMQP_HOST: str
    AMQP_PORT: PositiveInt | None = None
    AMQP_USER: str | None = None
    AMQP_PASSWORD: str | None = None
    AMQP_URI: AmqpDsn | None = None

    @validator('AMQP_URI')
    def assemble_pub_sub_uri(
        cls,
        current: str | None,
        values: dict[str, str],
    ) -> str:
        if current:
            return current

        return str(
            AmqpDsn.build(
                scheme='amqp',
                host=values['AMQP_HOST'],
                port=int(values['AMQP_PORT']) if values.get('AMQP_PORT') else None,
                username=values.get('AMQP_USER'),
                password=values.get('AMQP_PASSWORD'),
            ),
        )


class CelerySettings(BaseRedisSettings, AmqpSettings):
    CELERY_BROKER_URI: AmqpDsn | None = None

    @validator('CELERY_BROKER_URI')
    def assemble_celery_broker_uri(
        cls,
        current_value: str | None,
        values: dict[str, str],
    ) -> str:
        return current_value if current_value else values['AMQP_URI']

    CELERY_BACKEND_DB: PositiveInt
    CELERY_BACKEND_URI: RedisDsn | None = None

    @validator('CELERY_BACKEND_URI')
    def assemble_celery_backend_uri(
        cls,
        current: str | None,
        values: dict[str, str],
    ) -> str:
        if current:
            return current

        return str(
            RedisDsn.build(
                scheme='redis',
                host=values['REDIS_HOST'],
                port=int(values['REDIS_PORT']) if values.get('REDIS_PORT') else None,
                username=values.get('REDIS_USER'),
                password=values.get('REDIS_PASSWORD'),
                path=(
                    f"/{values['CELERY_BACKEND_DB']}"
                    if 'CELERY_BACKEND_DB' in values
                    else None
                ),
            ),
        )


class AuthSettings(BaseSettings):
    '''TODO'''


class Settings(
    PostgresSettings,
    GunicornSettings,
    CelerySettings,
    AmqpSettings,
    AuthSettings,
):
    '''All app settings'''

    model_config = SettingsConfigDict(
        env_file=find_dotenv(raise_error_if_not_found=False),
        env_file_encoding='utf-8',
        case_sensitive=True,
    )

    PROJECT_NAME: str = 'Boilerplate'
    DESCRIPTION: str = 'Boilerplate description'
    VERSION: str = '0.1.0'
    DEBUG: bool

    ORIGIN_REGEX: str = '.*'


@cache
def get_settings() -> Settings:
    '''Cached Settings factory'''

    return Settings()
