--CREATE copy of population for scenarios
SELECT setval('buildings_modified_gid_seq', (SELECT MAX(gid) FROM buildings));

--ADD Column population_gid when does not exists
ALTER TABLE population
ADD COLUMN IF NOT EXISTS building_gid int;

DROP TABLE IF EXISTS population_userinput;
CREATE TABLE population_userinput (like population INCLUDING ALL);
INSERT INTO population_userinput
SELECT * FROM population;

ALTER TABLE population_userinput ADD COLUMN userid integer;
CREATE INDEX ON population_userinput(userid);
ALTER TABLE population_userinput ADD COLUMN buildings_modified_id integer;
CREATE INDEX ON population_userinput(buildings_modified_id);

--Add Foreign Key to population_userinput  
ALTER TABLE population_userinput
ADD CONSTRAINT population_userinput_id_fkey FOREIGN KEY (buildings_modified_id) 
REFERENCES buildings_modified(gid) ON DELETE CASCADE;