#!/usr/bin/env bash
cmd="$@"

function postgres_ready(){
python << END
import os
import sys
import psycopg2
try:
    psycopg2.connect(dbname=os.getenv('POSTGRES_DB'),
                     user=os.getenv('POSTGRES_USER'),
                     password=os.getenv('POSTGRES_PASSWORD'),
                     host=os.getenv('POSTGRES_HOST'),
                     port=os.getenv('POSTGRES_PORT'))
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Waiting PostgreSQL..."
  sleep 1
done

>&2 echo "PostgreSQL is ready!"
exec $cmd
