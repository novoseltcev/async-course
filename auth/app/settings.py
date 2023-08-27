from datetime import timedelta
from functools import cache
from ipaddress import IPv4Address
from typing import Any, cast

from dotenv import find_dotenv
from pydantic import (
    HttpUrl,
    KafkaDsn,
    PositiveInt,
    PostgresDsn,
    SecretStr,
    validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(raise_error_if_not_found=False),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',
    )


class PostgresSettings(EnvSettings):
    '''DB connection settings'''

    model_config = SettingsConfigDict(env_prefix='POSTGRES_')

    HOST: str
    USER: str
    PASSWORD: SecretStr
    PORT: PositiveInt
    DB: str
    URI: PostgresDsn | None = None

    @validator('URI')
    def assemble_uri(cls, current_value: str | None, values: dict[str, Any]) -> str:
        if current_value:
            return current_value

        return str(
            PostgresDsn.build(
                scheme='postgresql+asyncpg',
                host=values['HOST'],
                port=values['PORT'],
                username=values['USER'],
                password=cast(SecretStr, values.get('PASSWORD')).get_secret_value(),
                path=values['DB'],
            ),
        )


class KafkaSettings(EnvSettings):
    '''Kafka connection settings'''

    model_config = SettingsConfigDict(env_prefix='KAFKA_')

    HOST: str
    PORT: PositiveInt | None = None
    USER: str | None = None
    PASSWORD: SecretStr | None = None
    URI: KafkaDsn | None = None

    @validator('URI')
    def assemble_uri(
        cls,
        current: str | None,
        values: dict[str, Any],
    ) -> str:
        if current:
            return current

        result = values['HOST']
        if values.get('PORT'):
            result += ':' + str(values['PORT'])
        
        return result


class SchemeRegistrySettings(EnvSettings):
    '''Kafka scheme registry connection settings'''

    model_config = SettingsConfigDict(env_prefix='SCHEME_REGISTRY_')

    HOST: str
    PORT: int = 8081
    URI: HttpUrl | None = None

    @validator('URI')
    def assemble_schema_registry_uri(
        cls,
        current: str | None,
        values: dict[str, str],
    ) -> str:
        if current:
            return current

        return str(
            HttpUrl.build(
                scheme='http',
                host=values['HOST'],
                port=int(values['PORT']),
            ),
        )


class JWTSettings(EnvSettings):
    model_config = SettingsConfigDict(env_prefix='JWT_')

    LIFETIME: timedelta = timedelta(days=30)
    SECRET: str


class AuthSettings(EnvSettings):
    model_config = SettingsConfigDict(env_prefix='AUTH_')

    ID: str
    SECRET: str
    TOKEN_URL: HttpUrl = HttpUrl('http://localhost:5555/srv/token')
    VERIFY_URL: HttpUrl = HttpUrl('http://localhost:5555/srv/verify')


class Settings(EnvSettings):
    '''All app settings'''

    PROJECT_NAME: str = 'SSO Service'
    DESCRIPTION: str = 'PopugINC SSO'
    VERSION: str = '0.1.0'

    ORIGIN_REGEX: str = '.*'

    HOST: IPv4Address = IPv4Address('0.0.0.0')  # noqa: S104
    PORT: PositiveInt
    DEBUG: bool

    auth: AuthSettings = AuthSettings()
    jwt: JWTSettings = JWTSettings()
    db: PostgresSettings = PostgresSettings()
    kafka: KafkaSettings = KafkaSettings()
    scheme_registry: SchemeRegistrySettings = SchemeRegistrySettings()


@cache
def get_settings() -> Settings:
    '''Cached Settings factory'''

    return Settings()
