#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml, os, psycopg2, glob


def bulk_compute_profile(db_name, user, port, host, password, size):
    import psycopg2

    con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (db_name,user,str(port),host,password))
    cursor = con.cursor()

    cursor.execute('SELECT count(*) FROM ways;')
    cnt_ways = cursor.fetchall()[0][0]

    cursor.execute("""
        DROP TABLE IF EXISTS ways_profile;
        
        CREATE TABLE ways_profile (
        way_id bigint NOT NULL,
        elevation decimal NOT NULL,
        geom geometry NOT NULL
        );
        
        CREATE INDEX way_id_idx ON ways_profile USING btree(way_id);
        CREATE INDEX geom_idx ON ways_profile USING gist(geom);
    """)

    con.commit()

    batches = range(int(cnt_ways / size)+1)

    # TODO: Enable threading/parallelism
    for b in batches:
        sql = """
            WITH segments AS (
                SELECT id FROM ways LIMIT {0} OFFSET {1}
            )
            
            
            INSERT INTO ways_profile
            SELECT seg.return_id as way_id, seg.elevs as elevation, seg.return_geom as geom                         
            FROM segments s,
            LATERAL get_slope_profile_precompute(s.id) seg;        
        """.format(size, b*size)

        cursor.execute(sql)
        con.commit()





