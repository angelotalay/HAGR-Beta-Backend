FROM postgres:10.23-alpine

# Copy initialization script and SQL dumps
COPY init_db.sh /docker-entrypoint-initdb.d/
COPY db-dumps/ /sql-dumps/

# Make the script executable
RUN chmod +x /docker-entrypoint-initdb.d/init_db.sh

EXPOSE 5432