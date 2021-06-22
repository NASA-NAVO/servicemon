.. doctest-skip-all

##########
servicemon
##########

**servicemon** is a command line tool for measuring the timing of Virtual Observatory (VO) queries.
The features are also available via the :doc:`servicemon-api`.

Code and issue tracker are on `GitHub <https://github.com/NASA-NAVO/servicemon>`_.

************
Installation
************

The latest version of **servicemon** requires Python 3.8 or higher and
can be pip installed.  If an environment already has an older version of
**servicemon** installed add ``--upgrade`` to make sure the latest version
is installed.

Be sure to use the ``--pre`` option since the latest version is a pre-release.

.. code-block:: bash

    $ pip install --pre servicemon

********
Overview
********

The basic intent of **servicemon** is to execute multiple queries on one or
more VO services and record the timing of each query.  The
specific query parameters (such as ra, dec and radius) are varied with each
query.  Those query parameters can be listed in an input file, or randomly
generated according to run-time arguments.

The following commands are available for performing timed queries and generating
random input parameters:

`sm_query`_
  Executes and times queries over a specified list of template services whose
  parameters are filled by a specified list of input parameters.

`sm_run_all`_
  Runs multiple `sm_query`_ commands in parallel based on the `Service Files`_ found in
  specified directory structure.

`sm_replay`_
  Replays the queries in a given ``csv`` result file from `sm_query`_, recording the
  timings into a new result file.

`sm_conegen`_
  Creates an input parameter file containing the specified number of the random cone search parameters
  ``ra``, ``dec`` and ``radius``.

The services to query are specified in `Service Files`_, typically formatted as a Python
list of dictionaries
that specify a template query to be filled with the input parameters along with the
query endpoint and other metadata.

The input parameters are specified as a list of dictionaries, each of which has a value for
``ra``, ``dec`` and ``radius``.  (A future generalization will support parameter names other than these
cone search parameters.)

**************
Basic Examples
**************

Timing a Simple Cone Search (SCS) service
=========================================
In this example, we will execute and time 3 different queries to a
`Simple Cone Search (SCS) <http://www.ivoa.net/documents/latest/ConeSearch.html>` service
hosted at the Cool Archive.

1. Create a cone search parameter input file for 3 random cones with radii from 0.1 to 0.2 degrees.
(If desired, this step can be skipped by supplying the `--num_cones`, `--min_radius` and `--max_radius` to
the `sm_query`_ command in step 3.  In that case the random cones will be generated internally and not stored
in a separate file.)

.. code-block:: bash

  $ sm_conegen three_cones.py --num_cones 3 --min_radius 0.1 --max_radius 0.2
  $ cat three_cones.py

  [
      {'dec': 27.663409836268887, 'ra': 101.18375952324169, 'radius': 0.11092016620136524},
      {'dec': 4.840997553935431, 'ra': 358.97280995896705, 'radius': 0.19181724441608894},
      {'dec': 3.284106996695529, 'ra': 312.34607454539434, 'radius': 0.13515755153293374}
  ]

2. Create a service file that defines the Simple Cone Search service to query.  For SCS services,
use `service_type` of `cone`.  This causes the ``ra``, ``dec`` and ``radius`` values from the input file
to be appended to the ``access_url`` at query time according to the SCS standard.

.. literalinclude:: files/cool_archive_cone_service.py
  :caption: cool_archive_cone_service.py

3. Run `sm_query`_.  By default, all `The Output`_ will appear in the ``results`` directory.

.. code-block:: bash

  $ sm_query cool_archive_cone_service.py --cone_file three_cones.py

Timing a Table Access Protocol (TAP) service
============================================

This example queries a
`Table Access Protocol (TAP) <http://www.ivoa.net/documents/TAP/20190927/>`
service hosted by the Great Archive 3 times with the same cones defined in the previous example.

