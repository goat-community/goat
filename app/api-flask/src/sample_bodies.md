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
            "scenario_id": 10,
            "gid": 81781
        },
        {
            "name": "Test2",
            "amenity": "bus_stop",
            "geom": "POINT(11.4743 48.1332)",
            "scenario_id": 10,
            "gid": 81782
        }                
    ]

}

```

Update
```json
{
    "table_name": "pois",
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