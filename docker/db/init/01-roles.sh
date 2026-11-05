#!/bin/bash
set -e

# Crear rol de aplicación no privilegiado (Paso D.5)
APP_USER="${APP_DB_USER:-app_user}"
APP_PASS="${APP_DB_PASSWORD:-cambia-esto}"
DB_NAME="${POSTGRES_DB:-criptomed}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$APP_USER') THEN
            CREATE ROLE $APP_USER WITH LOGIN PASSWORD '$APP_PASS' NOSUPERUSER NOCREATEDB NOCREATEROLE;
        ELSE
            ALTER ROLE $APP_USER WITH LOGIN PASSWORD '$APP_PASS' NOSUPERUSER NOCREATEDB NOCREATEROLE;
        END IF;
    END \$\$;
    GRANT CONNECT ON DATABASE $DB_NAME TO $APP_USER;
EOSQL

