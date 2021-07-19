# Rounding solution from: https://gis.stackexchange.com/questions/321518/rounding-coordinates-to-5-decimals-in-geopandas
import copy
import re
import geopandas as gpd
import zipfile
from db.db import Database
from geocube.api.core import make_geocube
from shapely.wkt import loads
from os import remove

db = Database()


class Profiles:
    def __init__(self):
        self.batch_size = 1000
        self.output_format = 'GeoJSON'
        self.out_dir = '/opt/data/'
        self.filename = self.out_dir + 'ways_profile_points.geojson'
        self.profile_table = 'ways_profile'
        self.impedance_table = 'ways_impedance'
        self.impedance_step = 10
        self.compress=True
        self.trim_decimals = True
        self.decimals = 5
        self.simpledec = re.compile(r"\d*\.\d+")
        self.check_drivers
        self.enable_driver=False
        self.raster=False
        self.bigtiff='YES'
        self.filter_ways='''WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container(\'excluded_class_id_cycling\')))'''                        

    def check_drivers(self):
        from fiona import supported_drivers
        from fiona._env import GDALEnv        

        # Check default Geopandas against FIONA drivers
        if self.output_format not in supported_drivers:
            self.enable_driver=True        
            drv = GDALEnv().drivers()
            if self.output_format not in drv:
                print('GDAL Driver {0} not present or misspelled'.format(self.output_format))
                exit(1)

    @staticmethod
    def ways2sql(ways):
        lsql = '('
        for w in ways:
            lsql = lsql + '{0},'.format(w)
        lsql = lsql[:-1] + ')'
        return lsql

    def mround(self, match):        
        return "{:.{}f}".format(float(match.group()), self.decimals)

    def trim(self, gdf):
        return gdf.geometry.apply(lambda x: loads(re.sub(self.simpledec, self.mround, x.wkt)))

    def get_chunks(self, table='ways'):
        r = db.select(query='SELECT count(*) FROM ways {0};'.format(self.filter_ways))
        chunks = range(int(r[0][0] / self.batch_size)+1)
        return chunks

    def get_elevation(self, way_list=None):
        if way_list is None:
            gdf_master = None
            batches = self.get_chunks()
            for b in batches:
                sql = """
                    WITH segments AS (
                        SELECT id FROM ways {2} LIMIT {0} OFFSET {1}
                    )                                
                    
                    SELECT seg.return_id as way_id, seg.elevs as elevation, seg.return_geom as geom
                    FROM segments s,
                    LATERAL get_slope_profile_precompute(s.id) seg;        
                """.format(self.batch_size, b * self.batch_size, self.filter_ways)
                gdf = db.select(query=sql, return_type='geodataframe')                
                if self.trim_decimals:
                    gdf.geometry = self.trim(gdf)
                if gdf_master is None:
                    gdf_master = copy.deepcopy(gdf)
                else:
                    t = gdf_master.append(gdf)
                    gdf_master = copy.deepcopy(t)            
            return gdf_master
        else:
            ways = self.ways2sql(way_list)
            sql = """
                    WITH segments AS (
                        SELECT id FROM ways WHERE id IN {0}
                    )                                
                    
                    SELECT seg.return_id as way_id, seg.elevs as elevation, seg.return_geom as geom
                    FROM segments s,
                    LATERAL get_slope_profile_precompute(s.id) seg;        
                """.format(ways)
            gdf = db.select(query=sql, return_type='geodataframe')
            if self.trim_decimals:
                gdf.geometry = self.trim(gdf)
            return gdf

    def get_impedance(self):
        sql = '''
                WITH profiles AS (
                    SELECT a.way_id, array_agg(a.elevation) AS elevation, max(length_m) AS sub_link_length,
                        max(b.geom) AS geom        
                    FROM {0} a
                    JOIN ways b ON a.way_id::bigint = b.id
                    GROUP by a.way_id
                )
                
                SELECT a.elevation::text, sub_link_length, c.imp AS s_imp, c.rs_imp, a.geom    
                FROM profiles a,
                LATERAL compute_impedances(a.elevation, sub_link_length, {1}) c;            
            '''.format(self.profile_table, self.impedance_step)
        gdf = db.select(query=sql, return_type='geodataframe')
        if self.trim_decimals:
            gdf.geometry = self.trim(gdf)
        return gdf

    def write_zip(self):
        zout = zipfile.ZipFile(self.filename + '.zip', "w", zipfile.ZIP_DEFLATED)
        zout.write(self.filename)
        zout.close()
        remove(self.filename)

    def write_file(self, df):
        if not self.raster:
            # Enable not default FIONA drivers
            if self.enable_driver:
                gpd.io.file.fiona.drvsupport.supported_drivers[self.output_format] = 'rw'
            df.to_file(self.filename, driver=self.output_format)
        else:
            self.write_raster(df)

        if self.compress:
            self.write_zip()

    def write_raster(self, df):
        # TODO: https://github.com/corteva/geocube/blob/master/geocube/geo_utils/geobox.py#L79
        df.rename(columns={'geom': 'geometry'}, inplace=True)
        cube = make_geocube(
            df,
            measurements=["elevation"],
            resolution=(-0.0001, 0.0001)
        )
        cube.elevation.rio.to_raster(self.filename, bigtiff=self.bigtiff)

# TODO: Move this to dedicated UnitTest class
# Test...

# Enable timer
# import time
# start = time.time()

# Initialize
# p = Profiles()

# Test elevation profiles
# df = p.get_elevation(way_list=[31,47,48,49,9,15,20,11,16,17])
# df = p.get_elevation()

# Vector Output
# p.output_format = 'PGDUMP'
# p.check_drivers()
# p.filename = '/opt/data/ways_profile_test.sql'
# p.write_file(df)

# p.output_format = 'GeoJSON'
# p.check_drivers()
# p.filename = '/opt/data/ways_profile_test.geojson'
# p.write_file(df)

# Raster Output
# p.raster = True
# p.filename = '/opt/data/ways_profile_test.tif'
# p.write_file(df)

# Test Impedance Calculation
# p.profile_table = 'ways_profile_test'
# df = p.get_impedance()

# Vector Output
# p.output_format = 'PGDUMP'
# p.check_drivers()
# p.filename = '/opt/data/ways_impedance_test.sql'
# p.write_file(df)

# Finish timmer
# end = time.time()
# print('Finished in ' + str(end - start) + ' seconds')

