### GEOAPI

The aim of this service is to provide OGC-compliant Geoservices. At the moment there OGC Features and OGC Feature Tiles are implemented.
This service is based on Tipg (https://github.com/developmentseed/tipg). 

It was decided not to create a fork of the project but instead for now monkey patch some of the classes to have the custom behavior that is needed in particular for reading the data from one table per user and geometry typ instead of having one table per collection. For the use cases of GOAT having one table per collection would result in having too many tables, which could lead to problem on maintaining the DB.

