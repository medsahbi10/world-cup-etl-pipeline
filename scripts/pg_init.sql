/*
==================================================================================
CREATE USER AND SCHEMA - WORLD CUP PROJECT
==================================================================================

Runs automatically when the Postgres container starts (via the
/docker-entrypoint-initdb.d mount in docker-compose.yml).

The database itself (`$POSTGRES_DB`) is created by the Postgres image's entrypoint
using the POSTGRES_DB environment variable, so we don't create it here.
*/

-- Create application user (idempotent — DO block guards on existence)
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dev_user') THEN
        CREATE ROLE dev_user LOGIN PASSWORD 'dev123';
    END IF;
END
$$;

-- Schema for raw layer (Bronze)
CREATE SCHEMA IF NOT EXISTS wc_raw AUTHORIZATION dev_user;

-- Grant privileges on the current database (the one Postgres connected to via POSTGRES_DB)
GRANT ALL PRIVILEGES ON SCHEMA wc_raw TO dev_user;
