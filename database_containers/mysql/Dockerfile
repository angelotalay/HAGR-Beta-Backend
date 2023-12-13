# Use the official MySQL image as the base
FROM mysql:5.7

# Copy the SQL script to the docker-entrypoint-initdb.d directory, 
COPY db-dumps/*.sql /docker-entrypoint-initdb.d/
# Expose the MySQL port
EXPOSE 3306