1. Create a service file that describes the TAP service to be queried.  Note that the
``service_type`` is ``tap``.  The ``adql`` value is a template containing 3 `{}`s into
which the input ``ra``, ``dec`` and  ``radius`` values will be substituted.

.. literalinclude:: files/great_archive_tap_service.py
  :caption: great_archive_tap_service.py

2. Run `sm_query`_.  By default, all `The Output`_ will appear in the ``results`` directory.

.. code-block:: bash

  $ sm_query great_archive_tap_service.py --cone_file three_cones.py


Query multiple services in parallel
===================================

It can be efficient to query multiple service providers in parallel, however, we may not
want to execute multiple parallel queries on the same service provider. `sm_run_all`_
provides an automated way to handle that situation.

For each subdirectory of the specified input directory, `sm_run_all`_ invokes
`sm_query`_ once at a time for each service definition file found in that subdirectory.
The subdirectories themselves (each perhaps representing a single service provider)
are handled in parallel.

This example uses `sm_run_all`_ to query the two services above in parallel.

1.  Using the files from the previous examples, create an input directory structure to
give to `sm_run_all`_.

.. code-block:: bash

  $ mkdir -p input/cool_archive input/great_archive   # Create a subdirectory for each archive
  $ mv cool_archive_cone_service.py input/cool_archive/
  $ mv great_archive_tap_service.py input/great_archive/
  $ mv three_cones.py input
  $ ls -RF input

  cool_archive/	great_archive/	three_cones.py

  input/cool_archive:
  cool_archive_cone_service.py

  input/great_archive:
  great_archive_tap_service.py

2. For all the cones in `input/three_cones.py`, run all the services in `input/cool_archive`
in parallel with those in `input/great_archive`.
In addition to specifying the input directory created above, `sm_run_all`_ requires that
the result directory is explicitly specified.

.. code-block:: bash

  $ sm_run_all input --cone_file input/three_cones.py --result_dir results

***************
Command Options
***************

sm_query
========

Documentation for this command:

.. program-output:: sm_query --help

sm_run_all
==========

.. program-output:: sm_run_all --help

sm_replay
=========

.. program-output:: sm_replay --help

sm_conegen
==========

.. program-output:: sm_conegen --help

*************
Service Files
*************

A service file contains a Python list of dictionaries.  Each dictionary
defines a service endpoint, and must contain the keys defined below.  All
services are assumed to return results as VOTables.

* **base_name** - This name of the service will be used in constructing the unique
  ids for each result row as well as the file names for the VOTable result files
  stored in the ``results`` subdirectory.
* **service_type** - One of ``cone``, ``xcone`` or ``tap``

  * ``cone`` The query will be constructed as a VO standard Simple Cone Search
    with the RA, DEC and SR parameters being automatically set based per cone.

  .. literalinclude:: files/cool_archive_cone_service.py

  * ``xcone`` A non-standard cone search.  The **access_url** is assumed to contain
    three {}s (open/close braces).  The RA, Dec and Radius for each cone will be
    substituted for those 3 braces in order.

  .. literalinclude:: files/sia_service.py
    :caption: service_type 'xcone' can be used for an SIA service

  * ``tap`` A Table Access Protocol (TAP) service.  The **adql** value is a template
    template for the TAP query to be performed.

  .. literalinclude:: files/great_archive_tap_service.py
    :caption: Sample TAP service.

* **access_url** - The access URL for the service.
* **adql** - For the ``tap`` *service_type*, this is the ADQL query. For other types,
  this key must exist, but the value will be ignored. The ADQL query is assumed
  to contain three {}s (open/close braces).  The ra, dec and radius for each cone
  will be substituted for those 3 braces in order.

.. literalinclude:: files/multiple_services.py
  :caption: **Multiple services** are allowed, but it is recommended that all service_type values are the same.

**********
The Output
**********

