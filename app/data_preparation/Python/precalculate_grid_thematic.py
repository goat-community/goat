import psycopg2

import time
import math
from variables_precalculate import *




con = psycopg2.connect("dbname='goat' user='goat' host='localhost' password='earlmanigault'")
cursor = con.cursor()



def calculate_isochrones(grid_size):
	grid_size = str(grid_size)
	snap_tolerance = math.sqrt(2)*int(grid_size)
	cursor.execute(prepare_tables.replace('grid_size',grid_size))
	con.commit()
	cursor.execute('select grid_id, st_x(st_centroid(geom)), st_y(st_centroid(geom)) from grid_%s order by grid_id' % (grid_size))
	grid = cursor.fetchall()
	for i in grid:
	    #time.sleep(1)
	    
	    grid_id = i[0]
	    x = i[1]
	    y = i[2]
	    insert_into = '''insert into precalculate_walking_%s select * from isochrones_precalculate(%s,%f,%f,%i,%f,%f,%i)''' % (grid_size,15,x,y,grid_id,83.33,0.99,snap_tolerance)
	    insert_into = insert_into.replace('grid_size',grid_size)
	    print(insert_into)
	    
	    try:
	        cursor.execute(insert_into)
	        cursor.execute(final_sql.replace('grid_size',grid_size))
	        cursor.execute(thematic_data_sql.replace('grid_id_replace',str(grid_id)).replace('grid_size',grid_size))
	        con.commit()
	    except Exception as e:
	        print(e)
	        cursor.execute('rollback;')
	        continue




def calculate_index(grid_size):
    grid_size = str(grid_size)
    
   
    cursor.execute("select variable_array from variable_container where identifier = 'poi_categories'")
    pois=cursor.fetchall()[0][0]
    cursor.execute(sql_new_grid.replace('grid_size',grid_size))
    
    for i in sensitivities:
        
        sensitivity = str(i).split('.')[1]
        cursor.execute('alter table precalculate_walking_%s add column index_0_%s jsonb' % (grid_size,sensitivity))
        cursor.execute('''update precalculate_walking_%s set index_0_%s='{"a":"first_value"}'::jsonb''' % (grid_size,sensitivity))
        
        sql_expand_json = 'select g.grid_id, '
        
        for x in public_transport_stops+pois:
            #sql_expand_json = sql_expand_json + '(index_0_001 ->> '+"'"+x + "')::float as "+x+','
                   
            cursor.execute(sql_calculate_accessibility.replace('amenity_type',x).replace('001',sensitivity).replace('grid_size',grid_size))
          
            con.commit()
        
        
        
       # sql_expand_json = sql_expand_json[:-1] + ''' ,g.geom, 0.001 as sensitivity from precalculate_walking_100 p,grid g 
                                                  #  where p.grid_id = g.grid_id'''.replace('001',sensitivity).replace('100',grid_size)
        
      # print(sql_expand_json)
        
        cursor.execute('''update precalculate_walking_100 set index_0_001= index_0_001- 'a' '''.replace('001',sensitivity).replace('100',grid_size))
        
        
        cursor.execute('alter table grid_%s add column index_0_%s jsonb' % (grid_size,sensitivity))
        cursor.execute('''update grid_100 set index_0_001 = p.index_0_001 
                          from precalculate_walking_100 p where grid_100.grid_id = p.grid_id'''.replace('001',sensitivity).replace('100',grid_size))
        #if sensitivities.index(i) == 0:
            
            #cursor.execute('create table grid_%s as ' % (grid_size) + sql_expand_json)
        
        #else:
            #cursor.execute('insert into grid_%s ' % (grid_size) + sql_expand_json)
        con.commit()
    
    #cursor.execute('drop table if exists grid')
    con.commit()






#calculate_isochrones(1000)   
#calculate_index(1000)
#calculate_isochrones(300)   
#calculate_index(300)
calculate_isochrones(300)   
calculate_index(300)

#calculate_isochrones(500)
#calculate_isochrones(800)
#calculate_isochrones(1000)



con.close()
