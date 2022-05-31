drop table if exists grid_access;
create table grid_access (
	grid_id numeric,
	population numeric,
	geom geometry,
	grocery_stores numeric,
	supermarket numeric,
	street_market numeric,
	stores numeric,
	bar numeric,
	restaurant numeric,
	cafe numeric,
	pub numeric,
	food_drinks numeric,
	newsstand numeric,
	kiosk numeric,
	bank numeric,
	atm numeric,
	post_office numeric,
	post_box numeric,
	hairdresser numeric,
	administration numeric,
	services numeric,
	commercial numeric,
	museum numeric,
	gallery numeric,
	arts_centre numeric,
	cinema numeric,
	theatre numeric,
	cultural numeric,
	sport_facilities numeric,
	fitness_centre numeric,
	playground numeric,
	sports numeric,
	pharmacy numeric,
	chemist numeric,
	doctors numeric,
	clinic numeric,
	hospital numeric,
	community_centre numeric,
	social_facility numeric,
	healthcare numeric,
	libraries numeric,
	nursery numeric,
	kindergarten numeric,
	primary_school numeric,
	secondary_school numeric,
	university numeric,
	education numeric,
	tram_stop numeric,
	bus_stop numeric,
	metro_station numeric,
	bike_sharing numeric,
	car_sharing numeric,
	public_transport numeric
	);
insert into grid_access (grid_id, population, geom)
select grid_id, population, geom from grid_heatmap;
ALTER TABLE grid_access add primary key (grid_id);


