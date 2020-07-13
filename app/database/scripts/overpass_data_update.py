import psycopg2 
from datetime import timedelta, datetime
import requests
import xml.etree.ElementTree as ET

from db_functions import ReadYAML
from db_functions import DB_connection

diff_time = (datetime.utcnow() - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")

#Get DB credentials
db_name,user,host,port,password = ReadYAML().db_credentials()
#Get buffer for study_area
buffer = ReadYAML().data_source()[2]
#Connect to database
db = DB_connection(db_name,user,host,port,password)
con,cursor = db.con_psycopg()
#Get bounding box for study area
cursor.execute('''SELECT ST_YMIN(ST_EXTENT(geom)),ST_XMIN(ST_EXTENT(geom)),ST_YMAX(ST_EXTENT(geom)),ST_XMAX(ST_EXTENT(geom))  
FROM (SELECT ST_BUFFER(ST_UNION(geom),%f) AS geom FROM study_area) b''' % (buffer))
bbox = str(cursor.fetchall()[0])

overpass_url = "http://overpass-api.de/api/interpreter"
feature_osm_tag = {"pois":"node","ways":"way","buildings":"way"}
sql_condition_for_update = {"pois":"AND origin_geometry = 'point'","ways":"","buildings":""}


def overpass_pois(pois_type,pois_categories,diff_time):
    pois_categories = str(pois_categories).replace("'","").replace(",","|").replace(" ","")[1:-1]
    overpass_query = '''[diff:"%s"];
    node[%s~'%s']%s;
    out center;
    ''' % (diff_time,pois_type,pois_categories,bbox)
    return requests.get(overpass_url, params={'data': overpass_query})

def overpass_ways(diff_time):
    overpass_query = '''[diff:"%s"];
    way
    [highway]%s;
    out;''' % (diff_time,bbox)
    return requests.get(overpass_url, params={'data': overpass_query})

def overpass_buildings(diff_time):
    overpass_query = '''[diff:"%s"];
    way
    [building]%s;
    out;''' % (diff_time,bbox)
    return requests.get(overpass_url, params={'data': overpass_query})

def xml_to_sql(xml,table,tags_translation):
    root = ET.fromstring(xml)
    bulk_sql_update = ''
    #Get column name of table
    sql_column_names = '''SELECT array_agg(column_name)
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name   = '%s_mapping'
    AND column_name NOT IN ('id','osm_id','source','target');
    ''' % table
    cursor.execute(sql_column_names)
    column_names = cursor.fetchall()[0][0].replace('{','').replace('}','').replace("'","").split(',')
    
    #Build dictionary for all column name while considering translation
    for i in column_names:
        if i not in tags_translation.keys():
            tags_translation[i] = i
    
    for child in root.findall('./action/new/%s' % feature_osm_tag[table]):
        osm_id = child.attrib['id']
        #geom = 'ST_SETSRID(ST_Point(%s,%s),4326)' % (child.attrib['lon'], child.attrib['lat'])
        pairs_to_update = ''
        child = child.findall('./tag')
        for tag in child:
            if tag.attrib['k'] in tags_translation:
                key = tag.attrib['k']
                tag_translated = tags_translation[key]
                if ':' in tag_translated:
                    tag_translated = '"%s"' % tag_translated
                key_value = ",%s='%s'" % (tag_translated,tag.attrib['v'].replace("'","''"))
                pairs_to_update = pairs_to_update + key_value
                
        sql_update = "UPDATE %s_mapping SET %s WHERE osm_id = %s %s; \n" % (table,pairs_to_update[1:],osm_id, sql_condition_for_update[table])
     
        bulk_sql_update = bulk_sql_update + sql_update 
    return bulk_sql_update    

def psycopg_execute(sql,cursor,con):
    print(sql)
    if sql != '':
        cursor.execute(sql)
        con.commit()
  


response = overpass_pois('amenity',ReadYAML().mapping_conf()['amenity'],diff_time)
amenity_translation = {}
print(xml_to_sql(response.content,'pois',amenity_translation))
psycopg_execute(xml_to_sql(response.content,'pois',amenity_translation),cursor,con)

response = overpass_pois('shop',ReadYAML().mapping_conf()['shop_osm'],diff_time)
shop_translation = {'shop':'amenity'}
print(xml_to_sql(response.content,'pois',shop_translation))
psycopg_execute(xml_to_sql(response.content,'pois',shop_translation),cursor,con)

response = overpass_ways(diff_time)
ways_translation = {}
print(xml_to_sql(response.content,'ways',ways_translation))
psycopg_execute(xml_to_sql(response.content,'ways',ways_translation),cursor,con)

response = overpass_buildings(diff_time)
buildings_translation = {}
print(xml_to_sql(response.content,'buildings',buildings_translation))
psycopg_execute(xml_to_sql(response.content,'buildings',buildings_translation),cursor,con)

open('/opt/data/overpass_update.txt', 'w').close()
file = open('/opt/data/overpass_update.txt','a')
file.write(diff_time+'\n')
file.close()

con.close()
