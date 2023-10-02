FROM postgres:alpine

# COPY SQL FILES
COPY db-dumps/beta_daa.dump /docker-entrypoint-initdb.d/
COPY db-dumps/libage.tar /docker-entrypoint-initdb.d/

EXPOSE 5432
