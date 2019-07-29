.. doctest-skip-all

**********
servicemon
**********

**servicemon** is a command line tool for measuring the timing of Virtual Observatory (VO) queries.

Code and issue tracker are on `GitHub <https://github.com/NASA-NAVO/servicemon>`_.


Installation
=============

The latest version of **servicemon** can be pip installed.  If an
environment already has an older version of **servicemon** installed
add ``--upgrade`` to make sure the latest version is installed.

.. code-block:: bash

    $ pip install servicemon

Command Structure
=================

**servicemon** is invoked on the command line with a subcommand of
either ``conegen``, ``replay`` or ``query``.

.. code-block:: bash

    $ servicemon --help

    usage: servicemon [-h] [-b] [-t {sync,async}] [-n] [-v]
                      conegen|replay|query ...

    Measure service performance.

    positional arguments:
      conegen|replay|query
        conegen             Generate random cones
        replay              Replay queries from a previous result file.
        query               Query a list of services

    optional arguments:
      -h, --help            show this help message and exit
      -b, --batch           Catch SIGHUP, SIGQUIT and SIGTERM to allow running in
                            the background
      -t {sync,async}, --tap-mode {sync,async}
                            How to run TAP queries
      -n, --norun           Display summary of command arguments withoutperforming
                            any actions
      -v, --verbose         Print additional information to stdout

Query a List of Services
========================

Use the ``query`` subcommand to time queries on
a list of Simple Cone or TAP Services defined in a service file.
The service file contains a Python list of VO services, where each
service is a dictionary defining the service details.  See `Structure of Service Files`_
for more detail.

Each service is queried once for each cone in a list of of cone regions.
A cone region consist of an RA, Dec and Radius.  The cone regions can be
randomly generated (see `Query services over random cones`_), or come from
a file (`Query services over cones from file`_).

The VOTables resulting from each query are stored in individual files under the
``results`` subdirectory relative to where ``servicemon`` was run.  The full path to the
result files depends on the service base name, type and query parameters.

.. code-block:: bash

    $ servicemon query --help
    usage: servicemon query [-h] [--num-cones NUM_CONES | --cone-file CONE_FILE]
                            [--min-radius MIN_RADIUS] [--max-radius MAX_RADIUS]
                            [--start-index START_INDEX]
                            services output

    Query a list of services

    positional arguments:
      services              File containing list of services to query
      output                Name of the output file to contain the cones. May
                            contain Python datetime format elements which will be
                            substituted with appropriate elements of the current
                            time (e.g., query-timing-'%m-%d-%H:%M:%S'.csv)

    optional arguments:
      -h, --help            show this help message and exit
      --num-cones NUM_CONES
                            Number of cones to generate
      --cone-file CONE_FILE

    --min-radius MIN_RADIUS
                          Minimum radius (deg). Default=0
    --max-radius MAX_RADIUS
                          Maximum radius (deg). Default=0.25

      --start-index START_INDEX

Query services over random cones
--------------------------------

Use the ``--num-cones``, ``min-radius`` and ``--max-radius`` to specify how many cones
and the bounds of the radii (in degrees).  Each cone will consist of an ra, dec and radius, where
the radius falls between min-radius and max-radius (inclusive).

The example below times queries to each service in ``service_list.py`` for each of
25 random cones on the sky with a random RA and Dec, and a random radius from 0.5 to 2.5 degrees.
The output file specification accepts Python datetime formats, so
if the command was executed at 10:45:05 AM on July 12th, the timing results file would be
called ``query_timing-07-12-10:45:05.csv``.

.. code-block:: bash

    $ servicemon query service_list.py query_timing-'%m-%d-%H:%M:%S'.csv \
        --num-cones 25 \
        --min-radius 0.5 \
        --max-radius 2.5

    # Using --batch when running in the background prevents the job
    # from exiting upon logout.
    $ servicemon --batch query service_list.py query_timing-'%m-%d-%H:%M:%S'.csv \
        --num-cones 25 \
        --min-radius 0.5 \
        --max-radius 2.5 >> outputs.txt 2>&1 &

Query services over cones from file
-----------------------------------

Use the ``--cone-file``, to specify the file containing the list of cones to query.

A cone file contains a Python list of dictionaries, with each dictionary containing an
``ra``, ``dec``, and ``radius``.

Specify ``--start-index n`` (n > 0) to skip the first n cones in the cone file.

The example below times queries to each service in ``service_list.py`` for each of
the cones defined in ``cone_list.py``.
If the command was executed at 10:45:05 AM on July 12th, the timing results file would be
called ``query_timing-07-12-10:45:05.csv``.

.. code-block:: bash

    $ servicemon query service_list.py query-timing-'%m-%d-%H:%M:%S'.csv \
        --cone-file cone_list.py

    # ``start-index`` is used here to skip the first 15 cones in ``cone_list.py``.
    $ servicemon query service_list.py query-timing-'%m-%d-%H:%M:%S'.csv \
        --cone-file cone_list.py \
        --start-index 15

