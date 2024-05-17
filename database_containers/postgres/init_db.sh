#!/bin/bash
set -e

# Create databases
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  CREATE DATABASE beta_daa;
  CREATE DATABASE la;
  CREATE DATABASE libage;
EOSQL

# Import SQL dumps
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname beta_daa < /sql-dumps/beta_daa.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname la < /sql-dumps/la.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname libage < /sql-dumps/libage.sql
