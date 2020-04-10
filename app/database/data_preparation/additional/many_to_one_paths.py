#This script calculates the fastest path from many origins to one destinations
#and weights the path according the number of residents and employment at a certain building
import psycopg2
con=psycopg2.connect(dbname='goat', host='localhost', port = 65432, user='goat',password='earlmanigault')
cursor=con.cursor()

destination_x = 10.684361
destination_y = 47.575645
buffer_destination = 1000

sql_origins= '''select population_building,st_x(st_Centroid(geom)),st_y(st_Centroid(geom))
from buildings_pop
where st_intersects(geom,
st_buffer(st_setsrid(st_point(%f,%f),4326)::geography,%i))''' % (destination_x,destination_y,buffer_destination)


cursor.execute('DROP TABLE IF EXISTS onetomany_weighted; create table onetomany_weighted(id serial,persons integer, geom geometry);')
cursor.execute(sql_origins)
population = cursor.fetchall()


#Add Bundeswehr
cursor.execute('''
with x as (
	select way geom from planet_osm_polygon 
	where building is not null
	and st_intersects(way,(select way geom from planet_osm_polygon where osm_id = '30991201'))
)
select round(st_area(geom::geography)/(select sum(st_area(geom::geography)) from x)*1090) as employees,
st_x(st_centroid(geom)),st_y(st_centroid(geom))
from x
''')
employees=cursor.fetchall()
#Add manually big point-working locations
employees.append((101,10.674913,47.575498)) #MPE Garry
employees.append((300,10.674391,47.573509)) #PMG Füssen
employees.append((250,10.670645,47.573964)) #Bihler
employees.append((63,10.678405,47.577558)) #Scheibel
employees.append((150,10.673072,47.572910)) #Zetka

origins =  population + employees

for i in origins:
    print("insert into onetomany_weighted(persons,geom) SELECT %i, geom from pgr_fromAtoB_split_long('ways_split_long',%f,%f,%f,%f);" % (i[0],i[1],i[2],destination_x,destination_y))
    cursor.execute("insert into onetomany_weighted(persons,geom) SELECT %i, geom from pgr_fromAtoB_split_long('ways_split_long',%f,%f,%f,%f);" % (i[0],i[1],i[2],destination_x,destination_y))
con.commit()
con.close()                  
                   
