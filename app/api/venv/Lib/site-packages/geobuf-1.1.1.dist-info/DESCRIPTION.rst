Geobuf
------

Geobuf is a compact binary geospatial format for *lossless* compression
of GeoJSON and TopoJSON data.

|Build Status| |Coverage Status|

**Note well**: this project is no longer actively developed. Issues and
pull requests will be attended to when possible, but delays should be
expected.

Advantages over using GeoJSON and TopoJSON directly (in this `revised
version <https://github.com/mapbox/geobuf/issues/27>`__):

-  **Very compact**: typically makes GeoJSON 6-8 times smaller and
   TopoJSON 2-3 times smaller.
-  Smaller even when comparing gzipped sizes: 2-2.5x compression for
   GeoJSON and 20-30% for TopoJSON.
-  Easy **incremental parsing** — you can get features out as you read
   them, without the need to build in-memory representation of the whole
   data.
-  **Partial reads** — you can read only the parts you actually need,
   skipping the rest.
-  Trivial **concatenation**: you can concatenate many Geobuf files
   together and they will form a valid combined Geobuf file.
-  Potentially **faster encoding/decoding** compared to native JSON
   implementations (i.e. in Web browsers).
-  Can still accommodate any GeoJSON and TopoJSON data, including
   extensions with arbitrary properties.

Think of this as an attempt to design a simple, modern Shapefile
successor that works seamlessly with GeoJSON and TopoJSON.

Unlike `Mapbox Vector
Tiles <https://github.com/mapbox/vector-tile-spec/>`__, it aims for
*lossless* compression of datasets — without tiling, projecting
coordinates, flattening geometries or stripping properties.

pygeobuf
^^^^^^^^

This repository is the first encoding/decoding implementation of this
new major version of `Geobuf <https://github.com/mapbox/geobuf>`__ (in
Python). It serves as a prototyping playground, with faster
implementations in JS and C++ coming in future.

Sample compression sizes
^^^^^^^^^^^^^^^^^^^^^^^^

::

                    | normal    | gzipped

+---------------------+-------------+------------+
| us-zips.json        | 101.85 MB   | 26.67 MB   |
+---------------------+-------------+------------+
| us-zips.pbf         | 12.24 MB    | 10.48 MB   |
+---------------------+-------------+------------+
| us-zips.topo.json   | 15.02 MB    | 3.19 MB    |
+---------------------+-------------+------------+
| us-zips.topo.pbf    | 4.85 MB     | 2.72 MB    |
+---------------------+-------------+------------+
| idaho.json          | 10.92 MB    | 2.57 MB    |
+---------------------+-------------+------------+
| idaho.pbf           | 1.37 MB     | 1.17 MB    |
+---------------------+-------------+------------+
| idaho.topo.json     | 1.9 MB      | 612 KB     |
+---------------------+-------------+------------+
| idaho.topo.pbf      | 567 KB      | 479 KB     |
+---------------------+-------------+------------+

Usage
~~~~~

Command line:

.. code:: bash

    geobuf encode < example.json > example.pbf
    geobuf decode < example.pbf > example.pbf.json

As a module:

.. code:: python

    import geobuf

    pbf = geobuf.encode(my_json) # GeoJSON or TopoJSON -> Geobuf string
    my_json = geobuf.decode(pbf) # Geobuf string -> GeoJSON or TopoJSON

The ``encode`` function accepts a dict-like object, for example the
result of ``json.loads(json_str)``.

Both ``encode.py`` and ``geobuf.encode`` accept two optional arguments:

-  **precision** — max number of digits after the decimal point in
   coordinates, ``6`` by default.
-  **dimensions** — number of dimensions in coordinates, ``2`` by
   default.

Tests
~~~~~

.. code:: bash

    py.test -v

The tests run through all ``.json`` files in the ``fixtures`` directory,
comparing each original GeoJSON with an encoded/decoded one.

.. |Build Status| image:: https://travis-ci.org/mapbox/pygeobuf.svg?branch=master
   :target: https://travis-ci.org/mapbox/pygeobuf
.. |Coverage Status| image:: https://coveralls.io/repos/mapbox/pygeobuf/badge.svg?branch=master
   :target: https://coveralls.io/r/mapbox/pygeobuf?branch=master


