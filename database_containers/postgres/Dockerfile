FROM postgres:alpine

# COPY SQL FILES
COPY db-dumps/daa.sql /docker-entrypoint-initdb.d/
COPY db-dumps/beta_daa.sql /docker-entrypoint-initdb.d/
COPY db-dumps/la.sql /docker-entrypoint-initdb.d/
COPY db-dumps/libage.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
