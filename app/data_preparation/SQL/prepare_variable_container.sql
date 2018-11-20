CREATE TABLE public.variable_container (
	identifier varchar(100) NOT NULL,
	variable_simple text NULL,
	variable_array text[] NULL,
	variable_object json NULL,
	CONSTRAINT variable_container_pkey PRIMARY KEY (identifier)
);

insert INTO variable_container(identifier,variable_array) 
values('poi_categories',
'{"kindergarten","primary_school","secondary_school","bar","biergarten","cafe","pub","fast_food",
"ice_cream","restaurant","sum_addresses","sum_population","cinema","library","night_club","recycling",
"car_sharing","charging_station","bus_station","tram_station","subway_station","railway_station","taxi",
"optician","hairdresser","tailer","atm","bank","dentist","doctors","pharmacy","post_box","post_office","fuel",
"alcohol","bakery","butcher","clothes","convenience","fashion","florist","greengrocer","grocery",
"kiosk","mall","organic","second_hand","shoes","sports","supermarket","toys","marketplace",
"picnic_site","hotel","museum","hostel","guest_house","attraction","attraction","viewpoint","gallery","bus_stop",
"tram_stop","subway_entrance","sbahn_regional"}');


insert INTO variable_container(identifier,variable_array) 
values('excluded_class_id_walking',
'{101,102,103,104,105,106,107,501,502,503,504}');

insert INTO variable_container(identifier,variable_array)
values('landuse_with_no_residents',
'{"AX_TagebauGrubeSteinbruch",
"AX_SportFreizeitUndErholungsflaeche",
"AX_FlaecheBesondererFunktionalerPraegung",
"AX_Halde",
"AX_Friedhof",
"AX_IndustrieUndGewerbeflaeche"}'
);
