import uvicorn

from app.api import srv, v1
from app.application import Application
from app.core.settings import get_settings

app = Application(get_settings())
app.register_endpoints(srv, v1)

if __name__ == '__main__':
    uvicorn.run(
        'app.__main__:app',
        host=app.settings.HOST.compressed,
        port=app.settings.PORT,
        reload=app.settings.DEBUG,
    )
