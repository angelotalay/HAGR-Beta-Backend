# HAGR Curator #
The beta version of the HAGR Curator and Digital Ageing Atlas Backend is to be refactored and eventually moved to the new server. 

## Prerequisites ##
+ Docker
+ Docker compose
+ Correct .env file.
+ All the SQL dump files that can be retrieved from the beta server or from Angelo. 

## Project Structure ## 
- **app/**: Contains Django related files 
- **database_containers**: Contains database docker files for containers 
- **docker-compose.yaml**: To be run to set up containers using docker compose

## Getting Started - Installation Guide 
- Clone the repository
- Retrieve the SQL files and store them in the appropriate directories. postgresql and mysql dumps should be stored in the path "database_containers/mysql" and "database_containers/postgres" respectively. You may need to alter the SQL filenames to the filenames mentioned in the Dockerfiles. 
- Run the command: ``` docker compose up -d --build  ``` in the directory of the docker-compose.yaml file.
- The SQL files should have been initialised into the database containers. If not you will need to open the terminal and log into the mysql / psql interface using the credentials in the given .env file.

Eg:
```
docker exec -it <container-name> bash
psql -U <username>  
 ```
Then you can restore the files to the database. 

- You should be able to access the curator on "localhost:8000"

## Notes 
A docker compose build has been set up for this project to prevent contributors from having to set up the project locally as it was originally written in Python2 and utilises unmaintained packages that are difficult to install. Once we have converted this codebase into Python3 and an up to date version of Djano there may be no need for docker and docker compose.
  

