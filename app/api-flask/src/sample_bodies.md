#### Export Scenarios
'/api/export_scenario'





#### Layer Controller

Read
```json
{
    "table_name": "pois",
    "mode": "read",
    "scenario_id": 10
}
```
Insert
```json
{
    "table_name": "pois",
    "mode": "insert",
    "features": [

        {
            "name": "Test1",
            "amenity": "tram_stop",
            "geom": "POINT(11.4043 48.1232)",
            "scenario_id": 10
        },
        {
            "name": "Test2",
            "amenity": "bus_stop",
            "geom": "POINT(11.4743 48.1332)",
            "scenario_id": 10
        }                
    ]

}

```

Update
```json
{
    "table_name": "pois_modified",
    "mode": "update",
    "features": [

        {
            "name": "Test1",
            "amenity": "tram_stop",
            "geom": "POINT(11.4943 48.1232)",
            "scenario_id": 10,
            "gid": 81781
        },
        {
            "name": "Test2",
            "amenity": "bus_stop",
            "geom": "POINT(11.4143 48.1332)",
            "scenario_id": 10,
            "gid": 81782
        }                
    ]

}
```

Delete
```json
{
    "table_name": "pois",
    "mode": "delete",
    "features": [

        {
            "scenario_id": 10,
            "gid": 81781
        },
        {
            "scenario_id": 10,
            "gid": 81782
        }                
    ]

}
```
#### layer_read
```json


{
    "table_name": "pois",
    "scenario_id": 0,
    "amenities": ["kindergarten","nursery","primary_school","secondary_school"],
    "table_name": "pois",
    "geom": "POLYGON ((11.5022 48.1232, 11.502007852804033 48.121249096779835, 11.501438795325113 48.11937316567634, 11.500514696123027 48.1176442976698, 11.499271067811867 48.11612893218813, 11.497755702330197 48.114885303876974, 11.49602683432365 48.11396120467489, 11.494150903220161 48.11339214719597, 11.4922 48.1132, 11.49024909677984 48.11339214719597, 11.48837316567635 48.11396120467489, 11.486644297669804 48.114885303876974, 11.485128932188134 48.11612893218813, 11.483885303876974 48.1176442976698, 11.482961204674888 48.11937316567634, 11.482392147195968 48.121249096779835, 11.4822 48.1232, 11.482392147195968 48.12515090322016, 11.482961204674888 48.12702683432365, 11.483885303876974 48.128755702330196, 11.485128932188134 48.13027106781186, 11.486644297669804 48.13151469612302, 11.48837316567635 48.13243879532511, 11.49024909677984 48.13300785280403, 11.4922 48.133199999999995, 11.494150903220161 48.13300785280403, 11.49602683432365 48.13243879532511, 11.497755702330197 48.13151469612302, 11.499271067811867 48.13027106781186, 11.500514696123027 48.128755702330196, 11.501438795325113 48.12702683432365, 11.502007852804033 48.12515090322016, 11.5022 48.1232))",
    "routing_profile": "walking_standard",
    "modus": "default",
    "return_type": "geobuf"
}
{
    "table_name": "pois",
    "scenario_id": 0,
    "amenities": ["kindergarten","nursery","primary_school","secondary_school"],
    "routing_profile": "walking_standard",
    "modus": "default",
    "return_type": "geobuf"
}

{
    "table_name": "edges",
    "objectid": 629281940,
    "modus_input": "default", 
    "return_type": "geobuf"

}

```

#### pois_multi_isochrones
```json
{
    "user_id": 0,
    "scenario_id": 0,
    "minutes": 10, 
    "speed": 5,
    "n": 2,
    "routing_profile": "walking_standard",
    "alphashape_parameter":"0.00003", 
    "modus": "default",
    "region_type": "study_area",
    "region": ["16.3","16.4"],
    "amenities": ["bar"]

}
```

#### Heatmap
http://localhost:5000/v2/map/heatmap/heatmap_population
```json
{

    "scenario_id_input": "1",
    "modus_input": "default",
    "return_type": "geojson"
}
```
http://localhost:5000/api/map/heatmap
```json
{
    "heatmap_type": "heatmap_gravity",
    "scenario_id_input": 0,
    "modus_input": "default", 
    "pois": {"nursery":{"sensitivity":250000,"weight":1}},
    "return_type": "geojson"
}
```