--commercial activities
update grid_access g
set grocery_stores = (select h.accessibility_index
FROM heatmap_dynamic('{"convenience":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set supermarket = (select h.accessibility_index
FROM heatmap_dynamic('{"supermarket":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set street_market = (select h.accessibility_index
FROM heatmap_dynamic('{"marketplace":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set stores = coalesce(a.grocery_stores,0)+coalesce(a.supermarket,0)+coalesce(a.street_market,0)
from grid_access a 
where g.grid_id = a.grid_id;

update grid_access g
set bar = (select h.accessibility_index
FROM heatmap_dynamic('{"Bar2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set restaurant = (select h.accessibility_index
FROM heatmap_dynamic('{"Restaurant2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set cafe = (select h.accessibility_index
FROM heatmap_dynamic('{"Café2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set pub = (select h.accessibility_index
FROM heatmap_dynamic('{"Pub2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set food_drinks = coalesce(a.bar,0)+coalesce(a.restaurant,0)+coalesce(a.cafe,0)+coalesce(a.pub,0)
from grid_access a 
where g.grid_id = a.grid_id;

update grid_access g
set newsstand = (select h.accessibility_index
FROM heatmap_dynamic('{"newsagent2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set kiosk = (select h.accessibility_index
FROM heatmap_dynamic('{"tobacco2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set bank = (select h.accessibility_index
FROM heatmap_dynamic('{"bank":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set atm = (select h.accessibility_index
FROM heatmap_dynamic('{"atm":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set post_office = (select h.accessibility_index
FROM heatmap_dynamic('{"post_office":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set post_box = (select h.accessibility_index
FROM heatmap_dynamic('{"post_box":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set hairdresser = (select h.accessibility_index
FROM heatmap_dynamic('{"hairdresser":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set administration = (select h.accessibility_index
FROM heatmap_dynamic('{"townhall":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set services =	coalesce(a.newsstand,0)+coalesce(a.kiosk,0)+coalesce(a.bank,0)+coalesce(a.atm,0)+
				coalesce(a.post_office,0)+coalesce(a.post_box,0)+coalesce(a.hairdresser,0)+coalesce(a.administration,0)
from grid_access a 
where g.grid_id = a.grid_id;

update grid_access g
set commercial = coalesce(a.grocery_stores,0)+coalesce(a.supermarket,0)+coalesce(a.street_market,0)+
				coalesce(a.bar,0)+coalesce(a.restaurant,0)+coalesce(a.cafe,0)+coalesce(a.pub,0)+
				coalesce(a.newsstand,0)+coalesce(a.kiosk,0)+coalesce(a.bank,0)+coalesce(a.atm,0)+
				coalesce(a.post_office,0)+coalesce(a.post_box,0)+coalesce(a.hairdresser,0)+coalesce(a.administration,0)
from grid_access a 
where g.grid_id = a.grid_id;

--cultural spaces

update grid_access g
set museum = (select h.accessibility_index
FROM heatmap_dynamic('{"museum":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set gallery = (select h.accessibility_index
FROM heatmap_dynamic('{"gallery":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set arts_centre = (select h.accessibility_index
FROM heatmap_dynamic('{"arts_centre":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set cinema = (select h.accessibility_index
FROM heatmap_dynamic('{"cinema":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set theatre = (select h.accessibility_index
FROM heatmap_dynamic('{"theatre":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set cultural = coalesce(a.museum,0)+coalesce(a.gallery,0)+coalesce(a.arts_centre,0)+
				coalesce(a.cinema,0)+coalesce(a.theatre,0)
from grid_access a 
where g.grid_id = a.grid_id;

--sports
update grid_access g
set sport_facilities = (select h.accessibility_index
FROM heatmap_dynamic('{"sports":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set fitness_centre = (select h.accessibility_index
FROM heatmap_dynamic('{"gym":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set playground = (select h.accessibility_index
FROM heatmap_dynamic('{"playground":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set sports = coalesce(a.sport_facilities,0)+coalesce(a.fitness_centre,0)+coalesce(a.playground,0)
from grid_access a 
where g.grid_id = a.grid_id;

--healthcare
update grid_access g 
set pharmacy = (select h.accessibility_index
FROM heatmap_dynamic('{"pharmacy":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set chemist = (select h.accessibility_index
FROM heatmap_dynamic('{"chemist":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set doctors = (select h.accessibility_index
FROM heatmap_dynamic('{"doctors":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set clinic = (select h.accessibility_index
FROM heatmap_dynamic('{"clinic":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set hospital = (select h.accessibility_index
FROM heatmap_dynamic('{"hospital":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set community_centre = (select h.accessibility_index
FROM heatmap_dynamic('{"community_":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set social_facility = (select h.accessibility_index
FROM heatmap_dynamic('{"social_facility2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set healthcare = coalesce(a.pharmacy,0)+coalesce(a.chemist,0)+coalesce(a.doctors,0)+
				coalesce(a.clinic,0)+coalesce(a.hospital,0)+coalesce(a.community_centre,0)+
				coalesce(a.social_facility,0)
from grid_access a 
where g.grid_id = a.grid_id;


--education
update grid_access g 
set libraries = (select h.accessibility_index
FROM heatmap_dynamic('{"library2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set nursery = (select h.accessibility_index
FROM heatmap_dynamic('{"nursery2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set kindergarten = (select h.accessibility_index
FROM heatmap_dynamic('{"kindergarten2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set primary_school = (select h.accessibility_index
FROM heatmap_dynamic('{"primary2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set secondary_school = (select h.accessibility_index
FROM heatmap_dynamic('{"secondary2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set university = (select h.accessibility_index
FROM heatmap_dynamic('{"university2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set education = coalesce(a.libraries,0)+coalesce(a.nursery,0)+coalesce(a.kindergarten,0)+
				coalesce(a.primary_school,0)+coalesce(a.secondary_school,0)+coalesce(a.university,0)
from grid_access a 
where g.grid_id = a.grid_id;

--public transport
update grid_access g 
set tram_stop = (select h.accessibility_index
FROM heatmap_dynamic('{"tram_stop":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set bus_stop = (select h.accessibility_index
FROM heatmap_dynamic('{"bus_stop":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set metro_station = (select h.accessibility_index
FROM heatmap_dynamic('{"subway_entrance":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set bike_sharing = (select h.accessibility_index
FROM heatmap_dynamic('{"bike_sharing2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set car_sharing = (select h.accessibility_index
FROM heatmap_dynamic('{"car_sharing2":{"sensitivity":300000,"weight":1}}'::jsonb,'default',0) h
WHERE h.grid_id = g.grid_id);

update grid_access g
set public_transport = coalesce(a.tram_stop,0)+coalesce(a.bus_stop,0)+coalesce(a.metro_station,0)+
				coalesce(a.bike_sharing,0)+coalesce(a.car_sharing,0)
from grid_access a 
where g.grid_id = a.grid_id;


--select distinct amenity from pois p;

--select distinct amenity from pois_userinput pu; 
--select distinct amenity from reached_pois_heatmap rph; 
--select * from POIS where amenity='arts_centre';
--select * from pois_userinput pu  where amenity='arts_centre';


--normalization of accessibility
drop table if exists grid_access_norm;
create table grid_access_norm as (
WITH stats AS (SELECT 
avg (grocery_stores) grocery_stores_avg, stddev (grocery_stores) as grocery_stores_stddev,
avg (supermarket) supermarket_avg, stddev (supermarket) as supermarket_stddev,
avg (street_market) street_market_avg, stddev (street_market) as street_market_stddev,
avg (stores) stores_avg, stddev (stores) as stores_stddev,
avg (bar) bar_avg, stddev (bar) as bar_stddev,
avg (restaurant) restaurant_avg, stddev (restaurant) as restaurant_stddev,
avg (cafe) cafe_avg, stddev (cafe) as cafe_stddev,
avg (pub) pub_avg, stddev (pub) as pub_stddev,
avg (food_drinks) food_drinks_avg, stddev (food_drinks) as food_drinks_stddev,
avg (newsstand) newsstand_avg, stddev (newsstand) as newsstand_stddev,
avg (kiosk) kiosk_avg, stddev (kiosk) as kiosk_stddev,
avg (bank) bank_avg, stddev (bank) as bank_stddev,
avg (atm) atm_avg, stddev (atm) as atm_stddev,
avg (post_office) post_office_avg, stddev (post_office) as post_office_stddev,
avg (post_box) post_box_avg, stddev (post_box) as post_box_stddev,
avg (hairdresser) hairdresser_avg, stddev (hairdresser) as hairdresser_stddev,
avg (administration) administration_avg, stddev (administration) as administration_stddev,
avg (services) services_avg, stddev (services) as services_stddev,
avg (commercial) commercial_avg, stddev (commercial) as commercial_stddev,
avg (museum) museum_avg, stddev (museum) as museum_stddev,
avg (gallery) gallery_avg, stddev (gallery) as gallery_stddev,
avg (arts_centre) arts_centre_avg, stddev (arts_centre) as arts_centre_stddev,
avg (cinema) cinema_avg, stddev (cinema) as cinema_stddev,
avg (theatre) theatre_avg, stddev (theatre) as theatre_stddev,
avg (cultural) cultural_avg, stddev (cultural) as cultural_stddev,
avg (sport_facilities) sport_facilities_avg, stddev (sport_facilities) as sport_facilities_stddev,
avg (fitness_centre) fitness_centre_avg, stddev (fitness_centre) as fitness_centre_stddev,
avg (playground) playground_avg, stddev (playground) as playground_stddev,
avg (sports) sports_avg, stddev (sports) as sports_stddev,
avg (pharmacy) pharmacy_avg, stddev (pharmacy) as pharmacy_stddev,
avg (chemist) chemist_avg, stddev (chemist) as chemist_stddev,
avg (doctors) doctors_avg, stddev (doctors) as doctors_stddev,
avg (clinic) clinic_avg, stddev (clinic) as clinic_stddev,
avg (hospital) hospital_avg, stddev (hospital) as hospital_stddev,
avg (community_centre) community_centre_avg, stddev (community_centre) as community_centre_stddev,
avg (social_facility) social_facility_avg, stddev (social_facility) as social_facility_stddev,
avg (healthcare) healthcare_avg, stddev (healthcare) as healthcare_stddev,
avg (libraries) libraries_avg, stddev (libraries) as libraries_stddev,
avg (nursery) nursery_avg, stddev (nursery) as nursery_stddev,
avg (kindergarten) kindergarten_avg, stddev (kindergarten) as kindergarten_stddev,
avg (primary_school) primary_school_avg, stddev (primary_school) as primary_school_stddev,
avg (secondary_school) secondary_school_avg, stddev (secondary_school) as secondary_school_stddev,
avg (university) university_avg, stddev (university) as university_stddev,
avg (education) education_avg, stddev (education) as education_stddev,
avg (tram_stop) tram_stop_avg, stddev (tram_stop) as tram_stop_stddev,
avg (bus_stop) bus_stop_avg, stddev (bus_stop) as bus_stop_stddev,
avg (metro_station) metro_station_avg, stddev (metro_station) as metro_station_stddev,
avg (bike_sharing) bike_sharing_avg, stddev (bike_sharing) as bike_sharing_stddev,
avg (car_sharing) car_sharing_avg, stddev (car_sharing) as car_sharing_stddev,
avg (public_transport) public_transport_avg, stddev (public_transport) as public_transport_stddev
                  FROM grid_access 
                  )
select * from (select grid_id, geom,
COALESCE ( ( grocery_stores - grocery_stores_avg) / grocery_stores_stddev, null ) as grocery_stores_norm,
COALESCE ( ( supermarket - supermarket_avg) / supermarket_stddev, null ) as supermarket_norm,
COALESCE ( ( street_market - street_market_avg) / street_market_stddev, null ) as street_market_norm,
COALESCE ( ( bar - bar_avg) / bar_stddev, null ) as bar_norm,
COALESCE ( ( restaurant - restaurant_avg) / restaurant_stddev, null ) as restaurant_norm,
COALESCE ( ( cafe - cafe_avg) / cafe_stddev, null ) as cafe_norm,
COALESCE ( ( pub - pub_avg) / pub_stddev, null ) as pub_norm,
COALESCE ( ( newsstand - newsstand_avg) / newsstand_stddev, null ) as newsstand_norm,
COALESCE ( ( kiosk - kiosk_avg) / kiosk_stddev, null ) as kiosk_norm,
COALESCE ( ( bank - bank_avg) / bank_stddev, null ) as bank_norm,
COALESCE ( ( atm - atm_avg) / atm_stddev, null ) as atm_norm,
COALESCE ( ( post_office - post_office_avg) / post_office_stddev, null ) as post_office_norm,
COALESCE ( ( post_box - post_box_avg) / post_box_stddev, null ) as post_box_norm,
COALESCE ( ( hairdresser - hairdresser_avg) / hairdresser_stddev, null ) as hairdresser_norm,
COALESCE ( ( administration - administration_avg) / administration_stddev, null ) as administration_norm,
COALESCE ( ( commercial - commercial_avg) / commercial_stddev, null ) as commercial_norm,
COALESCE ( ( museum - museum_avg) / museum_stddev, null ) as museum_norm,
COALESCE ( ( gallery - gallery_avg) / gallery_stddev, null ) as gallery_norm,
COALESCE ( ( arts_centre - arts_centre_avg) / arts_centre_stddev, null ) as arts_centre_norm,
COALESCE ( ( cinema - cinema_avg) / cinema_stddev, null ) as cinema_norm,
COALESCE ( ( theatre - theatre_avg) / theatre_stddev, null ) as theatre_norm,
COALESCE ( ( cultural - cultural_avg) / cultural_stddev, null ) as cultural_norm,
COALESCE ( ( sport_facilities - sport_facilities_avg) / sport_facilities_stddev, null ) as sport_facilities_norm,
COALESCE ( ( fitness_centre - fitness_centre_avg) / fitness_centre_stddev, null ) as fitness_centre_norm,
COALESCE ( ( playground - playground_avg) / playground_stddev, null ) as playground_norm,
COALESCE ( ( sports - sports_avg) / sports_stddev, null ) as sports_norm,
COALESCE ( ( pharmacy - pharmacy_avg) / pharmacy_stddev, null ) as pharmacy_norm,
COALESCE ( ( chemist - chemist_avg) / chemist_stddev, null ) as chemist_norm,
COALESCE ( ( doctors - doctors_avg) / doctors_stddev, null ) as doctors_norm,
COALESCE ( ( clinic - clinic_avg) / clinic_stddev, null ) as clinic_norm,
COALESCE ( ( hospital - hospital_avg) / hospital_stddev, null ) as hospital_norm,
COALESCE ( ( community_centre - community_centre_avg) / community_centre_stddev, null ) as community_centre_norm,
COALESCE ( ( social_facility - social_facility_avg) / social_facility_stddev, null ) as social_facility_norm,
COALESCE ( ( healthcare - healthcare_avg) / healthcare_stddev, null ) as healthcare_norm,
COALESCE ( ( libraries - libraries_avg) / libraries_stddev, null ) as libraries_norm,
COALESCE ( ( nursery - nursery_avg) / nursery_stddev, null ) as nursery_norm,
COALESCE ( ( kindergarten - kindergarten_avg) / kindergarten_stddev, null ) as kindergarten_norm,
COALESCE ( ( primary_school - primary_school_avg) / primary_school_stddev, null ) as primary_school_norm,
COALESCE ( ( secondary_school - secondary_school_avg) / secondary_school_stddev, null ) as secondary_school_norm,
COALESCE ( ( university - university_avg) / university_stddev, null ) as university_norm,
COALESCE ( ( education - education_avg) / education_stddev, null ) as education_norm,
COALESCE ( ( tram_stop - tram_stop_avg) / tram_stop_stddev, null ) as tram_stop_norm,
COALESCE ( ( bus_stop - bus_stop_avg) / bus_stop_stddev, null ) as bus_stop_norm,
COALESCE ( ( metro_station - metro_station_avg) / metro_station_stddev, null ) as metro_station_norm,
COALESCE ( ( bike_sharing - bike_sharing_avg) / bike_sharing_stddev, null ) as bike_sharing_norm,
COALESCE ( ( car_sharing - car_sharing_avg) / car_sharing_stddev, null ) as car_sharing_norm,
COALESCE ( ( public_transport - public_transport_avg) / public_transport_stddev, null ) as public_transport_norm,
COALESCE ( ( stores - stores_avg) / stores_stddev, null ) as stores_norm,
COALESCE ( ( services - services_avg) / services_stddev, null ) as services_norm,
COALESCE ( ( food_drinks - food_drinks_avg) / food_drinks_stddev, null ) as food_drinks_norm
       FROM grid_access, stats) h);   
     
   
--max_min of accessibility
drop table if exists grid_access_mx;
create table grid_access_mx as (
WITH stats AS (SELECT 
max (grocery_stores) grocery_stores_max, min (grocery_stores) as grocery_stores_min,
max (supermarket) supermarket_max, min (supermarket) as supermarket_min,
max (street_market) street_market_max, min (street_market) as street_market_min,
max (bar) bar_max, min (bar) as bar_min,
max (restaurant) restaurant_max, min (restaurant) as restaurant_min,
max (cafe) cafe_max, min (cafe) as cafe_min,
max (pub) pub_max, min (pub) as pub_min,
max (newsstand) newsstand_max, min (newsstand) as newsstand_min,
max (kiosk) kiosk_max, min (kiosk) as kiosk_min,
max (bank) bank_max, min (bank) as bank_min,
max (atm) atm_max, min (atm) as atm_min,
max (post_office) post_office_max, min (post_office) as post_office_min,
max (post_box) post_box_max, min (post_box) as post_box_min,
max (hairdresser) hairdresser_max, min (hairdresser) as hairdresser_min,
max (administration) administration_max, min (administration) as administration_min,
max (commercial) commercial_max, min (commercial) as commercial_min,
max (museum) museum_max, min (museum) as museum_min,
max (gallery) gallery_max, min (gallery) as gallery_min,
max (arts_centre) arts_centre_max, min (arts_centre) as arts_centre_min,
max (cinema) cinema_max, min (cinema) as cinema_min,
max (theatre) theatre_max, min (theatre) as theatre_min,
max (cultural) cultural_max, min (cultural) as cultural_min,
max (sport_facilities) sport_facilities_max, min (sport_facilities) as sport_facilities_min,
max (fitness_centre) fitness_centre_max, min (fitness_centre) as fitness_centre_min,
max (playground) playground_max, min (playground) as playground_min,
max (sports) sports_max, min (sports) as sports_min,
max (pharmacy) pharmacy_max, min (pharmacy) as pharmacy_min,
max (chemist) chemist_max, min (chemist) as chemist_min,
max (doctors) doctors_max, min (doctors) as doctors_min,
max (clinic) clinic_max, min (clinic) as clinic_min,
max (hospital) hospital_max, min (hospital) as hospital_min,
max (community_centre) community_centre_max, min (community_centre) as community_centre_min,
max (social_facility) social_facility_max, min (social_facility) as social_facility_min,
max (healthcare) healthcare_max, min (healthcare) as healthcare_min,
max (libraries) libraries_max, min (libraries) as libraries_min,
max (nursery) nursery_max, min (nursery) as nursery_min,
max (kindergarten) kindergarten_max, min (kindergarten) as kindergarten_min,
max (primary_school) primary_school_max, min (primary_school) as primary_school_min,
max (secondary_school) secondary_school_max, min (secondary_school) as secondary_school_min,
max (university) university_max, min (university) as university_min,
max (education) education_max, min (education) as education_min,
max (tram_stop) tram_stop_max, min (tram_stop) as tram_stop_min,
max (bus_stop) bus_stop_max, min (bus_stop) as bus_stop_min,
max (metro_station) metro_station_max, min (metro_station) as metro_station_min,
max (bike_sharing) bike_sharing_max, min (bike_sharing) as bike_sharing_min,
max (car_sharing) car_sharing_max, min (car_sharing) as car_sharing_min,
max (public_transport) public_transport_max, min (public_transport) as public_transport_min,
max (stores) stores_max, min (stores) as stores_min,
max (food_drinks) food_drinks_max, min (food_drinks) as food_drinks_min,
max (services) services_max, min (services) as services_min
                  FROM grid_access 
                  )
select * from (select grid_id, geom,
COALESCE ( ( grocery_stores - grocery_stores_min) / ( grocery_stores_max - grocery_stores_min), null ) as grocery_stores_mx,
COALESCE ( ( supermarket - supermarket_min) / ( supermarket_max - supermarket_min), null ) as supermarket_mx,
COALESCE ( ( street_market - street_market_min) / ( street_market_max - street_market_min), null ) as street_market_mx,
COALESCE ( ( bar - bar_min) / ( bar_max - bar_min), null ) as bar_mx,
COALESCE ( ( restaurant - restaurant_min) / ( restaurant_max - restaurant_min), null ) as restaurant_mx,
COALESCE ( ( cafe - cafe_min) / ( cafe_max - cafe_min), null ) as cafe_mx,
COALESCE ( ( pub - pub_min) / ( pub_max - pub_min), null ) as pub_mx,
COALESCE ( ( newsstand - newsstand_min) / ( newsstand_max - newsstand_min), null ) as newsstand_mx,
COALESCE ( ( kiosk - kiosk_min) / ( kiosk_max - kiosk_min), null ) as kiosk_mx,
COALESCE ( ( bank - bank_min) / ( bank_max - bank_min), null ) as bank_mx,
COALESCE ( ( atm - atm_min) / ( atm_max - atm_min), null ) as atm_mx,
COALESCE ( ( post_office - post_office_min) / ( post_office_max - post_office_min), null ) as post_office_mx,
COALESCE ( ( post_box - post_box_min) / ( post_box_max - post_box_min), null ) as post_box_mx,
COALESCE ( ( hairdresser - hairdresser_min) / ( hairdresser_max - hairdresser_min), null ) as hairdresser_mx,
COALESCE ( ( administration - administration_min) / ( administration_max - administration_min), null ) as administration_mx,
COALESCE ( ( commercial - commercial_min) / ( commercial_max - commercial_min), null ) as commercial_mx,
COALESCE ( ( museum - museum_min) / ( museum_max - museum_min), null ) as museum_mx,
COALESCE ( ( gallery - gallery_min) / ( gallery_max - gallery_min), null ) as gallery_mx,
COALESCE ( ( arts_centre - arts_centre_min) / ( arts_centre_max - arts_centre_min), null ) as arts_centre_mx,
COALESCE ( ( cinema - cinema_min) / ( cinema_max - cinema_min), null ) as cinema_mx,
COALESCE ( ( theatre - theatre_min) / ( theatre_max - theatre_min), null ) as theatre_mx,
COALESCE ( ( cultural - cultural_min) / ( cultural_max - cultural_min), null ) as cultural_mx,
COALESCE ( ( sport_facilities - sport_facilities_min) / ( sport_facilities_max - sport_facilities_min), null ) as sport_facilities_mx,
COALESCE ( ( fitness_centre - fitness_centre_min) / ( fitness_centre_max - fitness_centre_min), null ) as fitness_centre_mx,
COALESCE ( ( playground - playground_min) / ( playground_max - playground_min), null ) as playground_mx,
COALESCE ( ( sports - sports_min) / ( sports_max - sports_min), null ) as sports_mx,
COALESCE ( ( pharmacy - pharmacy_min) / ( pharmacy_max - pharmacy_min), null ) as pharmacy_mx,
COALESCE ( ( chemist - chemist_min) / ( chemist_max - chemist_min), null ) as chemist_mx,
COALESCE ( ( doctors - doctors_min) / ( doctors_max - doctors_min), null ) as doctors_mx,
COALESCE ( ( clinic - clinic_min) / ( clinic_max - clinic_min), null ) as clinic_mx,
COALESCE ( ( hospital - hospital_min) / ( hospital_max - hospital_min), null ) as hospital_mx,
COALESCE ( ( community_centre - community_centre_min) / ( community_centre_max - community_centre_min), null ) as community_centre_mx,
COALESCE ( ( social_facility - social_facility_min) / ( social_facility_max - social_facility_min), null ) as social_facility_mx,
COALESCE ( ( healthcare - healthcare_min) / ( healthcare_max - healthcare_min), null ) as healthcare_mx,
COALESCE ( ( libraries - libraries_min) / ( libraries_max - libraries_min), null ) as libraries_mx,
COALESCE ( ( nursery - nursery_min) / ( nursery_max - nursery_min), null ) as nursery_mx,
COALESCE ( ( kindergarten - kindergarten_min) / ( kindergarten_max - kindergarten_min), null ) as kindergarten_mx,
COALESCE ( ( primary_school - primary_school_min) / ( primary_school_max - primary_school_min), null ) as primary_school_mx,
COALESCE ( ( secondary_school - secondary_school_min) / ( secondary_school_max - secondary_school_min), null ) as secondary_school_mx,
COALESCE ( ( university - university_min) / ( university_max - university_min), null ) as university_mx,
COALESCE ( ( education - education_min) / ( education_max - education_min), null ) as education_mx,
COALESCE ( ( tram_stop - tram_stop_min) / ( tram_stop_max - tram_stop_min), null ) as tram_stop_mx,
COALESCE ( ( bus_stop - bus_stop_min) / ( bus_stop_max - bus_stop_min), null ) as bus_stop_mx,
COALESCE ( ( metro_station - metro_station_min) / ( metro_station_max - metro_station_min), null ) as metro_station_mx,
COALESCE ( ( bike_sharing - bike_sharing_min) / ( bike_sharing_max - bike_sharing_min), null ) as bike_sharing_mx,
COALESCE ( ( car_sharing - car_sharing_min) / ( car_sharing_max - car_sharing_min), null ) as car_sharing_mx,
COALESCE ( ( public_transport - public_transport_min) / ( public_transport_max - public_transport_min), null ) as public_transport_mx,
COALESCE ( ( food_drinks - food_drinks_min) / ( food_drinks_max - food_drinks_min), null ) as food_drinks_mx,
COALESCE ( ( stores - stores_min) / ( stores_max - stores_min), null ) as stores_mx,
COALESCE ( ( services - services_min) / ( services_max - services_min), null ) as services_mx
       FROM grid_access, stats) h);  