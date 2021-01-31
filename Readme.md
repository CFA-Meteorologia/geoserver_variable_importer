Purpose

These scripts are meant to be run after a run of WRF is finished in order to fill
databases of the app for management of WRF runs and geoserver layers.

#Installation guide

* install pydev as it is said here https://realpython.com/intro-to-pyenv/
* Execute 
    1. ```sudo apt-get install libgdal-dev```
    1. ```pyenv install 3.9.0```
    1. ```pyenv virtualenv 3.9.0 geoserver_variable_importer```
    1. ```pyenv local geoserver_variable_importer```
    1. ```pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')```
    1. ```pip install python-dev-tools```
    1. ```pip install -r requirements.txt```
    1. ```cp config.yml.example config.yml```, and change there configurations for your environment

#Docs for integration with geoserver
* [Image Mosaic data store documentation](https://docs.geoserver.org/latest/en/user/tutorials/imagemosaic_timeseries/imagemosaic_timeseries.html)
* [geoserver-restconfig Library to work with geoserver through api rest](https://pypi.org/project/geoserver-restconfig/)
* https://gis.stackexchange.com/questions/211717/geoserver-imagemosaic-creation-through-rest-api-with-postgis-granule-indexing

#Raster organization on geoserver
Each variable in each domain will be represented by a coverageStore with time dimension
and a wms layer that exposes the images. So each time representation of a variable
can be queried by using `TIME=[Needed Time]` using the wms service. Take for example `T2`
for domain 1 at `2018-05-02_00:00:00` you could get its value using layer name `T2_D1_WMS` and
`TIME=2018-05-02_00:00:00`, the store created for such variable and domain would be named `T2_D1`
