#!/bin/sh
#####################################################################
#	Custom script to install Geoserver as a Docker image			#
#	and running it in a container.									#
# Main Docker image taken from:										#
# https://github.com/terrestris/docker-geoserver					#
#																	#
#	Args:															#
#		- $1 - Specify the location of needed geoserver catalog dir #
#																	#
#	Credits: fernando.ribeiro@geocrafter.eu							#
#####################################################################

# Specify container name
CONTAINER_NAME=geoserver

# Initial checks


display_usage() { 
	echo "This script must be run with super-user privileges."  
} 



if [[ "$EUID" -ne 0 ]]; 
	then 
		echo "This script must be run as root!" 
		exit 1
fi 

echo "Build geoserver docker image"

#curl -jkSL https://raw.githubusercontent.com/terrestris/docker-geoserver/master/Dockerfile -o ./Dockerfile

docker build --force-rm --build-arg GS_VERSION=2.15.0 -t geoserver:2.15.0 .

echo "Starting geoserver container..."

docker run -d -v $(pwd)/gs-catalog:/opt/geoserver_data/ -p 80:8080 --restart=on-failure --name $CONTAINER_NAME geoserver:2.15.0
sleep 10

echo "Running $CONTAINER_NAME..."
echo "To stop|restart geoserver container please use: sudo docker stop|restart $CONTAINER_NAME"
