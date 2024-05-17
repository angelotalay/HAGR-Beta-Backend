#!/bin/bash
set -e

# Define the databases to be created
DATABASES=("dev_orthologs" "dev_genage_human" "dev_genage_models" "dev_anage" "dev_gendr" "dev_longevity" "dev_drug_age" "dev_cell_age")

# Grant all privileges to the user
echo "Granting privileges to the user"
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}' WITH GRANT OPTION; FLUSH PRIVILEGES;"


# Loop through and create each database
for DB in "${DATABASES[@]}"; do
  echo "Creating database: $DB"
  mysql -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" -e "CREATE DATABASE IF NOT EXISTS $DB;"
done

# Import SQL files into the corresponding databases
for DB in "${DATABASES[@]}"; do
  SQL_FILE="/sql-dumps/$DB.sql"
  if [ -f "$SQL_FILE" ]; then
    echo "Importing $SQL_FILE into $DB"
    mysql -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "$DB" < "$SQL_FILE"
  else
    echo "No SQL file found for $DB"
  fi
done
