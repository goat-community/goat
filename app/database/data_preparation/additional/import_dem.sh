
#gdalwarp -s_srs EPSG:4258 -t_srs EPSG:4326 -dstnodata -999.0 -r near -ot Float32 -of GTiff -te 11.3189 48.2880 11.7661 48.0175 dem.tif dem_cut1.tif

#raster2pgsql -c -C -s 4326 -f rast -F -I -M -t 100x100 dem_cut.tif public.dem > dem_cut.sql
#psql -U goat -d goat -f dem_cut.sql