`sm_query`_ and `sm_run_all`_ write multiple output files, all to the result directory
specified using the ``--result_dir`` command argument.  `sm_run_all`_ requires that the
result directory is explicitly specified while `sm_query`_ will use a default of ``results``.

`CSV files`
  By default, the output statistics for the queries are written to CSV files, one CSV file
  per service file.  The CSV file names are ``<service_file_base_name>_<date_string>.csv``.

  These files are written by the default output writer plugin, ``csv_writer``.  See `Plugins`_
  for information on how to specify alternative or additional writers, or how to customize the
  CSV file name.


`VOTable subdirectories and files`
  If ``--save_results`` is specified on the command line, the VOTables returned from each query will
  be stored in subdirectories of the result directory.  Those subdirectories are named for the `base_name`
  specified in the query's service file.  The names of the VOTables are built from attributes of the
  service and the input: ``<base_name>_<service_type>_<ra>_<dec>_<radius>.xml``

  Even when ``--save_results`` is not specified, the VOTables are written to those files temporarily.
  Empty VOTables subdirectories are an artifact of that process when ``--save_results`` is not specified.

`Log files from sm_run_all`
  For each subdirectory handled, `sm_run_all`_ creates a file that logs the commands run in that directory.
  The files are called ``<input_subdir_name>-<date_string>_comlog.txt``.

  In addition, for each service queried (i.e., each `sm_query`_ run), a file is created to collect any stdout
  or stderr generated by `sm_query`_.  Those files are named
  ``<base_name>_<service_type>-<date_string>_runlog.xml``.

*******
Plugins
*******

Using a plugin
==============

A plugin mechanism is provided to allow customization of the output from `sm_query`_ (and `sm_run_all`_).
By default, a plugin called `csv_writer` writes the query statistcs to the CSV files described above.

Alternative or additional plugins can be loaded via the ``--writer`` argument.
To use a new plugin called `my_writer`:

.. code-block:: bash
  :emphasize-lines: 2

  $ sm_query cool_archive_cone_service.py --cone_file three_cones.py \
    --writer my_writer

When multiple writers are specified, each writer will be invoked for each result, and they will be executed
in the order they were specified on the command line.
To use a new plugin called `my_writer` along with the builtin `csv_writer`:

.. code-block:: bash
  :emphasize-lines: 2,3

  $ sm_query cool_archive_cone_service.py --cone_file three_cones.py \
    --writer my_writer \
    --writer csv_writer

Writing a plugin
================

A plugin is a Python class in a file that gets loaded at run time.  The class must be a subclass of
`AbstractResultWriter` and must implement the abstract methods defined there.

.. automethod:: servicemon.plugin_support.AbstractResultWriter.begin

.. automethod:: servicemon.plugin_support.AbstractResultWriter.one_result

.. automethod:: servicemon.plugin_support.AbstractResultWriter.end

Loading a plugin at run time
============================

To load your plugin at run time, the plugin should be in a ``.py`` file.  Then it should either
be placed in the ``plugins`` subdirectory of your working directory, or its location should be
specified on the command line (for `sm_query`_, `sm_replay`_) with the ``--load_plugins`` argument.  The value for ``--load_plugins``
can be either a directory (from which all ``.py`` files will be loaded, or an individual ``.py`` file.)

Example: csv_writer
===================

The builtin plugin ``csv_writer`` is shown below.  Note that its ``begin`` method accepts the keyword
argument ``outfile`` which can be used to override the default output file name.  To specify ``outfile`` on the
command line, include it with the ``--writer`` value:

.. code-block:: bash
  :emphasize-lines: 2

  $ sm_query cool_archive_cone_service.py --cone_file three_cones.py \
    --writer csv_writer:outfile=my_override_filename.csv

.. literalinclude:: ../servicemon/builtin_plugins/csv_writer.py
  :language: python

Developer documentation
-----------------------

The :doc:`analysis-api` is for use in finding and analyzing data already collected.

.. toctree::
   :maxdepth: 1

   analysis-api.rst