Replay previous queries
=======================

Use the ``replay`` subcommand to replay the queries from an existing output timing file.

.. code-block:: bash

    $ servicemon replay --help
    usage: servicemon replay [-h] file output

    Replay queries from a previous result file.

    positional arguments:
      file        The file to replay.
      output      Name of the output file to contain the cones. May contain Python
                  datetime format elements which will be substituted with
                  appropriate elements of the current time (e.g., replay-
                  timing-'%m-%d-%H:%M:%S'.csv)

The example below repeats all the queries that were timed in a previous ``servicemon query``,
and outputs the timing results to ``replay_timing-2019-07-12-16:56.785`` (assuming that time stamp
is when the command was run).

.. code-block:: bash

    $ servicemon replay query_timing-07-12-10:45:05.csv replay_timing-'%Y-%m-%d-%H:%M:%S.%f'.csv

Generate list of cones
======================

The ``conegen`` command doesn't perform any queries, but does generate a file containing a
random list of cones that can be used by a subsequent ``servicemon query``.

.. code-block:: bash

    $ servicemon conegen --help
    usage: servicemon conegen [-h] [--num-cones NUM_CONES]
                              [--min-radius MIN_RADIUS] [--max-radius MAX_RADIUS]
                              output

    Generate random cones

    positional arguments:
      output                Name of the output file to contain the cones. May
                            contain Python datetime format elements which will be
                            substituted with appropriate elements of the current
                            time (e.g., conefile-'%m-%d-%H:%M:%S'.py)

    optional arguments:
      -h, --help            show this help message and exit

      --num-cones NUM_CONES
                            Number of cones to generate
      --min-radius MIN_RADIUS
                            Minimum radius (deg). Default=0
      --max-radius MAX_RADIUS
                            Maximum radius (deg). Default=0.25

The example below generates the file ``new_cones.py`` which contains 3 cone
definitions, each with a random RA and Dec, and a random radius from 0 to 1 degree.

.. code-block:: bash

    $ servicemon conegen new_cones.py --num-cones 3 --min-radius 0.0 --max-radius 1.0

generates this file which can be used as the ``--cone-file`` in a
``servicemon query`` command.

**conefile.py**

.. code-block:: python

    [
        {'dec': -28.6372961471081, 'ra': 197.27375725149247, 'radius': 0.6496046448539057},
        {'dec': -3.721565362583686, 'ra': 46.451147367862944, 'radius': 0.16151283368330616},
        {'dec': -85.790701482934, 'ra': 7.434138258894394, 'radius': 0.549397311022974}
    ]


Structure of Service Files
==========================

A service file contains a Python list of dictionaries.  Each dictionary
defines a service endpoint, and must contain the keys defined below.  All
services are assumed to return results as VOTables.

* **base_name** - This name of the service will be used in constructing the unique
  ids for each result row as well as the file names for the VOTable result files
  stored in the ``results`` subdirectory.
* **service_type** - One of ``cone``, ``xcone`` or ``tap``

  * ``cone`` The query will be constructed as a VO standard Simple Cone Search
    with the RA, DEC and SR parameters being automatically set based per cone.
  * ``xcone`` A non-standard cone search.  The **access_url** is assumed to contain
    three {}s (open/close braces).  The RA, Dec and Radius for each cone will be
    substituted for those 3 braces in order.

* **access_url** - The access URL for the service.
* **adql** - For the ``tap`` *service_type*, this is the ADQL query. For other types,
  this key must exist, but the value will be ignored. The ADQL query is assumed
  to contain three {}s (open/close braces).  The ra, dec and radius for each cone
  will be substituted for those 3 braces in order.

Example service file:

.. code-block:: python

    [
        {'base_name': '2MASS_STScI',
         'service_type': 'cone',
         'adql': '',
         'access_url': 'http://gsss.stsci.edu/webservices/vo/ConeSearch.aspx?CAT=2MASS',
         },

        {'base_name': 'PanSTARRS',
         'service_type': 'xcone',
         'adql': '',
         'access_url': 'https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/'
         'mean.votable?flatten_response=false&raw=false&sort_by=distance'
         '&ra={}&dec={}&radius={}'
         },

        {'base_name': 'PanSTARRS',
         'service_type': 'tap',
         'access_url': 'http://vao.stsci.edu/PS1DR2/tapservice.aspx',
         'adql':'''
       SELECT objID, RAMean, DecMean, nDetections, ng, nr, ni, nz, ny, gMeanPSFMag,
       rMeanPSFMag, iMeanPSFMag, zMeanPSFMag, yMeanPSFMag
       FROM dbo.MeanObjectView
       WHERE
       CONTAINS(POINT('ICRS', RAMean, DecMean),CIRCLE('ICRS',{},{},{}))=1
         '''
         }
    ]


