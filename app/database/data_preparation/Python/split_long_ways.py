#Split long network links in order to make pedestrian routing more precise a buffer is set in order to split only the lines within a certain radius
import psycopg2
con=psycopg2.connect(dbname='goat', host='localhost', port = 65432, user='goat',password='earlmanigault')
cursor=con.cursor()


sql_tables = '''
DROP TABLE IF EXISTS ways_split_long_vertices_pgr cascade;
CREATE TABLE ways_split_long_vertices_pgr (
	id bigserial NOT NULL,
	geom geometry NULL,
	CONSTRAINT ways_split_long_vertices_pgr_pkey PRIMARY KEY (id)
);
DROP TABLE IF EXISTS ways_split_long cascade;
create table ways_split_long(
	id serial, 
	class_id integer,
	length_m float, 
	source integer, 
	target integer, 
	ways_id bigint,
	geom geometry,
	CONSTRAINT ways_split_long_pkey PRIMARY KEY (id)
);

ALTER TABLE public.ways_split_long ADD CONSTRAINT ways_split_long_class_id_fkey FOREIGN KEY (class_id) REFERENCES osm_way_classes(class_id);
ALTER TABLE public.ways_split_long ADD CONSTRAINT ways_split_long_source_fkey FOREIGN KEY (source) REFERENCES ways_split_long_vertices_pgr(id);
ALTER TABLE public.ways_split_long ADD CONSTRAINT ways_split_long_target_fkey FOREIGN KEY (target) REFERENCES ways_split_long_vertices_pgr(id);

CREATE INDEX ways_split_long_source_idx ON ways_split_long USING btree (source);
CREATE INDEX ways_split_long_target_idx ON ways_split_long USING btree (target);
CREATE INDEX ways_split_long_index ON ways_split_long USING gist (geom);
CREATE INDEX ways_split_long_vertices_pgr_index ON ways_split_long_vertices_pgr USING gist (geom);
CREATE TABLE preliminary_ways_split_long(
    ways_id integer,
    geom geometry,
    class_id integer
);

'''

cursor.execute(sql_tables)

max_length = 300

cursor.execute ( ''' with  array_class_ids as
(
	SELECT unnest(variable_array::integer[]) as class_id
	FROM variable_container v
	WHERE v.identifier = 'excluded_class_id_walking'
),
array_excluded_foot as (
	SELECT unnest(variable_array) as foot
	FROM variable_container v
	WHERE v.identifier = 'categories_no_foot'
)
SELECT id, 1/ceil(length_m/%i) as fraction, w.class_id  
FROM ways w, array_class_ids a 
WHERE length_m > %i 
AND w.class_id not in (select * from array_class_ids)
AND (foot not in (select * from array_excluded_foot) OR foot IS NULL);
'''
% (max_length,max_length)
)
ways_to_split = cursor.fetchall()

 

for i in ways_to_split:
    fraction = i[1]
    end = 0
    while end < 1:
        start = round(end,5)
        end = round(end+fraction,5)
        if end > 1:
            end = 1
        #print(end)
        cursor.execute('''insert into preliminary_ways_split_long(ways_id,class_id,geom)
                          select id ways_id,class_id, st_linesubstring(geom,%f,%f)
                          geom from ways where id=%i''' % (start,end,i[0]))

        con.commit()
        
cursor.execute('''INSERT INTO ways_split_long(geom,ways_id) 
               select distinct on (geom) geom, ways_id, class_id
               from preliminary_ways_split_long; 
               drop table preliminary_ways_split_long; 
               ''')     
        

sql_fill_tables = '''
UPDATE ways_split_long set class_id = ways.class_id from ways
where ways_id = ways.id;
insert into ways_split_long(class_id,ways_id,geom)
select class_id,w.id ways_id, geom 
from ways w
where w.id not in (select ways_id from ways_split_long);
insert into ways_split_long_vertices_pgr(geom)
(
	select distinct geom from(
		select st_startpoint(geom) geom
		from ways_split_long
		union all
		select st_endpoint(geom) geom
		from ways_split_long
	) x
);
with s as (
	select w.id,st_startpoint(w.geom), v.id as source
	from ways_split_long w, ways_split_long_vertices_pgr v
	where st_startpoint(w.geom) = v.geom
) 
UPDATE ways_split_long set source = s.source from s where ways_split_long.id = s.id;
with t as (
	select w.id,st_endpoint(w.geom), v.id as target
	from ways_split_long w, ways_split_long_vertices_pgr v
	where st_endpoint(w.geom) = v.geom
) 
UPDATE ways_split_long set target = t.target from t where ways_split_long.id = t.id;
UPDATE ways_split_long set length_m = st_length(geom::geography);
'''
cursor.execute(sql_fill_tables)
con.commit()
con.close()


