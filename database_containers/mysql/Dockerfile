# Use the official MySQL image as the base
FROM mysql:5.7

# Copy the custom initialization script
COPY db-dumps/*.sql /sql-dumps/

# Custom entrypoint script to create databases and import data
COPY init_db.sh /
RUN chmod +x /init_db.sh

# Expose the MySQL port
EXPOSE 3306

