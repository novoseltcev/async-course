import uvicorn

from app import api
from app.application import Application
from app.consumer import start_consumer
from app.settings import get_settings

app = Application(get_settings(), [start_consumer])
app.register_endpoints(api)

if __name__ == '__main__':
    uvicorn.run(
        'app.__main__:app',
        host=app.settings.HOST.compressed,
        port=app.settings.PORT,
        reload=app.settings.DEBUG,
    )
