# Workflow recipes

GOAT's common analysis chains, with real tool ids, inputs and settings. Read the
settings with workflow_describe_tool before you use them; the layer numbers (12,
13, 14, 15) stand for layer_project_ids from project_get_layers, and the field
names stand for fields read with project_get_fields.

## Who lives within N minutes of places

Catchment areas around the places, then the residents inside them.

```json
{
  "name": "Residents within 15 minutes of the supermarkets",
  "steps": [
    {"id": "shops", "kind": "dataset", "label": "Supermarkets", "layer": 12},
    {"id": "people", "kind": "dataset", "label": "Residents", "layer": 13},
    {"id": "walk", "kind": "tool", "tool": "catchment_area_v2", "label": "15 minutes on foot",
     "settings": {"routing_mode": "walking", "cost_type": "time", "max_cost": 15, "steps": 1}},
    {"id": "count", "kind": "tool", "tool": "aggregate_polygon", "label": "Residents in reach",
     "settings": {"area_type": "polygon", "weighted_by_intersecting_area": true,
                  "column_statistics": [{"operation": "sum", "field": "einwohner"}]}},
    {"id": "save", "kind": "export", "name": "Residents within 15 minutes"}
  ],
  "connections": [
    {"from": "shops", "to": "walk", "input": "starting_points"},
    {"from": "walk", "to": "count", "input": "area_layer_id"},
    {"from": "people", "to": "count", "input": "source_layer_id"},
    {"from": "count", "to": "save"}
  ]
}
```

- Residents as polygons (a census grid, blocks): aggregate_polygon, as above;
  `weighted_by_intersecting_area` counts a polygon cut by the catchment by the
  share inside it.
- Residents as points (addresses, census points): aggregate_points with
  `area_type` `polygon`, `source_layer_id` the points and `area_layer_id` the
  catchments, and `column_statistics` `[{"operation": "sum", "field": "<field>"}]`,
  or `[{"operation": "count"}]` to count the points.
- Residents left open (no layer fits): the `people` step gets `layer` null and its
  label, and the statistic keeps its operation without a field,
  `[{"operation": "sum"}]`, for the user to complete after choosing the layer.
- Another mode: `routing_mode` `bicycle`, `pedelec`, `car` or `pt` (public
  transport; then `max_cost` is minutes, `pt_day` sets the day, and
  `pt_start_time` and `pt_end_time`, in seconds after midnight, set when people
  travel).
- A distance instead of a time: `cost_type` `distance` and `max_cost` in meters.
- Bands, such as 5, 10 and 15 minutes: `steps` 3 with `max_cost` 15.

## Access everywhere: a heatmap

heatmap_closest_average gives each grid cell the average travel time to its
nearest destinations; heatmap_gravity weighs destinations by how far and how large
they are. A 15-minute city check is a heatmap_closest_average with one opportunity
per kind of destination (up to three), each with `max_cost` 15.

```json
{
  "name": "Everyday needs within 15 minutes on foot",
  "steps": [
    {"id": "shops", "kind": "dataset", "label": "Supermarkets", "layer": 12},
    {"id": "schools", "kind": "dataset", "label": "Schools", "layer": 14},
    {"id": "heat", "kind": "tool", "tool": "heatmap_closest_average", "label": "Walking time to everyday needs",
     "settings": {"routing_mode": "walking",
                  "opportunity_1_max_cost": 15, "opportunity_1_n_destinations": 1,
                  "opportunity_2_max_cost": 15, "opportunity_2_n_destinations": 1}},
    {"id": "save", "kind": "export", "name": "Walking time to everyday needs"}
  ],
  "connections": [
    {"from": "shops", "to": "heat", "input": "opportunity_layer_1_id"},
    {"from": "schools", "to": "heat", "input": "opportunity_layer_2_id"},
    {"from": "heat", "to": "save"}
  ]
}
```

- heatmap_gravity takes per opportunity `max_cost`, `sensitivity` and
  `potential_type` (`constant`, `field` or `expression`, with
  `potential_constant`, `potential_field`, a field of that opportunity's layer, or
  `potential_expression`), and `decay` for the whole heatmap.

## Join attributes

join keeps the features of `target_layer_id` and adds fields of `join_layer_id`,
by location or by a shared field.

```json
{
  "name": "Schools with their district",
  "steps": [
    {"id": "schools", "kind": "dataset", "label": "Schools", "layer": 12},
    {"id": "districts", "kind": "dataset", "label": "Districts", "layer": 15},
    {"id": "join", "kind": "tool", "tool": "join", "label": "District of each school",
     "settings": {"use_spatial_relationship": true, "use_attribute_relationship": false,
                  "spatial_relationship": "intersects", "join_type": "inner",
                  "join_operation": "one_to_one", "add_join_fields": true, "join_fields": ["name"]}},
    {"id": "save", "kind": "export", "name": "Schools with district"}
  ],
  "connections": [
    {"from": "schools", "to": "join", "input": "target_layer_id"},
    {"from": "districts", "to": "join", "input": "join_layer_id"},
    {"from": "join", "to": "save"}
  ]
}
```

- By a shared field: `use_attribute_relationship` true and
  `attribute_relationships` `[{"target_field": "<field>", "join_field": "<field>"}]`.
- `join_fields` are fields of the join layer (project_get_fields).

## Counting within a distance

Buffers around places, then what lies inside them.

```json
{
  "name": "Bus stops within 500 m of the schools",
  "steps": [
    {"id": "schools", "kind": "dataset", "label": "Schools", "layer": 12},
    {"id": "stops", "kind": "dataset", "label": "Bus stops", "layer": 13},
    {"id": "ring", "kind": "tool", "tool": "buffer", "label": "500 m around the schools",
     "settings": {"distance_type": "constant", "distances": [500], "units": "meters"}},
    {"id": "count", "kind": "tool", "tool": "aggregate_points", "label": "Stops per school",
     "settings": {"area_type": "polygon", "column_statistics": [{"operation": "count"}]}},
    {"id": "save", "kind": "export", "name": "Bus stops within 500 m"}
  ],
  "connections": [
    {"from": "schools", "to": "ring", "input": "input_layer_id"},
    {"from": "ring", "to": "count", "input": "area_layer_id"},
    {"from": "stops", "to": "count", "input": "source_layer_id"},
    {"from": "count", "to": "save"}
  ]
}
```

- Polygons inside the buffers (green spaces, buildings): aggregate_polygon with
  `source_layer_id` the polygons.
- A walking distance instead of a straight line: catchment_area_v2 with
  `cost_type` `distance` and `max_cost` in meters, in place of buffer.
