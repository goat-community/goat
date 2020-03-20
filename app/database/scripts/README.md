# Database readme
## How to run custom_pois
### 1.Copy geojson files in the next folder
### 2.Check and update name lookup conditions
Go to the goat config.yaml folder located in the path:
```
\app\config\goat_config.yaml
```
Look the line: "pois_sear_conditions"
Each line is an amenity brand, create one new line for each custom_pois to be updated, delete those that you do not need. 
### 3.Install geojson module
Run in console
```
docker exec -it goat-database pip3 install geojson
```
### 4.To run the custom pois compilation
Run in console to standarize the custom_pois database
```
docker exec -it goat-database python3 /opt/scripts/db_functions.py
```
### 5.Run de SQL script
