from confluent_kafka import Producer

from app.settings import get_settings


def get_producer() -> Producer:
    return Producer({'bootstrap.servers': get_settings().kafka.URI})
