#!/bin/sh

set -e

# Activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

# Run migrations
while ! alembic upgrade head
do
     echo "Retry migrate..."
     sleep 1
done

exec "$@"