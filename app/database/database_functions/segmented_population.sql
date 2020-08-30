SELECT count(cod_mzn) FROM pop_block;

SELECT * FROM pop_block;


----------------------------------------
-------- NEW population process---------
----------------------------------------

-- 1. GENERAL population per block

DROP TABLE IF EXISTS pop_gen;
SELECT cod_mzn AS id_block, sum(population::int) AS population INTO pop_gen FROM pop_block GROUP BY cod_mzn;
SELECT * FROM pop_gen;
-- 2. Population per block BY gender

DROP TABLE IF EXISTS pop_gen;
SELECT cod_mzn, sum(population::int) AS total_pop, sum("S_01"::int) AS pop_male, sum("S_02"::int) AS pop_female INTO pop_gen FROM pop_block GROUP BY cod_mzn;

-- 3. Population per block BY age GROUP

DROP TABLE IF EXISTS pop_age;
SELECT * INTO pop_age FROM crosstab(
'SELECT cod_mzn, "AGE_GROUP", sum(population::int) from pop_block GROUP BY cod_mzn, "AGE_GROUP" order by 1,2',
'SELECT DISTINCT age_group FROM age_group_dic order by age_group;'
) AS ct ("Section" TEXT, "1" int, "2" int, "3" int, "4" int, "5" int, "6" int,
		"7" int, "8" int, "9" int, "10" int, "11" int, "12" int, "13" int, "14" int,
		"15" int, "16" int, "17" int, "18" int, "19" int, "20" int, "21" int);
SELECT * FROM pop_age;
UPDATE pop_age SET "1" = 0 WHERE "1" IS NULL;
UPDATE pop_age SET "2" = 0 WHERE "2" IS NULL;
UPDATE pop_age SET "3" = 0 WHERE "3" IS NULL;
UPDATE pop_age SET "4" = 0 WHERE "4" IS NULL;
UPDATE pop_age SET "5" = 0 WHERE "5" IS NULL;
UPDATE pop_age SET "6" = 0 WHERE "6" IS NULL;
UPDATE pop_age SET "7" = 0 WHERE "7" IS NULL;
UPDATE pop_age SET "8" = 0 WHERE "8" IS NULL;
UPDATE pop_age SET "9" = 0 WHERE "9" IS NULL;
UPDATE pop_age SET "10" = 0 WHERE "10" IS NULL;
UPDATE pop_age SET "11" = 0 WHERE "11" IS NULL;
UPDATE pop_age SET "12" = 0 WHERE "12" IS NULL;
UPDATE pop_age SET "13" = 0 WHERE "13" IS NULL;
UPDATE pop_age SET "14" = 0 WHERE "14" IS NULL;
UPDATE pop_age SET "15" = 0 WHERE "15" IS NULL;
UPDATE pop_age SET "16" = 0 WHERE "16" IS NULL;
UPDATE pop_age SET "17" = 0 WHERE "17" IS NULL;
UPDATE pop_age SET "18" = 0 WHERE "18" IS NULL;
UPDATE pop_age SET "19" = 0 WHERE "19" IS NULL;
UPDATE pop_age SET "20" = 0 WHERE "20" IS NULL;
UPDATE pop_age SET "21" = 0 WHERE "21" IS NULL;

-- 3. Population per block BY strata

DROP TABLE IF EXISTS pop_strata;
SELECT * INTO pop_strata FROM crosstab(
'SELECT cod_mzn, "VA1_ESTRATO", sum(population::int) from pop_block GROUP BY cod_mzn, "VA1_ESTRATO" order by 1,2',
'SELECT DISTINCT "VA1_ESTRATO" FROM pop_block order by "VA1_ESTRATO";'
) AS ct ("Section" TEXT, "0" int, "1" int, "2" int, "3" int, "4" int, "5" int, "6" int,
		"9" int);

UPDATE pop_strata SET "0" = 0 WHERE "0" IS NULL;
UPDATE pop_strata SET "1" = 0 WHERE "1" IS NULL;
UPDATE pop_strata SET "2" = 0 WHERE "2" IS NULL;
UPDATE pop_strata SET "3" = 0 WHERE "3" IS NULL;
UPDATE pop_strata SET "4" = 0 WHERE "4" IS NULL;
UPDATE pop_strata SET "5" = 0 WHERE "5" IS NULL;
UPDATE pop_strata SET "6" = 0 WHERE "6" IS NULL;
UPDATE pop_strata SET "9" = 0 WHERE "9" IS NULL;
	
SELECT * FROM pop_strata;

SELECT * FROM blocks_dane;
SELECT * FROM pop_strata ps, blocks_dane bd WHERE "Section" =  bd.cod_census;

-- 4. Verifications


SELECT * FROM pop_strata;

SELECT sum("0"),sum("1"),sum("2"),sum("3"),sum("4"),sum("5"),sum("6"),sum("9") FROM pop_strata;

SELECT sum("1") + sum("2") + sum("3") + sum("4") + sum("5") + sum("6") + sum("7") + sum("8") + sum("9") + sum("10") + sum("11")
		 + sum("12") + sum("13") + sum("14") + sum("15") + sum("16") + sum("17") + sum("18") + sum("19") + sum("20") + sum("21")



SELECT * FROM pop_block WHERE cod_mzn = '110011000000031080104'

SELECT count(cod_mzn) FROM pop_block;




-- Cleaning mzn code dane


SELECT * FROM manzanas_dane;

SELECT geom, concat(mpio_ccdgo,clas_ccdgo,'00',clas_ccdgo, setr_ccdgo,secr_ccdgo, setu_ccdgo, secu_ccdgo, manz_ccdgo) AS dane_manz_code, shape_area, shape_leng INTO manzanas_dane_fixed FROM manzanas_dane;

SELECT * FROM manzanas_dane_fixed;


