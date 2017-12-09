#!/bin/bash
set -e

if (echo $DATABASE_URI | grep -Eq ^.+\:\/\/.+\:.+\@.+\:[0-9]+\/.*$); then
    # DATABASE_URI is in prot://user:pass@host:port/db format
    HOST=$(echo $DATABASE_URI | cut -d@ -f2 | cut -d/ -f1 | cut -d: -f1)
    PORT=$(echo $DATABASE_URI | cut -d@ -f2 | cut -d/ -f1 | cut -d: -f2)
    TIMEOUT=5

    until /wait-for-it/wait-for-it.sh --host=${HOST} --port=${PORT} --timeout=${TIMEOUT} --quiet; do
        >&2 echo "Connection not available on ${HOST}:${PORT} - waiting ${TIMEOUT} seconds"
    done
    echo "Connection to ${HOST}:${PORT} is available!"
fi

echo "Creating schema..."
python3 ./src/manage.py migrate
echo "Schema created!"

echo "Loading fixtures..."
python3 ./src/manage.py loaddata src/fixtures.json
echo "Fixtures loaded!"

python3 ./src/manage.py runserver 0.0.0.0:8000
