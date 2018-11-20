# TuM geoserver docker image

Based on [terrestris/tomcat](https://github.com/terrestris/docker-tomcat):

## Quick tips

Create a new folder for Geoserver

`mkdir goat_geoserver`

Create new folder for the gs-catalog inside the folder of Geoserver

`mkdir gs-catalog`
`mkdir additional-libs`

If you want to migrate from existing Geoserver:
You have to move everything under geoserver/data to the gs-catalog folder.


### Git repo for geoserver TuM catalog

* Initialize a git repo for gs-catalog folder
* Since docker runs as sudo, for every geoserver catalog change ownership of recent create files with:
	* `sudo chown -R myuser:mygroup gs-catalog`
* Git add and commit as usual


### Upgrade geoserver version docker image

To upgrade geoserver version easily in future just run this command, where Dockerfile image lives (replace <geoserver_version> with desired version)

`sudo docker build --force-rm --build-arg GS_VERSION=<geoserver_version> -t geoserver:<geoserver_version> .`

Then run a new container with same catalog folder (again replace <geoserver_version>, <container_name> and <relative_path_to_catalog>)

`docker run -d -v $(pwd)/<relative_path_to_catalog>:/opt/geoserver_data/ -p 80:8080 --restart=on-failure --name <container_name> geoserver:<geoserver_version>`

## Support

For support please get in [touch](fernando.ribeiro@geocrafter.eu)
