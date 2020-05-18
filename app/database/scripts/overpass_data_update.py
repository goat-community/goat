import psycopg2 
from datetime import timedelta, datetime
import requests
import xml.etree.ElementTree as ET

from db_functions import ReadYAML
from db_functions import DB_connection

diff_time = (datetime.utcnow() - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

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

def overpass_pois(pois_type,pois_categories,diff_time):
    overpass_url = "http://overpass-api.de/api/interpreter"
    pois_categories = str(pois_categories).replace("'","").replace(",","|").replace(" ","")[1:-1]
    overpass_query = '''[diff:"%s"];
    node[%s~'%s']%s;
    out center;
    ''' % (diff_time,pois_type,pois_categories,bbox)
    print(overpass_query)
    response = requests.get(overpass_url, params={'data': overpass_query})

    return response 


def xml_to_sql(xml,pois_tags):
    root = ET.fromstring(xml)
    bulk_sql_update = ''
    
    for child in root.findall('./action/new/node'):
        osm_id = child.attrib['id']
        geom = 'ST_SETSRID(ST_Point(%s,%s),4326)' % (child.attrib['lon'], child.attrib['lat'])
        pairs_to_update = ''
        for tag in child:
            key = tag.attrib['k']
            if key in pois_tags:
                key_value = ",%s='%s'" % (pois_tags[key],tag.attrib['v'].replace("'","''"))
                pairs_to_update = pairs_to_update + key_value
                
        sql_update = "UPDATE pois_mapping SET geom = %s %s WHERE osm_id = %s AND origin_geometry ='point';" % (geom,pairs_to_update,osm_id)
     
        bulk_sql_update = bulk_sql_update + sql_update 
    return bulk_sql_update    

def psycopg_execute(sql,cursor,con):
    print(sql)
    if sql != '':
        cursor.execute(sql)
        con.commit()
  

amenity_attributes = {'amenity':'amenity','opening_hours':'opening_hours','wheelchair':'wheelchair','name':'name','origin':'orign','organic':'organic'}
response = overpass_pois('amenity',ReadYAML().mapping_conf()['amenity'],diff_time)
psycopg_execute(xml_to_sql(response.content,amenity_attributes),cursor,con)


shop_attributes = {'shop':'amenity','opening_hours':'opening_hours','wheelchair':'wheelchair','name':'name','origin':'orign','organic':'organic'}
response = overpass_pois('shop',ReadYAML().mapping_conf()['shop_osm'],diff_time)
psycopg_execute(xml_to_sql(response.content,amenity_attributes),cursor,con)

con.close()
