# Use the official MySQL image as the base
FROM mysql:8.0

# Copy the SQL script to the docker-entrypoint-initdb.d directory, 
COPY db-dumps/hagr_beta_db.sql /docker-entrypoint-initdb.d/
COPY db-dumps/drugage_270923.sql /docker-entrypoint-initdb.d/
# Expose the MySQL port
EXPOSE 3306
